import socket
import struct

from utils.mcclient.address import Address
from utils.mcclient.encoding.packet import Packet
from utils.mcclient.encoding.varint import VarInt

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 25565
DEFAULT_TIMEOUT = 5
DEFAULT_PROTO = 47


class BaseClient:
    host: str
    hostname: str
    port: int
    sock: socket.socket
    varint: VarInt
    connected: bool | None
    protocol_version: int

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, timeout: int = DEFAULT_TIMEOUT, proto: int = DEFAULT_PROTO, srv: bool = True):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.varint = VarInt()
        self.connected = False
        self.protocol_version = proto

        self.sock.settimeout(timeout)
        self.get_host(host, port, srv=srv)

    def get_host(self, hostname: str, port: int, srv: bool) -> None:
        addr = Address(hostname)
        self.host, srv_port = addr.get_host(srv)
        self.hostname = hostname
        if srv_port == -1:
            self.port = port

        else:
            self.port = srv_port

    def _connect(self) -> None:
        if self.connected == False:
            self.sock.connect((self.host, self.port))
            self.connected = True

        elif self.connected == None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connected = False
            self._connect()

    def _send(self, packet: Packet):
        return self.sock.send(packet.pack())

    def _recv(self) -> tuple[bool, int, bytes]:
        length = self.varint.unpack(self.sock)
        packet_id = self.varint.unpack(self.sock)
        data = self.sock.recv(length)
        if len(data) < length - 4:
            loss = True

        else:
            loss = False
        return loss, packet_id, data

    def _close(self, flush: bool = True):
        if flush:
            self._flush()
        self.sock.close()
        self.connected = None

    def _reset(self) -> None:
        self._close()
        self._connect()
        self._handshake()

    def _flush(self, chunk_size: int = 8192) -> None:
        try:
            self.sock.recv(chunk_size)

        except Exception:
            return

    def implant_socket(self, sock: socket.socket) -> None:
        self.sock = sock
        self.connected = True

    def _handshake(self, next_state: int = 1) -> None:
        packet = Packet(
            b"\x00",  # packet id
            self.varint.pack(self.protocol_version),
            self.hostname,
            struct.pack(">H", self.port),
            self.varint.pack(next_state)  # next state 1 for status request
        )
        self._send(packet)
