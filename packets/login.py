from mcproto.buffer import Buffer
from mcproto.packets.packet import GameState, ServerBoundPacket
from mcproto.types.uuid import UUID
from typing import ClassVar, final
from typing_extensions import Self

@final
class LoginStart(ServerBoundPacket):
    """Packet from client asking to start login process. (Client -> Server)"""

    __slots__ = ("username", "uuid")

    PACKET_ID: ClassVar[int] = 0x00
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self, *, username: str, uuid: UUID):
        """
        :param username: Username of the client who sent the request.
        :param uuid: UUID of the player logging in
        """
        self.username = username
        self.uuid = uuid

    def serialize(self) -> Buffer:
        buf = Buffer()
        buf.write_utf(self.username)
        buf.extend(self.uuid.serialize())
        return buf

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        username = buf.read_utf()
        uuid = UUID.deserialize(buf)
        return cls(username=username, uuid=uuid)

@final
class LoginAcknowledged(ServerBoundPacket):
    __slots__ = tuple() # type: ignore
    
    PACKET_ID: ClassVar[int] = 0x03
    GAME_STATE: ClassVar[GameState] = GameState.LOGIN

    def __init__(self):
        pass

    def serialize(self) -> Buffer:
        return Buffer()

    @classmethod
    def deserialize(cls, buf: Buffer, /) -> Self:
        return cls()
