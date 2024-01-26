from mcproto.buffer import Buffer
from mcproto.packets.packet import GameState, ClientBoundPacket
from typing import ClassVar, final, Dict, Any
from typing_extensions import Self

@final
class RegistryData(ClientBoundPacket):
    """Represents certain registries that are sent from the server and are applied on the client. (Server -> Client)"""

    __slots__ = ("nbt", )

    PACKET_ID: ClassVar[int] = 0x05
    GAME_STATE: ClassVar[GameState] = GameState.PLAY # this isn't actually play

    def __init__(self, *, nbt: bytearray):
        """
        :param nbt: The NBT data.
        """
        self.nbt = nbt

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.extend(self.nbt)
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        nbt = buf.read(buf.remaining)
        return cls(nbt=nbt)

class Packet:
    PACKET_ID = 0x00
    
    def __init__(self):
        pass
    
    def serialize(self) -> Buffer:
        return Buffer()

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        return cls()

class PacketDict(dict[Any, Any]): # Dict that doesn't care whether or not something doesn't exist
    def __init__(self, default: Dict[Any, Any]):
        self.default = default
    
    def __getitem__(self, __key: Any) -> Any:
        p = Packet
        p.PACKET_ID = __key
        return self.default.get(__key, p)

CONFIGURATING_CLIENTBOUND_MAP = PacketDict({
    0x05: RegistryData
})
