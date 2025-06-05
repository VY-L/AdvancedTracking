from mcdreforged.command.builder.common import CommandContext
from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.builder.nodes.special import CountingLiteral
from mcdreforged.command.builder.tools import SimpleCommandBuilder
from mcdreforged.command.command_source import CommandSource
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface

from advanced_tracking import TrackerRegistry, ScoreboardRegistry


class CommandManager:
    def __init__(self, server: PluginServerInterface, tracker_registry: TrackerRegistry, scoreboard_registry: ScoreboardRegistry):
        self.server = server
        self.tracker_registry = tracker_registry
        self.scoreboard_registry = scoreboard_registry

    def cmd_help(self, src:CommandSource, ctx:CommandContext):
        pass



    def register_commands(self):
        self.server.register_command(
            Literal("!!at").runs(self.cmd_help)
        )