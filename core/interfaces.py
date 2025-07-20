from abc import ABC, abstractmethod
from core.models import ServerStatus
    
class IPlugin(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_id(self) -> str:
        ...
    
    def get_version(self) -> str | None:
        return None
    
    def get_author(self) -> str | None:
        return None
    
    def get_website(self) -> str | None:
        return None
    
    def get_license(self) -> str | None:
        return None
    
    def get_dependencies(self) -> list[str] | None:
        return None
    
    def i18n_addins(self) -> dict[str, dict[str, str]]:
        return {}
    
    @abstractmethod
    def check_dependencies(self) -> bool:
        ...
    
    def get_install_command(self) -> str | None:
        return f"pip install {" ".join(self.get_dependencies())}" if self.get_dependencies() else None


class IChecker(IPlugin):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, address) -> ServerStatus | str | None:
        ...