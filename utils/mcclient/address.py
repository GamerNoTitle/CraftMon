import ipaddress

import dns.resolver

MINECRAFT_SRV_PREFIX = "_minecraft._tcp."

class Address:
    addr: str
    is_ip: bool

    def __init__(self, addr: str):
        self.addr = addr
        self.is_ip = self._ip_check(self.addr)

    def get_host(self, srv: bool = True) -> tuple[str, int]:
        if self.is_ip:
            return self.addr, -1

        else:
            return self._resolve_hostname(self.addr, srv)

    def _resolve_hostname(self, hostname: str, srv: bool) -> tuple[str, int]:
        host = self._resolve_a_record(hostname)
        if srv:
            try:
                srv_record = self._mc_srv_lookup(hostname)
                return host, srv_record[1]

            except Exception:
                pass

        return host, -1  # -1 = no srv port

    @staticmethod
    def _mc_srv_lookup(hostname: str) -> tuple[str, int]:
        srv_record = dns.resolver.resolve(MINECRAFT_SRV_PREFIX + hostname, "SRV")[0]
        host = str(srv_record.target).rstrip(".")
        port = int(srv_record.port)
        return host, port

    @staticmethod
    def _resolve_a_record(hostname: str) -> str:
        record = dns.resolver.resolve(hostname, "A")[0]
        return str(record).rstrip(".")

    @staticmethod
    def _ip_check(addr: str) -> bool:
        try:
            ipaddress.ip_address(addr)
            return True
        except ValueError:
            return False
