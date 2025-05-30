from typing import List, Dict, Optional, Type
from typing_extensions import Self
from advanced_tracking.tracker import Tracker


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
    def deserialize(cls, data:Dict) -> Self:
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
    def deserialize(cls, data:Dict) -> Self:
        return cls(
            id=data["id"],
            area=data.get("area", {}),
            block_type=data.get("block_type", {})
        )



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

