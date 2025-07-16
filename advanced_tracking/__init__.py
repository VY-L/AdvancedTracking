from pathlib import Path

from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from advanced_tracking.tracker import Tracker, TrackerRegistry
from advanced_tracking.scoreboard import Scoreboard, ScoreboardRegistry
from advanced_tracking.script_loader import ScriptLoader
from advanced_tracking.config import Config

from advanced_tracking.commands import CommandManager

from typing import Optional

import os

PLUGIN_PATH = r"plugins\AdvancedTracking"

SERVER_PATH = r".\server"



# class PermissionConfig(Serializable):
#     pass


# class Config(Serializable):
#     permissions: PermissionConfig = PermissionConfig()


# class AdvancedTrackingManager:
#     """Singleton manager for all plugin operations, trackers, and scoreboards."""
#     _instance = None
#     initialized: bool = False
#     tracker_registry: TrackerRegistry
#     scoreboard_registry: ScoreboardRegistry
#     script_loader: ScriptLoader
#     # config: Config
#     command_manager: CommandManager
#     server: PluginServerInterface
#
#     def __new__(cls, server: PluginServerInterface = None, server_path: str = SERVER_PATH, plugin_path: str = PLUGIN_PATH):
#         if cls._instance is None:
#             if server is None:
#                 raise ValueError("Server instance must be provided for the first initialization.")
#             cls._instance = super().__new__(cls)
#             cls.initialized = True
#
#             cls.server_path = server_path
#             cls.plugin_path = plugin_path
#
#             cls.server = server
#             cls.tracker_registry = TrackerRegistry()
#             cls.scoreboard_registry = ScoreboardRegistry()
#
#             cls.script_loader = ScriptLoader(server, os.path.join(server_path, plugin_path), os.path.join(server_path, r"shared\advanced_tracking"))
#             cls.command_manager = CommandManager(server, cls.tracker_registry, cls.scoreboard_registry)
#             cls.command_manager.register_commands()
#         return cls._instance



# advanced_tracking_manager: Optional[AdvancedTrackingManager] = None
    

def on_load(server:PluginServerInterface, prev):
    global command_manager, config
    print("AdvancedTracking plugin is loading...")
    # print("prev:", prev)
    print("current path:", os.path.dirname(__file__))
    print("server path:", Path(server.get_mcdr_config().get("working_directory")).absolute())
    config = server.load_config_simple(target_class=Config, failure_policy='raise')
    command_manager = CommandManager(server)
    # advanced_tracking_manager = AdvancedTrackingManager(server)
    pass

def on_unload(server:PluginServerInterface, prev):
    print("AdvancedTracking plugin is unloading...")
    global command_manager, config
    command_manager.unregister_commands()
    server.save_config_simple(config)
