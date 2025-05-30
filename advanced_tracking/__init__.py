from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
from mcdreforged.utils.serializer import Serializable
from typing import Dict, List, Optional, Type
from typing_extensions import Self
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
        return {
            "display_name": self.display_name, 
            "mode": self.mode, 
            "trackers": tracker_dicts
        }
    
    def serialize(self) -> Dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "mode": self.mode,
            "trackers": [tracker.serialize() if hasattr(tracker, "serialize") else {
                "tracker_id": tracker.tracker.id if hasattr(tracker, "tracker") else None,
                "weight": tracker.weight if hasattr(tracker, "weight") else None
            } for tracker in self.trackers]
        }
    
    @classmethod
    def deserialize(cls, data:Dict) -> "TrackerComponent":
        return cls(
            id=data["id"],
            area=data.get("area", {}),
            block_type=data.get("block_type", {})
        )
    
    def serialize(self) -> Dict:
        return {
            "id": self.id,
            "area": self.area,
            "block_type": self.block_type
        }

    @classmethod
    def deserialize(cls, data:Dict) -> "TrackerComponent":
        return cls(
            id=data["id"],
            area=data.get("area", {}),
            block_type=data.get("block_type", {})
        )

    
class TrackerComponent:
    def __init__(self, id:str, area:Dict[str, int], block_type:Dict):
        self.id:str = id
        self.area:Dict[str, int] = area
        self.block_type:Dict = block_type
    def to_script(self):
        return {
            "area": self.area, 
            "block_type": self.block_type
        }

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
            # "tracker": self.id, 
            "area": self.area, 
            "components": component_dict
        }
    
    def serialize(self) -> Dict:
        return {
            "id": self.id,
            "area": self.area,
            "components": {name: comp.serialize() for name, comp in self.components.items()}
        }

    @classmethod
    def deserialize(cls, data:Dict) -> "Tracker":
        tracker = cls(tracker_id=data["id"], area=data.get("area", {}))
        tracker.components = {name: TrackerComponent.deserialize(comp) for name, comp in data.get("components", {}).items()}
        return tracker

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
    
    def serialize(self) -> Dict:
        return {
            "tracker": self.tracker.serialize(),
            "weight": self.weight
        }

    @classmethod
    def deserialize(cls, data:Dict) -> "TrackerScoreboardConfig":
        tracker = Tracker.deserialize(data["tracker"])
        weight = data.get("weight", 1)
        return cls(tracker=tracker, weight=weight)
    
    def serialize(self) -> Dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "mode": self.mode,
            "trackers": [tracker.serialize() for tracker in self.trackers]
        }

    @classmethod
    def deserialize(cls:Type[Self], data:Dict) -> "Scoreboard":
        obj = cls(
            objective=data["id"],
            display_name=data.get("display_name"),
            mode=data.get("mode", "weighted_sum")
        )
        obj.trackers = [TrackerScoreboardConfig.deserialize(t) for t in data.get("trackers", [])]
        return obj


class TrackerRegistry:
    """Singleton-like registry for all Tracker instances."""
    _instance = None
    trackers: Dict[str, Tracker]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.trackers = {}
        return cls._instance

    def add(self, tracker: Tracker):
        self.trackers[tracker.id] = tracker

    def get(self, tracker_id: str) -> Optional[Tracker]:
        return self.trackers.get(tracker_id)

    def all(self) -> List[Tracker]:
        return list(self.trackers.values())

    def remove(self, tracker_id: str):
        if tracker_id in self.trackers:
            del self.trackers[tracker_id]

    def serialize(self) -> Dict:
        return {
            "trackers": [t.serialize() for t in self.tracker_registry.all()],
            "scoreboards": [s.serialize() for s in self.scoreboard_registry.all()]
        }

    @classmethod
    def deserialize(cls, data: Dict) -> Self:
        instance = cls()
        instance.reset()
        for t_data in data.get("trackers", []):
            tracker = Tracker.deserialize(t_data)
            instance.tracker_registry.add(tracker)
        for s_data in data.get("scoreboards", []):
            scoreboard = Scoreboard.deserialize(s_data)
            instance.scoreboard_registry.add(scoreboard)
        return instance

class ScoreboardRegistry:
    """Singleton-like registry for all Scoreboard instances."""
    _instance = None
    scoreboards: Dict[str, Scoreboard]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.scoreboards = {}
        return cls._instance

    def add(self, scoreboard: Scoreboard):
        self.scoreboards[scoreboard.id] = scoreboard

    def get(self, scoreboard_id: str) -> Optional[Scoreboard]:
        return self.scoreboards.get(scoreboard_id)

    def all(self) -> List[Scoreboard]:
        return list(self.scoreboards.values())

    def remove(self, scoreboard_id: str):
        if scoreboard_id in self.scoreboards:
            del self.scoreboards[scoreboard_id]

    def serialize(self) -> Dict:
        return {
            "scoreboards": [sb.serialize() for sb in self.scoreboards.values()]
        }

    @classmethod
    def deserialize(cls, data: Dict) -> Self:
        instance = cls()
        instance.scoreboards.clear()
        for sb_data in data.get("scoreboards", []):
            sb = Scoreboard.deserialize(sb_data)
            instance.add(sb)
        return instance




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
    

