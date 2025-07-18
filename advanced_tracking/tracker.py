import json
from pathlib import Path
from typing import Dict, Optional, List, Literal
import types

from mcdreforged.command.command_source import CommandSource
from mcdreforged.utils.serializer import Serializable
from typing_extensions import Self

# from advanced_tracking import Scoreboard
from advanced_tracking.project_types import BlockTypes
from advanced_tracking.project_types import TrackerType, TrackerMode



class TrackerComponent(Serializable):
    id: str
    area: Dict[str, int] = {}
    block_type: BlockTypes = BlockTypes()
    comments: str = ""

    def to_script(self) -> Dict:
        return {
            "area": self.area,
            "block_type": self.block_type.serialize()
        }

    def show_info(self, src: CommandSource) -> None:
        src.reply(f"Component ID: {self.id}")
        src.reply(f"Area: {self.area}")
        src.reply(f"Block Type: {self.block_type}")
        if self.comments:
            src.reply(f"Comments: {self.comments}")


class Tracker(Serializable):
    id: str
    type: TrackerType
    mode: TrackerMode = "union"
    area: Dict[str, int]={}
    components: List[TrackerComponent] = []
    comments: str = ""
    def add_component(self, component: TrackerComponent) -> None:
        """Add a component to the tracker."""
        for existing_component in self.components:
            if existing_component.id == component.id:
                raise ValueError(f"Component with ID {component.id} already exists in tracker {self.id}.")
        self.components.append(component)
    def remove_component(self, component_id: str) -> bool:
        """Remove a component by its ID."""
        for component in self.components:
            if component.id == component_id:
                self.components.remove(component)
                return True
        return False

    def to_script(self) -> Dict:
        return {
            "area": self.area,
            "components": {comp.id: comp.to_script() for comp in self.components}
        }

    def show_info(self, src: CommandSource) -> None:
        src.reply(f"Tracker ID: {self.id}")
        src.reply(f"Type: {self.type}")
        src.reply(f"Area: {self.area}")
        src.reply(f"Components: {[comp.id for comp in self.components]}")
        if self.comments:
            src.reply(f"Comments: {self.comments}")

    def get_component(self, component_id: str) -> Optional[TrackerComponent]:
        for component in self.components:
            if component.id == component_id:
                return component
        return None

class TrackerRegistry(Serializable):
    """Registry for all trackers."""
    trackers: List[Tracker]=[]

    def add(self, tracker: Tracker) -> None:
        """Add a tracker to the registry."""
        for tracker_ in self.trackers:
            if tracker_.id == tracker.id:
                raise ValueError(f"Tracker with ID {tracker.id} already exists.")
        self.trackers.append(tracker)


    def remove_tracker(self, tracker_id: str) -> bool:
        """Delete a tracker by its ID."""
        for tracker in self.trackers:
            if tracker.id == tracker_id:
                self.trackers.remove(tracker)
                return True
        return False


    def update_json_file(self, file_path: str|Path, scoreboards: List['Scoreboard']) -> None:
        # add all trackers to "default group"，area would be empty
        tracker_types = ["player_break_blocks", "player_place_blocks"]
        data = {"player_break_blocks":{"default_group": {"area":{}, "trackers":{}}},
                "player_place_blocks":{"default_group": {"area":{}, "trackers":{}}}}
        for tracker in self.trackers:
            data[tracker.type]["default_group"]["trackers"][tracker.id] = tracker.to_script()
            data[tracker.type]["default_group"]["trackers"][tracker.id]["scoreboards"] = [
                scoreboard.id for scoreboard in scoreboards if scoreboard.has_tracker(tracker.id)
            ]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_tracker(self, tracker_id: str) -> Optional[Tracker]:
        for tracker in self.trackers:
            if tracker.id == tracker_id:
                return tracker
        return None

    def list_trackers(self, src: CommandSource):
        """List all trackers."""
        if not self.trackers:
            src.reply("No trackers found.")
            return
        for tracker in self.trackers:
            src.reply(f"- {tracker.id} ({tracker.type})" + tracker.comments)

    def reset_all(self) -> None:
        self.trackers = []

if __name__ == "__main__":
    # Example usage
    tracker_registry = TrackerRegistry()

    tracker1 = Tracker(id = "tracker1", type="player_break_blocks", area={"x": 10, "y": 20, "z": 30})
    component1 = TrackerComponent(id = "component1", area={"x_min": 5, "y_min": 5, "z_min": 5})
    TrackerComponent.deserialize(component1.serialize())
    # tracker1.add_component("component1")

    tracker_registry.add(tracker1)

    data = tracker_registry.serialize()
    print(json.dumps(data, indent=4, sort_keys=True))

    reloaded_tr = TrackerRegistry.deserialize(data)

    print(data.__eq__(reloaded_tr.serialize()))

    tracker_registry.update_json_file("trackers.json")