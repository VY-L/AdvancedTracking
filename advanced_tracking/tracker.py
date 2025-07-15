import json
from typing import Dict, Optional, List, Literal

from mcdreforged.utils.serializer import Serializable
from typing_extensions import Self

TrackerType = Literal["player_break_blocks", "player_place_blocks"]

class TrackerComponent(Serializable):
    id: str
    area: Dict[str, int] = {}
    block_type: Dict[str, str] = {}
    comments: str = ""

    def to_script(self) -> Dict:
        return {
            "area": self.area,
            "block_type": self.block_type
        }


class Tracker(Serializable):
    id: str
    type: TrackerType
    # type: str
    area: Dict[str, int]={}
    components: List[TrackerComponent] = []
    comments: str = ""
    def add_component(self, component: TrackerComponent) -> None:
        self.components.append(component)

    def to_script(self) -> Dict:
        return {
            "area": self.area,
            "components": {comp.id: comp.to_script() for comp in self.components}
        }

class TrackerRegistry(Serializable):
    """Registry for all trackers."""
    trackers: List[Tracker]=[]

    def add(self, tracker: Tracker) -> None:
        self.trackers.append(tracker)


    def update_json_file(self, file_path: str) -> None:
        # add all trackers to "default group"，area would be empty
        tracker_types = ["player_break_blocks", "player_place_blocks"]
        data = {"player_break_blocks":{"default_group": {"area":{}, "trackers":{}}},
                "player_place_blocks":{"default_group": {"area":{}, "trackers":{}}}}
        for tracker in self.trackers:
            data[tracker.type]["default_group"]["trackers"][tracker.id] = tracker.to_script()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Example usage
    tracker_registry = TrackerRegistry()

    tracker1 = Tracker(id = "tracker1", type="player_break_blocks", area={"x": 10, "y": 20, "z": 30})
    component1 = TrackerComponent(id = "component1", area={"x_min": 5, "y_min": 5, "z_min": 5}, block_type = {"type": "stone"})
    TrackerComponent.deserialize(component1.serialize())
    # tracker1.add_component("component1")

    tracker_registry.add(tracker1)

    data = tracker_registry.serialize()
    print(json.dumps(data, indent=4, sort_keys=True))

    reloaded_tr = TrackerRegistry.deserialize(data)

    print(data.__eq__(reloaded_tr.serialize()))



    tracker_registry.update_json_file("trackers.json")