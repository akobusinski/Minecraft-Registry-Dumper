import sys
import asyncio
from mcproto.connection import TCPAsyncConnection
from mcproto.packets import async_write_packet, async_read_packet, generate_packet_map, GameState, PacketDirection
from mcproto.packets.handshaking import Handshake, NextState
from mcproto.packets.status import StatusRequest, StatusResponse
from mcproto.packets.login import LoginSuccess, LoginEncryptionRequest, LoginSetCompression, LoginDisconnect
from mcproto.types.uuid import UUID
from mcproto.types.chat import ChatMessage
from uuid import uuid4

from packets.login import LoginStart, LoginAcknowledged
from packets.configurating import RegistryData, CONFIGURATING_CLIENTBOUND_MAP

STATUS_CLIENTBOUND_MAP = generate_packet_map(PacketDirection.CLIENTBOUND, GameState.STATUS)
LOGIN_CLIENTBOUND_MAP = generate_packet_map(PacketDirection.CLIENTBOUND, GameState.LOGIN)

def chat_to_string(chat: ChatMessage) -> str:
        string = ""
        msg = chat.as_dict()
        if ('text' in msg):
            string += msg['text']
        if ('extra' in msg):
            for i in msg['extra']:
                if (isinstance(i, str)):
                    string += i
                elif (isinstance(i, dict)): # type: ignore -- idc
                    if ('text' in i):
                        string += i['text']
                    else:
                        print(f"Very weird behaviour, i: {i}")
        return string

async def get_protocol_version(address: str, port: int) -> int:
    connection: TCPAsyncConnection[asyncio.StreamReader, asyncio.StreamWriter] = await TCPAsyncConnection.make_client(address=(address, port), timeout=30)
    await async_write_packet(connection, Handshake(
        protocol_version=47,
        server_address=address,
        server_port=port,
        next_state=NextState.STATUS
    ))
    await async_write_packet(connection, StatusRequest())
    
    packet = await async_read_packet(connection, STATUS_CLIENTBOUND_MAP)
    
    if not isinstance(packet, StatusResponse):
        raise TypeError("Invalid status packet received!")
    
    await connection.close()
    return int(packet.data["version"]["protocol"])

async def main(address: str, port: int):
    print("Getting protocol version.. ")
    protocol_version = await get_protocol_version(address, port)
    print(f"Server protocol version: {protocol_version}")
    print("Connecting to server..")
    connection: TCPAsyncConnection[asyncio.StreamReader, asyncio.StreamWriter] = await TCPAsyncConnection.make_client(address=(address, port), timeout=30)
    compression_threshold = -1
    await async_write_packet(connection, Handshake(
        protocol_version=protocol_version,
        server_address=address,
        server_port=port,
        next_state=NextState.LOGIN
    ), compression_threshold=compression_threshold)
    await async_write_packet(connection, LoginStart(
        username="NBTDumper",
        uuid=UUID(bytes=uuid4().bytes)
    ), compression_threshold=compression_threshold)
    
    while True:
        packet = await async_read_packet(connection, LOGIN_CLIENTBOUND_MAP, compression_threshold=compression_threshold)
    
        if isinstance(packet, LoginSuccess):
            break
        elif isinstance(packet, LoginEncryptionRequest):
            print("Server isn't in offline mode!")
            return
        elif isinstance(packet, LoginSetCompression):
            compression_threshold = packet.threshold
        elif isinstance(packet, LoginDisconnect):
            print("Client got disconnected from the server!")
            print(f"Reason: {chat_to_string(packet.reason)}")
            return
        else:
            print(f"Unknown packet received! (id: {hex(packet.PACKET_ID)})")
            return
    
    await async_write_packet(connection, LoginAcknowledged(), compression_threshold=compression_threshold)
    print("Login phase done!")
    
    while True:
        packet = await async_read_packet(connection, CONFIGURATING_CLIENTBOUND_MAP, compression_threshold=compression_threshold)
        
        if isinstance(packet, RegistryData):
            print("Got registry data!")
            await connection.close()
            
            with open("nbt.bin", "wb") as f:
                f.write(packet.nbt)
                
            print("NBT data saved to nbt.bin")
            
            return


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print(f"Usage: {sys.argv[0]} <address> <port>")
        exit(1)
    
    address = sys.argv[1]
    port = int(sys.argv[2])
    print(f"Connecting to {address}:{port}")
    asyncio.run(main(address, port))
