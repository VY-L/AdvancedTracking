from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.serializer import Serializable
from advanced_tracking.tracker import Tracker, TrackerRegistry
from advanced_tracking.scoreboard import Scoreboard, ScoreboardRegistry

from advanced_tracking.command.commands import CommandManager

# from typing import Dict, List, Optional, Type
# from typing_extensions import Self

import os
import shutil

PLUGIN_PATH = R"plugins\AdvancedTracking"

SERVER_PATH = R'.\server'


class ScriptLoader():
    def __init__(self, server:ServerInterface, script_src, script_dst):
        self.script_src:str = script_src
        self.script_dst:str = script_dst
        self.data_src:str = os.path.join(self.script_src, R"shared\advanced_tracking")
        self.data_dst:str = os.path.join(self.script_dst, R"shared\advanced_tracking")
        self.server:ServerInterface = server
    
    def copy_data(self):
        pass
    
    def reload_all(self):
        shutil.copytree(self.script_src, self.script_dst, dirs_exist_ok=True)
        self.server.execute("script load advanced_tracking global")
    
    def reload_scoreboards(self):
        shutil.copy(os.path.join(self.data_src, "scoreboards.json"), os.path.join(self.data_dst, "scoreboards.json"))
        self.server.execute("script in advaned_tracking run load_scoreboards(global_DATA_PATH)")
        
    def reload_trackers(self):
        shutil.copy(os.path.join(self.data_src, "trackers.json"), os.path.join(self.data_dst, "trackers.json"))
        self.server.execute("script in advaned_tracking run load_trackers(global_DATA_PATH)")


class PermissionConfig(Serializable):
    pass


class Config(Serializable):
    permissions: PermissionConfig = PermissionConfig()


class AdvancedTrackingManager:
    """Singleton manager for all plugin operations, trackers, and scoreboards."""
    _instance = None
    initialized: bool = False
    tracker_registry: TrackerRegistry
    scoreboard_registry: ScoreboardRegistry
    # script_loader: ScriptLoader
    # config: Config
    command_manager: CommandManager
    server: PluginServerInterface

    def __new__(cls, server: PluginServerInterface = None):
        if cls._instance is None:
            if server is None:
                raise ValueError("Server instance must be provided for the first initialization.")
            cls._instance = super().__new__(cls)
            cls.initialized = True

            cls.server = server
            cls.tracker_registry = TrackerRegistry()
            cls.scoreboard_registry = ScoreboardRegistry()
            # cls.script_loader = ScriptLoader(server, os.path.join(SERVER_PATH, PLUGIN_PATH), os.path.join(SERVER_PATH, R"shared\advanced_tracking"))
            cls.command_manager = CommandManager(server, cls.tracker_registry, cls.scoreboard_registry)
            cls.command_manager.register_commands()
        return cls._instance


advanced_tracking_manager: AdvancedTrackingManager = None
    

def on_load(server:PluginServerInterface):
    global advanced_tracking_manager
    advanced_tracking_manager = AdvancedTrackingManager(server)

    pass
    
