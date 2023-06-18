import socket
import struct

from utils.mcclient.address import Address
from utils.mcclient.response import BedrockResponse
from utils.mcclient.base_client import DEFAULT_TIMEOUT

DEFAULT_BEDROCK_PORT = 19132


class BedrockSLPClient:
    host: str
    port: int
    hostname: str
    sock: socket.socket

    def __init__(self, host: str, port: int = DEFAULT_BEDROCK_PORT, timeout: int = DEFAULT_TIMEOUT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = port
        self.hostname = host
        self.sock.settimeout(timeout)
        self.get_host(host)

    def get_host(self, hostname: str) -> None:
        addr = Address(hostname)
        self.host, _ = addr.get_host(False)

    def get_status(self) -> BedrockResponse:
        raw_res = self._request_status()
        res = self._parse_res(raw_res)
        return BedrockResponse(self.hostname, self.port, res)

    def _request_status(self) -> bytes:
        """
        needs to be updated (https://wiki.vg/Raknet_Protocol#Unconnected_Ping)
        """
        status_request = b"\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx"
        self.sock.sendto(status_request, (self.host, self.port))
        return self.sock.recv(4096)

    @staticmethod
    def _parse_res(raw_bytes: bytes) -> list[str]:
        res_bytes = raw_bytes[1:]
        extra_len = struct.unpack(">H", res_bytes[32:34])[0]
        res_bytes = res_bytes[34: 34 + extra_len]
        res_str = res_bytes.decode()
        res_split = res_str.split(";")
        return res_split
