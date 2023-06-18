import json

from utils.mcclient.response import SLPResponse, LegacySLPResponse
from utils.mcclient.base_client import BaseClient
from utils.mcclient.encoding.packet import Packet
from utils.mcclient.base_client import DEFAULT_PORT, DEFAULT_TIMEOUT, DEFAULT_PROTO


class SLPClient(BaseClient):
    retries: int

    def __init__(self, host: str, port: int = DEFAULT_PORT, timeout: int = DEFAULT_TIMEOUT, proto: int = DEFAULT_PROTO, srv: bool = True):
        super().__init__(host=host, port=port, timeout=timeout, proto=proto, srv=srv)
        self.retries = 0

    def _status_request(self) -> dict:
        packet = Packet(b"\x00")  # send status request
        self._send(packet)
        res = self._recv()

        if res[0]:
            # if packetloss occured
            if self.retries < 3:
                self.retries += 1
                self._reset()
                return self._status_request()

            else:
                raise Exception("Max retries exceeded.")

        self._close(flush=False)

        res_data = res[2][2:]
        res_str = res_data.decode("utf-8")
        res_dict = json.loads(res_str)
        return res_dict

    def get_status(self) -> SLPResponse:
        self._connect()
        self._handshake()
        res = self._status_request()
        self.retries = 0
        return SLPResponse(self.hostname, self.port, res)


class LegacySLPClient(BaseClient):
    def __init__(self, host: str, port: int = 25565, timeout: int = 5):
        super().__init__(host=host, port=port, timeout=timeout)

    def get_status(self) -> LegacySLPResponse:
        self._connect()
        # legacy status request
        self.sock.send(b"\xFE\x01")
        raw_res = self.sock.recv(1024)
        self._close()

        # remove padding and other headers
        res_bytes = raw_res[3:]
        res_str = res_bytes.decode("UTF-16-be", errors="ignore")
        res_split_str = res_str.split("\x00")
        res = LegacySLPResponse(self.hostname, self.port, res_split_str)
        return res
