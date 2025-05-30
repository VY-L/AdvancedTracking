from typing import List, Dict, Optional
from typing_extensions import Self

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
        return instance

