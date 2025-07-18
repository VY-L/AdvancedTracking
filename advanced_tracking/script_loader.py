import shutil
import os
from mcdreforged.plugin.si.server_interface import ServerInterface
from pathlib import Path

from advanced_tracking import TrackerRegistry, ScoreboardRegistry
from advanced_tracking.utils.script_holder import CARPET_SCRIPT


class ScriptLoader():
    def __init__(self, server: ServerInterface, tracker_registry: TrackerRegistry, scoreboard_registry: ScoreboardRegistry):
        # self.script_src = os.path.dirname(__file__)
        self.server_path = Path(server.get_mcdr_config().get("working_directory"))
        self.script_dst = self.server_path / "world" / "scripts"
        # self.data_src: str = os.path.join(self.script_src, R"shared\advanced_tracking")
        self.data_dst = self.script_dst / "shared" / "advanced_tracking"
        self.server: ServerInterface = server
        self.scoreboard_registry: ScoreboardRegistry = scoreboard_registry
        self.tracker_registry: TrackerRegistry = tracker_registry
        self.inject_all()
    def inject_script(self):
        """
        Injects the script into the server's script directory.
        """
        if not self.script_dst.exists():
            self.script_dst.mkdir(parents=True, exist_ok=True)
        with open(self.script_dst / "advanced_tracking.sc", "w") as script_file:
            script_file.write(CARPET_SCRIPT)
            self.server.execute("script load advanced_tracking global")

    def inject_scoreboard_data(self):
        """
        Injects the scoreboard data into the server's data directory.
        """
        if not self.data_dst.exists():
            self.data_dst.mkdir(parents=True, exist_ok=True)

        # Save scoreboards
        scoreboards_path = self.data_dst / "scoreboards.json"
        self.scoreboard_registry.update_json_file(scoreboards_path)

        self.server.execute("script in advanced_tracking run load_scoreboards(global_DATA_PATH)")
    def inject_tracker_data(self):
        """
        Injects the tracker data into the server's data directory.
        """
        if not self.data_dst.exists():
            self.data_dst.mkdir(parents=True, exist_ok=True)

        # Save trackers
        trackers_path = self.data_dst / "trackers.json"
        self.tracker_registry.update_json_file(trackers_path, self.scoreboard_registry.scoreboards)

        self.server.execute("script in advanced_tracking run load_trackers(global_DATA_PATH)")

    def inject_data(self):
        self.inject_scoreboard_data()
        self.inject_tracker_data()

    def inject_all(self):
        """
        Injects both the script and the data into the server's directories.
        """
        self.inject_script()
        self.inject_data()