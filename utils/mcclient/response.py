import datetime
import re


class Players:
    online: int
    max: int

    def __init__(self, online: int, max: int | None, player_list: list | None):
        self.online = online
        self.max = max
        self.list: list | None = player_list


class Version:
    name: str
    protocol: int | None
    software: str
    brand: str

    def __init__(self, name: str, protocol: int | None):
        self.name = name
        self.protocol = protocol


class StatusResponse:
    host: str
    port: int
    raw_res: str | dict | list
    res: dict
    timestamp: str

    def __init__(self, host: str, port: int, raw_res: str | dict | list):
        self.host = host
        self.port = port
        self.raw_res = raw_res
        self.res = {}

        self.res["host"] = self.host
        self.res["port"] = self.port
        self.timestamp = str(datetime.datetime.now())

    @staticmethod
    def _remove_color_codes(cstr: str, bedrock: bool = False) -> str:
        """
        Returns the input string stripped of all Minecraft color/formatting codes.
        documentation on minecraft color/formatting codes:
        https://minecraft.fandom.com/wiki/Formatting_codes

        Args:
        cstr (str): The string to remove color codes from.
        bedrock (bool): Wether to method should remove bedrock color/formating codes.

        Returns:
        str: The input string stripped of all Minecraft color/formatting codes.
        """

        if bedrock:
            return re.sub(r"§[a-u0-9]", "", cstr)
        return re.sub(r"§[a-fk-or0-9]", "", cstr)


class SLPResponse(StatusResponse):
    motd: str | dict
    favicon: bool
    version: Version
    players: Players

    def __init__(self, host: str, port: int, raw_res: dict):
        super().__init__(host, port, raw_res)

        self.res = self.res | self._parse_slp_res(self.raw_res)
        self.motd = self.res["motd"]
        self.favicon = self.res["favicon"]
        self.version = Version(
            self.res["version"]["name"], self.res["version"]["protocol"])
        self.players = Players(
            self.res["players"]["online"], self.res["players"]["max"], self.res["players"]["list"])

    def _parse_slp_res(self, slp_res) -> dict:
        slp_res = self._add_missing(slp_res)

        if "sample" in slp_res["players"]:
            slp_res["players"]["list"] = slp_res["players"]["sample"]
            slp_res["players"].pop("sample")

        if "description" in slp_res:
            slp_res["motd"] = slp_res["description"]
            slp_res.pop("description")

        else:
            slp_res["motd"] = ""

        for player in slp_res["players"]["list"]:
            player["last_seen"] = self.timestamp

        if "favicon" in slp_res:
            slp_res["favicon"] = True

        else:
            slp_res["favicon"] = False

        slp_res["motd"] = self._parse_motd(slp_res["motd"])
        slp_res["version"]["name"] = self._remove_color_codes(
            cstr=slp_res["version"]["name"])
        slp_res["status"] = "online"
        return slp_res

    @classmethod
    def _parse_motd(cls, raw_motd: str) -> str:
        motd = ""
        if type(raw_motd) == dict:
            entries = raw_motd.get("extra", [])
            end = raw_motd.get("text", "")

            for entry in entries:
                motd += entry.get("text", "")
            motd += end

        elif type(raw_motd) == str:
            motd = raw_motd

        motd = motd.replace("\n", " ").strip()
        motd = cls._remove_color_codes(cstr=motd)
        return motd

    @staticmethod
    def _add_missing(res: dict) -> dict:
        default_res: dict = {
            "previewsChat": None,
            "enforcesSecureChat": None,
            "description": "",
            "version": {"name": "", "protocol": -1},
            "players": {"online": -1, "max": -1, "list": []}
        }

        for key in default_res:
            if key not in res:
                res[key] = default_res[key]

        res["players"]["list"] = default_res["players"]["list"]
        return res


class LegacySLPResponse(StatusResponse):
    motd: str
    version: Version
    players: Players

    def __init__(self, host, port, raw_res):
        super().__init__(host, port, raw_res)

        self.res = self.res | self._parse_res(self.raw_res)
        self.motd = self.res["motd"]
        self.version = Version(self.res["version"], None)
        self.players = Players(self.res["online"], self.res["max"], None)

    @staticmethod
    def _parse_res(raw_res) -> dict:
        res = {}
        res["version"] = raw_res[2]
        res["motd"] = raw_res[3]
        res["online"] = raw_res[4]
        res["max"] = raw_res[5]
        return res


class QueryResponse(StatusResponse):
    motd: str
    gametype: str
    game_id: str
    plugins: list
    map: str
    hostip: str
    hostport: int
    players: Players
    version: Version

    def __init__(self, host: str, port: int, raw_res: dict):
        super().__init__(host, port, raw_res)

        self.res = raw_res | self.res

        self.motd = self.res["motd"]
        self.gametype = self.res["gametype"]
        self.game_id = self.res["game_id"]
        self.plugins = self.res["plugins"]
        self.map = self.res["map"]
        self.hostip = self.res["hostip"]
        self.hostport = self.res["hostport"]

        self.players = Players(
            self.res["numplayers"], self.res["maxplayers"], self.res["players"])
        self.version = Version(self.res["version"], None)
        self.version.software = self.res["software"]


class BedrockResponse(StatusResponse):
    version: Version
    motd: str
    players: Players
    server_id: int
    map: str
    gametype: str

    def __init__(self, host: str, port: int, raw_res: list):
        super().__init__(host, port, raw_res)

        self.res = {}
        self.res["version"] = {}
        self.res["version"]["brand"] = self.raw_res[0]
        self.res["version"]["protocol"] = int(self.raw_res[2])
        self.res["version"]["name"] = self.raw_res[3]
        self.res["motd"] = self._remove_color_codes(
            cstr=self.raw_res[1], bedrock=True)
        self.res["online_players"] = int(self.raw_res[4])
        self.res["max_players"] = int(self.raw_res[5])
        self.res["server_id"] = self.raw_res[6]

        self.res["map"] = None
        self.res["gametype"] = None
        if len(self.raw_res) > 6:
            self.res["map"] = self.raw_res[7]

        if len(self.raw_res) > 7:
            self.res["gametype"] = self.raw_res[8]

        self.version = Version(
            self.res["version"]["name"], self.res["version"]["protocol"])
        self.version.brand = self.res["version"]["brand"]
        self.motd = self.res["motd"]
        self.players = Players(self.res["online_players"], self.res["max_players"], None)
        self.server_id = self.res["server_id"]
        self.map = self.res["map"]
        self.gametype = self.res["gametype"]
