from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.plugin.si.server_interface import ServerInterface
import os
import shutil

PLUGIN_PATH = r"plugins\AdvancedTracking"

def load_scripts(server: ServerInterface, src=r'plugins\advancedTracking\Advanced_tracking\scripts', dst=r'server\world\scripts'):
    # print(os.listdir(src))
    # print(os.listdir(dst))
    shutil.copytree(src, dst, dirs_exist_ok=True)
    server.execute("script load advanced_tracking global")


def on_load(server:PluginServerInterface, prev):
    # print(os.getcwd())
    load_scripts(server=server)
    print("Advanced Tracking loaded")