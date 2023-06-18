import struct

from utils.mcclient.encoding.varint import VarInt


class Packet:
    fields: tuple
    varint: VarInt

    def __init__(self, *fields):
        self.fields = fields
        self.varint = VarInt()

    def pack(self) -> bytes:
        packet = b""
        for field in self.fields:
            field = self._encode(field)
            packet += field

        packet = self.varint.pack(len(packet)) + \
            packet  # add the packet length
        return packet

    def _encode(self, data) -> bytes:
        if type(data) == str:
            data = data.encode("utf-8")
            data = self.varint.pack(len(data)) + data

        elif type(data) == bool:
            data = b"\x01" if data else b"\x00"
        return data


class QueryPacket:
    type: int
    session_id: int
    payload: bytes

    def __init__(self, type, session_id, payload):
        self.type = type
        self.session_id = session_id
        self.payload = payload

    def pack(self) -> bytes:
        packet = b"\xFE\xFD"  # query packet padding
        packet += struct.pack("!B", self.type)
        packet += struct.pack('>l', self.session_id)
        packet += self.payload
        return packet
