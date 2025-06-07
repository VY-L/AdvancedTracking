from typing import Optional

from mcdreforged.command.builder.common import CommandContext
from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.builder.nodes.special import CountingLiteral
from mcdreforged.command.builder.tools import SimpleCommandBuilder
from mcdreforged.command.command_source import CommandSource
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.command.builder.nodes.arguments import Text, QuotableText

from advanced_tracking.tracker import Tracker, TrackerRegistry
from advanced_tracking.scoreboard import Scoreboard, ScoreboardRegistry


class CommandManager:
    def __init__(self, server: PluginServerInterface,
                 tracker_registry: Optional[TrackerRegistry]=None,
                 scoreboard_registry: Optional[ScoreboardRegistry]=None,):
        if tracker_registry is None:
            tracker_registry = TrackerRegistry()
        if scoreboard_registry is None:
            scoreboard_registry = ScoreboardRegistry()
        self.server = server
        self.tracker_registry = tracker_registry
        self.scoreboard_registry = scoreboard_registry

    def cmd_help(self, src:CommandSource, ctx:CommandContext):
        pass

    def cmd_add_ppb_tracker(self, src: CommandSource, ctx: CommandContext):
        tracker = Tracker(ctx["tracker_id"], "player_place_blocks")
        self.tracker_registry.add(tracker)

    def cmd_add_pbb_tracker(self, src: CommandSource, ctx: CommandContext):
        tracker = Tracker(ctx["tracker_id"], "player_break_blocks")
        self.tracker_registry.add(tracker)



    def cmd_add_scoreboard(self, src: CommandSource, ctx: CommandContext):
        pass

    def cmd_add_component(self, src: CommandSource, ctx: CommandContext):
        pass

    def register_commands(self):
        # tracker creation commands
        player_break_blocks_subtree = Literal("player_break_blocks").runs(self.cmd_add_pbb_tracker)
        player_place_blocks_subtree = Literal("player_place_blocks").runs(self.cmd_add_ppb_tracker)
        self.server.register_command(
            Literal("!!at").runs(self.cmd_help).then(
                Literal("add").then(
                    Literal("tracker").then(Text("tracker_id")
                                            .then(player_break_blocks_subtree).then(Literal("pbb").redirects(player_break_blocks_subtree))
                                            .then(player_place_blocks_subtree).then(Literal("ppb").redirects(player_place_blocks_subtree))
                                            )
                ).then(
                    Literal("component").then(Text("tracker_id").then(Text("component_id").runs(self.cmd_add_component)))
                ).then(
                    Literal("scoreboard").then(Text("scoreboard_id"))
                )
            ).then(
                Literal("tracker").then(Text("tracker_id"))
            ).then(
                Literal("component").then(Text("tracker_id").then(Text("component_id")))
            ).then(
                Literal("scoreboard").then(Text("scoreboard_id"))
            )
        )
