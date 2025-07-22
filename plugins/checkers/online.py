import ipaddress
import time
from core.interfaces import IPlugin, IChecker
from core.models import ServerStatus, Player


def check_ip_valid(ip):
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except Exception as e:
        return False


def is_lan(ip):
    try:
        return ipaddress.ip_address(ip.strip()).is_private
    except Exception as e:
        return False


class Main(IChecker):
    def __init__(self):
        pass

    def get_id(self) -> str:
        return "online"
    
    def i18n_addins(self):
        return {
            "zh_cn": {
                f"name": "在线",
                f"description": "使用mcstatus.io的在线查询服务API"
            },
            "en_us": {
                f"name": "Online",
                f"description": "Use mcstatus.io's online query API"
            },
            "zh_tw": {
                f"name": "線上",
                f"description": "使用mcstatus.io的線上查詢服務API"
            }
        }

    def get_version(self) -> str | None:
        return "1.0.0"

    def get_author(self) -> str | None:
        return "myworldzycpc"

    def get_website(self) -> str | None:
        return "https://github.com/myworldzycpc/mcstatus-checker"

    def get_license(self) -> str | None:
        return "GPLv3"

    def get_dependencies(self) -> list[str] | None:
        return ["mcstatus", "python-mcstatus"]

    def check_dependencies(self) -> bool:
        try:
            import mcstatus
            import python_mcstatus
            return True
        except ImportError:
            return False

    def get_install_command(self) -> str:
        return "pip install mcstatus python-mcstatus"

    def run(self, address: str) -> ServerStatus | str | None:
        from mcstatus import JavaServer
        from mcstatus.status_response import JavaStatusResponse
        from python_mcstatus import JavaStatusResponse as PythonJavaStatusResponse, statusJava
        try:
            server = JavaServer.lookup(address)
            if not server or is_lan(server.address.host):
                return None
            
            start_time = time.time()
            response: PythonJavaStatusResponse = statusJava(host=server.address.host, port=server.address.port)
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            if not response.online:
                return "Failed to get server status"

            status = ServerStatus(
                address=address,
                port=server.address.port,
                version=response.version.name_clean,
                protocol=response.version.protocol,
                player=response.players.online,
                max_players=response.players.max,
                latency=latency,
                players=[Player(name=p.name_clean) for p in response.players.list] if response.players.list else [],
                motd_plain=response.motd.clean,
                motd_html=f"<p>{response.motd.html}</p>",
                icon=response.icon,
                raw_data=str(response),
                method="online"
            )
            return status
        except Exception as e:
            return e
