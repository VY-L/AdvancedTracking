from typing import Optional
import functools
from typing_extensions import Self
from mcdreforged.utils.serializer import Serializable
from pathlib import Path

from advanced_tracking import ScoreboardRegistry, TrackerRegistry


class PermissionConfig(Serializable):
    pass

class Config(Serializable):
    scoreboard_registry: ScoreboardRegistry = ScoreboardRegistry()
    tracker_registry: TrackerRegistry= TrackerRegistry()
    @classmethod
    @functools.lru_cache
    def __get_default(cls) -> Self:
        """
        Returns the default configuration instance.
        This method should be overridden to provide a default configuration.
        """
        return Config.get_default()

    @classmethod
    def get(cls):
        if _config is None:
            return cls.__get_default()
        return _config

    permission_config: PermissionConfig = PermissionConfig()

    @property
    def script_destination(self) -> Path:
        """
        Returns the path to the script directory.
        """
        from mcdreforged.api.all import ServerInterface
        si = ServerInterface.si()
        if si is not None and (mcdr_wd := si.get_mcdr_config().get('working_directory')) is not None:
            return Path(mcdr_wd)
        raise ValueError("Can't find MCDR working directory")


_config: Optional[Config] = None

def set_config_instance(cfg: Config):
    global _config
    _config = cfg