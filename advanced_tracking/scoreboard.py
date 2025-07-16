import json
from pathlib import Path
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
    def show_info(self, src: CommandSource):
        '''
        show the scoreboard info to the command source
        '''
        src.reply(f"Scoreboard ID: {self.id}")
        src.reply(f"Display Name: {self.display_name or 'None'}")
        src.reply(f"Mode: {self.mode}")
        if self.mode == "weighted_sum":
            src.reply(f"Trackers: {', '.join([tsc.tracker_id for tsc in self.trackers])}")
        if self.comments:
            src.reply(f"Comments: {self.comments}")



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

    def update_json_file(self, file_path: str|Path) -> None:
        # add all trackers to "default group"，area would be empty
        data = {sb.id: sb.to_script() for sb in self.scoreboards}

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)



    def list_scoreboards(self, src: CommandSource) -> None:
        """
        List all scoreboard IDs.
        """
        if not self.scoreboards:
            src.reply("No scoreboards registered.")
            return
        src.reply("Scoreboards:")
        for scoreboard in self.scoreboards:
            src.reply(f"- {scoreboard.id} (Display Name: {scoreboard.display_name})")
    def list_scoreboards_detailed(self, src: CommandSource) -> None:
        pass

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
