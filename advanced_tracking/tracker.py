import json
from typing import Dict, Optional, List, Literal
from typing_extensions import Self

TrackerType = Literal["player_break_blocks", "player_place_blocks"]

class TrackerComponent:
    def __init__(self, id: str, area: Dict[str, int], block_type: Dict, comments: Optional[str] = None):
        self.id = id
        self.area = area
        self.block_type = block_type
        self.comments = comments if comments is not None else ""

    # def update(self, area: Optional[Dict[str, int]] = None, block_type: Optional[Dict] = None):
    #     if area is not None:
    #         self.area = area
    #     if block_type is not None:
    #         self.block_type = block_type

    def to_script(self) -> Dict:
        return {
            "area": self.area,
            "block_type": self.block_type
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            area=data["area"],
            block_type=data["block_type"],
            comments=data.get("comments", "")
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "area": self.area,
            "block_type": self.block_type,
            "comments": self.comments
        }

class Tracker:
    def __init__(self, tracker_id: str, tracker_type: TrackerType, area: Optional[Dict[str, int]] = None, comments: Optional[str] = None):
        # if tracker_type not in ("player_break_blocks", "player_place_blocks"):
        #     raise ValueError("tracker_type must be 'player_break_blocks' or 'player_place_blocks'")
        self.id = tracker_id
        self.type = tracker_type
        self.area = area if area is not None else {}
        self.components: List[TrackerComponent] = []
        self.comments:str = comments if comments is not None else ""

    def add_component(self, name: str, component: TrackerComponent) -> None:
        self.components.append(component)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "area": self.area,
            "components": [comp.to_dict() for comp in self.components],
            "comments": self.comments
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        tracker = cls(
            tracker_id=data["id"],
            tracker_type=data["type"],
            area=data.get("area", {}),
            comments=data.get("comments", "")
        )
        # 兼容组件为列表或字典
        components = data.get("components", [])
        if isinstance(components, dict):
            components = list(components.values())
        for comp_data in components:
            tracker.components.append(TrackerComponent.from_dict(comp_data))
        return tracker

    def to_script(self) -> Dict:
        return {
            "area": self.area,
            "components": {comp.id: comp.to_script() for comp in self.components}
        }

class TrackerRegistry:
    def __init__(self):
        self.trackers: List[Tracker] = []

    def add(self, tracker: Tracker) -> None:
        self.trackers.append(tracker)

    def to_dict(self) -> Dict[str, Dict]:
        return {tracker.id: tracker.to_dict() for tracker in self.trackers}

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        registry = cls()
        for tracker_id, tracker_data in data.items():
            tracker = Tracker.from_dict(tracker_data)
            registry.trackers.append(tracker)
        return registry

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

    tracker1 = Tracker("tracker1", "player_break_blocks", area={"x": 10, "y": 20, "z": 30})
    component1 = TrackerComponent("component1", {"x_min": 5, "y_min": 5, "z_min": 5}, {"type": "stone"})
    tracker1.add_component("component1", component1)

    tracker_registry.add(tracker1)

    data = tracker_registry.to_dict()
    print(json.dumps(data, indent=4, sort_keys=True))

    reloaded_tr = TrackerRegistry.from_dict(data)

    print(data.__eq__(reloaded_tr.to_dict()))



    tracker_registry.update_json_file("trackers.json")