from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.serializer import Serializable
from typing import Dict, List, Optional
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




class Scoreboard:
    '''
    A scoreboard class
    
    should load and save into config files
    
    '''
    def __init__(self, objective:str, display_name:Optional[str] = None, mode:str="weighted_sum"):
        if display_name is None:
            display_name = objective
        self.id:str = objective
        self.display_name:str = display_name
        self.mode:str = mode
        self.trackers:List[TrackerScoreboardConfig] = []
    
    def to_script(self):
        '''
        used to generate the json file that the carpet script uses
        '''
        tracker_dicts = map(lambda tsc: tsc.to_script, self.trackers)
        return self.id, {
            "display_name": self.display_name, 
            "mode": self.mode, 
            "trackers": tracker_dicts
        }

    
class TrackerComponent:
    def __init__():
        pass
    def to_string():
        pass

class Tracker:
    '''
    Tracker Class
    '''
    def __init__(self, tracker_id:str, area:Optional[Dict[str, int]]=None):
        if area is None:
            area = {}
        self.id = tracker_id
        self.area=area
        self.components:Dict[str, TrackerComponent] = {}

    def to_script(self):
        '''
        used to generate the json file that the car
        '''
        component_dict = {component_name:self.components[component_name].to_script() for component_name in self.components}
        return {
            "tracker": self.id, 
            "area": self.area, 
            "components": component_dict
        }

class TrackerScoreboardConfig:
    '''
    records a tracker and its weight inside a scoreboard
    '''
    def __init__(self, tracker:Tracker, weight:int=1):
        self.tracker:Tracker = tracker
        self.weight:int = weight
    def to_script(self) -> Dict:
        '''
        used to generate the json file that the carpet script uses
        '''
        return {"tracker_id":self.tracker.id, "weight":self.weight}
    

class ScoreboardManager():
    def __init__(self, server:PluginServerInterface, script_loader:ScriptLoader):
        self.script_loader = script_loader
        self.server:PluginServerInterface = server
        self.load()
        
    def load(self):
        self.scoreboards = self.server.load_config_simple("scoreboards.json", default_config = {})
        
    def add_scoreboard(self, objective:str, display_name:str, trackers=[]):
         pass
        
    
    
    

class TrackerManager():
    def __init__(self):
        pass



class ScriptManager():
    def __init__(self, server:PluginServerInterface, plugin_path:str = R"plugins\AdvancedTracking", server_path = R"server"):
        self.server:PluginServerInterface = server
        self.plugin_path:str = plugin_path
        self.server_path:str = server_path
        
        
    

def on_load(server:PluginServerInterface, prev):
    # global config
    # config = server.load_config_simple(target_class=Config)
    # global script_loader
    # script_loader = ScriptLoader(server, script_src=R"plugins\advancedTracking\Advanced_tracking\scripts", script_dst=R"server\world\scripts")
    # script_loader.reload_all()
    # print("Advanced Tracking loaded")
    # print(ssC.serialize())
    global script_manager
    script_manager = ScriptManager(server)
    

    
    


