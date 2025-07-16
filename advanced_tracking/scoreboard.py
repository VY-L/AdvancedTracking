import json
from typing import List, Dict, Optional, Type

from mcdreforged.command.command_source import CommandSource
from mcdreforged.utils.serializer import Serializable
from typing_extensions import Self
from advanced_tracking.tracker import Tracker


class TrackerScoreboardConfig(Serializable):
    '''
    records a tracker and its weight inside a scoreboard
    '''
    tracker_id: str
    weight: int


    def to_script(self) -> Dict:
        '''
        used to generate the json file that the carpet script uses
        '''
        return {"tracker_id":self.tracker_id, "weight":self.weight}


class Scoreboard(Serializable):
    '''
    A scoreboard class

    should load and save into config files

    '''

    id: str
    _display_name: Optional[str] = None
    mode: str = "weighted_sum"  # or "average", "max", etc., not supported yet
    trackers: List[TrackerScoreboardConfig] = []
    comments: str = ""

    @property
    def display_name(self) -> str:
        if self._display_name is None:
            return self.id
        return self._display_name

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
        tracker_dicts = [tsc.to_script() for tsc in self.trackers]
        return {
            "display_name": self.display_name,
            "mode": self.mode,
            "trackers": tracker_dicts
        }


class ScoreboardRegistry(Serializable):
    scoreboards: List[Scoreboard] = []
    # def __init__(self):
    #     self.scoreboards: List[Scoreboard] = []

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


    def to_script(self) -> Dict:
        return {sb.id: sb.to_script() for sb in self.scoreboards}

if __name__ == "__main__":
    # Example usage
    scoreboard_registry = ScoreboardRegistry()
    scoreboard = Scoreboard(id = "example_scoreboard", display_name = "Example Scoreboard")
    scoreboard.add_tracker(TrackerScoreboardConfig(tracker_id = "tracker1", weight = 2))
    scoreboard_registry.add(scoreboard)

    print(json.dumps(scoreboard_registry.serialize(), indent=4, sort_keys=True))
    loaded_registry = ScoreboardRegistry.deserialize(scoreboard_registry.serialize())
    print(json.dumps(loaded_registry.to_script(), indent=4, sort_keys=True))
    # print(loaded_registry.all())
