from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.serializer import Serializable
from tracker import Tracker, TrackerRegistry
from scoreboard import Scoreboard, ScoreboardRegistry

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
    
    def copy_data():
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
    script_loader: ScriptLoader
    config: Config
    server: PluginServerInterface
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.initialized = True
            # Add more initialization as needed
        return cls._instance

    @property
    def trackers(self) -> TrackerRegistry:
        return self.tracker_registry

    @property
    def scoreboards(self) -> ScoreboardRegistry:
        return self.scoreboard_registry
    
    def init(self, server:PluginServerInterface):
        if self.initialized:
            pass
        self.server = server
        self.script_loader = ScriptLoader(server, script_src=os.path.join(PLUGIN_PATH, "scripts"), script_dst=os.path.join(SERVER_PATH, "world", "scripts"))
        self.tracker_registry = TrackerRegistry.deserialize(server.load_config_simple("trackers"))
        self.scoreboard_registry = ScoreboardRegistry.deserialize(server.load_config_simple("scoreboards"))
        self.config = server.load_config_simple(target_class=Config)
        self.script_loader.reload_all()
    
    def save(self):
        self.server.save_config_simple("trackers", self.tracker_registry.serialize())
        self.server.save_config_simple("scoreboards", self.scoreboard_registry.serialize())
        self.server.save_config_simple("config", self.config)
    
    


    

def on_load(server:PluginServerInterface, prev):
    # global config
    # config = server.load_config_simple(target_class=Config)
    # global script_loader
    # script_loader = ScriptLoader(server, script_src=R"plugins\advancedTracking\Advanced_tracking\scripts", script_dst=R"server\world\scripts")
    # script_loader.reload_all()
    # print("Advanced Tracking loaded")
    # print(ssC.serialize())
    # global script_manager
    # script_manager = ScriptManager(server)
    pass
    
