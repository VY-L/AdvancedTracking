import json
from typing import List, Dict, Optional, Type
from typing_extensions import Self
from advanced_tracking.tracker import Tracker


class TrackerScoreboardConfig:
    '''
    records a tracker and its weight inside a scoreboard
    '''
    def __init__(self, tracker_id:str, weight:int=1):
        self.tracker_id = tracker_id
        self.weight:int = weight

    def to_script(self) -> Dict:
        '''
        used to generate the json file that the carpet script uses
        '''
        return {"tracker_id":self.tracker_id, "weight":self.weight}
    
    def to_dict(self) -> Dict:
        return self.to_script()

    @classmethod
    def from_dict(cls, data:Dict) -> Self:
        return cls(data["tracker_id"], data["weight"])

class Scoreboard:
    '''
    A scoreboard class

    should load and save into config files

    '''
    def __init__(self, objective:str, display_name:Optional[str] = None, mode:str="weighted_sum", comments:Optional[str] = None):
        if display_name is None:
            display_name = objective
        self.id:str = objective
        self.display_name:str = display_name
        self.mode:str = mode
        self.trackers:List[TrackerScoreboardConfig] = []
        self.comments = comments if comments is not None else ""

    def add_tracker(self, tracker:TrackerScoreboardConfig) -> None:
        '''
        add a tracker to the scoreboard
        '''
        self.trackers.append(tracker)

    def to_script(self)-> Dict:
        '''
        used to generate the json file that the carpet script uses
        '''
        # tracker_dicts = list(map(lambda tsc: tsc.to_script, self.trackers))
        tracker_dicts = [tsc.to_dict() for tsc in self.trackers]
        return {
            "display_name": self.display_name,
            "mode": self.mode,
            "trackers": tracker_dicts
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "mode": self.mode,
            "trackers": [tracker.to_dict() for tracker in self.trackers],
            "comments": self.comments
        }

    @classmethod
    def from_dict(cls, data:Dict) -> Self:
        tracker = cls(data["id"], data["display_name"], data["mode"], data.get("comments", ""))
        for tracker_weight_pair in data["trackers"]:
            tracker_scoreboard_config = TrackerScoreboardConfig.from_dict(tracker_weight_pair)
            tracker.trackers.append(tracker_scoreboard_config)
        return tracker




class ScoreboardRegistry:
    def __init__(self):
        self.scoreboards: List[Scoreboard] = []

    def add(self, scoreboard: Scoreboard) -> None:
        self.scoreboards.append(scoreboard)

    def get(self, scoreboard_id: str) -> Optional[Scoreboard]:
        for scoreboard in self.scoreboards:
            if scoreboard.id == scoreboard_id:
                return scoreboard
        return None

    def remove(self, scoreboard_id: str) -> None:
        """
        Remove a scoreboard by its ID.
        """
        self.scoreboards = [sb for sb in self.scoreboards if sb.id != scoreboard_id]

    # def all(self) -> List[Scoreboard]:
    #     return list(self.scoreboards.values())


    def to_dict(self) -> Dict:
        return {
            "scoreboards": [sb.to_dict() for sb in self.scoreboards]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        instance = cls()
        instance.scoreboards.clear()
        for sb_data in data.get("scoreboards", []):
            sb = Scoreboard.from_dict(sb_data)
            instance.add(sb)
        return instance

    def to_script(self) -> Dict:
        return {sb.id: sb.to_script() for sb in self.scoreboards}

if __name__ == "__main__":
    # Example usage
    scoreboard_registry = ScoreboardRegistry()
    scoreboard = Scoreboard("example_scoreboard", "Example Scoreboard")
    scoreboard.add_tracker(TrackerScoreboardConfig("tracker1", 2))
    scoreboard_registry.add(scoreboard)

    print(json.dumps(scoreboard_registry.to_dict(), indent=4, sort_keys=True))
    loaded_registry = ScoreboardRegistry.from_dict(scoreboard_registry.to_dict())
    print(json.dumps(loaded_registry.to_script(), indent=4, sort_keys=True))
    # print(loaded_registry.all())
