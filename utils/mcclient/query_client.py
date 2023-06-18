import socket
import struct
import random

from utils.mcclient.response import QueryResponse
from utils.mcclient.encoding.packet import QueryPacket
from utils.mcclient.base_client import DEFAULT_PORT, DEFAULT_TIMEOUT


class QueryClient:
    host: str
    port: int
    sock: socket.socket
    session_id: int
    token: bytes

    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: int = DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def _handshake(self) -> None:
        # generate session id from int between 0 and 2147483648
        self.session_id = random.randint(0, 2147483648) & 0x0F0F0F0F
        packet = QueryPacket(
            9,  # type 9 for handshaking
            self.session_id,
            b""  # empty payload
        )
        self._send(packet)
        res = self._recv()
        # extract token from response
        self.token = struct.pack('>l', int(res[2][:-1]))

    def _send(self, packet: QueryPacket) -> None:
        self.sock.sendto(packet.pack(), (self.host, self.port))

    def _recv(self) -> tuple[int, bytes, bytes]:
        res = self.sock.recv(4096)
        type = res[0]
        session_id = res[1:5]
        payload = res[5:]
        return type, session_id, payload

    def _query_request(self) -> dict:
        self._handshake()
        # challenge token and some padding for a full status request
        payload = self.token + b"\x00\x00\x00\x00"
        packet = QueryPacket(
            0,  # packettype 0 for a status request
            self.session_id,
            payload
        )
        self._send(packet)
        raw_res = self._recv()
        return self._read_query(raw_res[2])

    def get_status(self) -> QueryResponse:
        res = self._query_request()
        return QueryResponse(self.host, self.port, res)

    @staticmethod
    def _read_query(res: bytes) -> dict:
        # remove padding
        res = res[11:]

        # split stats from players
        raw_stats, raw_players = res.split(b"\x00\x00\x01player_\x00\x00")

        raw_split_stats = raw_stats.split(b"\x00")
        # decode keys and values
        try:
            stats = [stat.decode("utf-8")
                 for stat in raw_split_stats]
        except UnicodeDecodeError:
            stats = [stat.decode("latin-1")
                 for stat in raw_split_stats]

        # replace "hostname" key with "motd" key
        stats[0] = "motd"
        key_field = True
        data: dict = {}
        for y, x in enumerate(stats):
            if key_field:
                data[x] = stats[y + 1]
                key_field = False

            else:
                key_field = True

        # convert strings to int's
        for key in ["numplayers", "maxplayers", "hostport"]:
            data[key] = int(data[key])

        data["software"] = "Vanilla"
        software_parts = data["plugins"].split(":", 1)
        data["software"] = software_parts[0].strip()
        if len(software_parts) == 2:
            data["plugins"] = [plugin.strip()
                               for plugin in software_parts[1].split(";")]

        else:
            data["plugins"] = []

        # remove endpadding
        raw_players = raw_players[:-2]
        # split players
        players = raw_players.split(b"\x00")
        # split players
        data["players"] = [player.decode(
            "utf-8") for player in players if player != b""]
        return data
