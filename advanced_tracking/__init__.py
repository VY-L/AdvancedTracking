from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.serializer import Serializable
import os
import shutil

PLUGIN_PATH = r"plugins\AdvancedTracking"

SERVER_PATH = r'.\server'

class PermissionConfig(Serializable):
    pass

class Config(Serializable):
    permissions: PermissionConfig = PermissionConfig()


def load_scripts(server: ServerInterface, src=r'plugins\advancedTracking\Advanced_tracking\scripts', dst=r'server\world\scripts'):
    # print(os.listdir(src))
    # print(os.listdir(dst))
    shutil.copytree(src, dst, dirs_exist_ok=True)
    server.execute("script load advanced_tracking global")


def on_load(server:PluginServerInterface, prev):
    global config
    config = server.load_config_simple(target_class=Config)
    # print(os.getcwd())
    load_scripts(server=server)
    print("Advanced Tracking loaded")
    
    
class ScriptLoader():
    def __init__(self, server:ServerInterface, src, dst):
        self.src:str = src
        self.dst:str = dst
        self.server:ServerInterface = server
    
    def reload_all(self):
        shutil.copytree(self.src, self.dst, dirs_exist_ok=True)
        self.server.execute("script load advanced_tracking global")
    
    def reload_scoreboards(self):
        shutil.copy()


