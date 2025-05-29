from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.serializer import Serializable
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
    
    def _copy_data():
        pass
    
    def reload_all(self):
        shutil.copytree(self.script_src, self.script_dst, dirs_exist_ok=True)
        self.server.execute("script load advanced_tracking global")
    
    def reload_scoreboards(self):
        shutil.copy(os.path.join(self.data_src, "scoreboards.json"), os.path.join(self.data_dst, "scoreboards.json"))
        
    def reload_trackers(self):
        shutil.copy(os.path.join(self.data_src, "trackers.json"), os.path.join(self.data_dst, "trackers.json"))



class PermissionConfig(Serializable):
    pass

class Config(Serializable):
    permissions: PermissionConfig = PermissionConfig()


# def load_scripts(server: ServerInterface, src=R'plugins\advancedTracking\Advanced_tracking\scripts', dst=R'server\world\scripts'):
#     # print(os.listdir(src))
#     # print(os.listdir(dst))
#     shutil.copytree(src, dst, dirs_exist_ok=True)
#     server.execute("script load advanced_tracking global")


def on_load(server:PluginServerInterface, prev):
    global config
    config = server.load_config_simple(target_class=Config)
    global script_loader
    script_loader = ScriptLoader(server, script_src=R"plugins\advancedTracking\Advanced_tracking\scripts", script_dst=R"server\world\scripts")
    script_loader.reload_all()
    print("Advanced Tracking loaded")


    
    


