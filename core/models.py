

class Player():
    def __init__(self, name):
        self.name = name

class ServerStatus():
    def __init__(self, address = "", port = -1, player = -1, max_players = -1, version = "unknown", protocol = -1, latency = -1, players: list[Player] = [], motd_plain= "", motd_html = "<p></p>", raw_data = "", method = "unknown", icon=None, name=None):
        self.address = address
        self.port = port
        self.player = player
        self.max_players = max_players
        self.latency = latency
        self.version = version
        self.protocol = protocol
        self.players = players
        self.motd_plain = motd_plain
        self.motd_html = motd_html
        self.raw_data = raw_data
        self.icon = icon
        self.name = name
        self.method = method
        self.checker = None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)