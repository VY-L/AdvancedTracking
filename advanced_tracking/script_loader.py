import shutil
import os
from mcdreforged.plugin.si.server_interface import ServerInterface

class ScriptLoader():
    def __init__(self, server: ServerInterface, script_src, script_dst):
        self.script_src: str = script_src
        self.script_dst: str = script_dst
        self.data_src: str = os.path.join(self.script_src, R"shared\advanced_tracking")
        self.data_dst: str = os.path.join(self.script_dst, R"shared\advanced_tracking")
        self.server: ServerInterface = server

    def copy_data(self):
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
