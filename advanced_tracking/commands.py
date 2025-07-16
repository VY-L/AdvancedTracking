import json
from typing import Optional, Dict

from mcdreforged.command.builder.common import CommandContext
from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.command_source import CommandSource
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.command.builder.nodes.arguments import Text, QuotableText, Integer

from advanced_tracking.config import Config
from advanced_tracking.tracker import Tracker, TrackerRegistry
from advanced_tracking.scoreboard import Scoreboard, ScoreboardRegistry

TRACKER_TYPE_DICT: Dict[str, str] = {
    "player_break_blocks": "pbb",
    "player_place_blocks": "ppb",
    "ppb": "ppb",
    "pbb": "pbb"
}

class CommandManager:
    def __init__(self, server: PluginServerInterface):
        # if tracker_registry is None:
        #     tracker_registry = TrackerRegistry()
        # if scoreboard_registry is None:
        #     scoreboard_registry = ScoreboardRegistry()
        self.config = Config.get()
        self.server = server
        self.tracker_registry = self.config.tracker_registry
        self.scoreboard_registry = self.config.scoreboard_registry

    # list stuff

    def cmd_list_trackers(self, src: CommandSource, ctx: CommandContext):
        tracker_list = self.tracker_registry.trackers
        if not tracker_list:
            src.reply("No trackers found.")
            return
        response = "Trackers:\n" + "\n".join((f"[{TRACKER_TYPE_DICT[tracker.type]}] {tracker.id}"
                                              + (f": {tracker.comments}" if tracker.comments!="" else ""))
                                             for tracker in tracker_list)
        src.reply(response)

    def cmd_list_scoreboards(self, src: CommandSource, ctx: CommandContext):
        if "scoreboard_id" not in ctx:
            scoreboard_list = self.scoreboard_registry.scoreboards
            if not scoreboard_list:
                src.reply("No scoreboards found.")
                return
            response = "Scoreboards:\n" + "\n".join((f"{scoreboard.id}: {scoreboard.display_name}"
                                                    + (f" ({scoreboard.comments})" if scoreboard.comments!="" else ""))
                                                   for scoreboard in scoreboard_list)
            src.reply(response)
        else:
            scoreboard = self.scoreboard_registry.get(ctx["scoreboard_id"])
            if scoreboard is None:
                src.reply(f"Scoreboard '{ctx['scoreboard_id']}' not found.")
                return
            response = f"Scoreboard '{scoreboard.id}': {scoreboard.display_name}\n"


    # def cmd_list_components(self, src: CommandSource, ctx: CommandContext):
    #     pass

    def cmd_help(self, src:CommandSource, ctx:CommandContext):
        src.reply("To be written.\n") # TODO: Write a proper help message.

    def cmd_add_ppb_tracker(self, src: CommandSource, ctx: CommandContext):
        tracker = Tracker(id=ctx["tracker_id"], type="player_place_blocks")
        self.tracker_registry.add(tracker)

    def cmd_add_pbb_tracker(self, src: CommandSource, ctx: CommandContext):
        tracker = Tracker(id=ctx["tracker_id"], type="player_break_blocks")
        self.tracker_registry.add(tracker)

    def cmd_show_tracker(self, src: CommandSource, ctx: CommandContext):
        tracker = self.tracker_registry.get_tracker(ctx["tracker_id"])
        if tracker is None:
            src.reply(f"Tracker '{ctx['tracker_id']}' not found.")
        else:
            tracker.show_info(src)


    def cmd_add_scoreboard(self, src: CommandSource, ctx: CommandContext):
        print(ctx)
        display_name = ctx.get("display_name", ctx["scoreboard_id"])
        scoreboard = Scoreboard(id=ctx["scoreboard_id"], display_name=display_name, comments=ctx.get("comments", ""))
        if "tracker_id" in ctx:
            scoreboard.add_tracker(ctx["tracker_id"])
        self.scoreboard_registry.add(scoreboard)
    def cmd_add_component(self, src: CommandSource, ctx: CommandContext):
        pass

    def cmd_showraw_scoreboard(self, src: CommandSource, ctx: CommandContext):
        reply = json.dumps(self.scoreboard_registry.serialize(), indent=4, sort_keys=True)
        src.reply(reply)

    def cmd_showraw_tracker(self, src: CommandSource, ctx: CommandContext):
        reply = json.dumps(self.tracker_registry.serialize(), indent=4, sort_keys=True)
        src.reply(reply)

    def show_config(self, src: CommandSource, ctx: CommandContext):
        src.reply(json.dumps(self.config.serialize(), indent=4, sort_keys=True))

    def register_commands(self):
        # tracker creation commands
        player_break_blocks_subtree = Literal("player_break_blocks").runs(self.cmd_add_pbb_tracker)
        player_place_blocks_subtree = Literal("player_place_blocks").runs(self.cmd_add_ppb_tracker)
        self.server.register_command(
            Literal("!!at").runs(self.cmd_help)
            .then(
                Literal("help").runs(self.cmd_help)
            ).then(
                Literal("add")
                .then(
                    Literal("tracker")
                    .then(
                        Text("tracker_id")
                        .then(player_break_blocks_subtree)
                        .then(Literal("pbb").redirects(player_break_blocks_subtree))

                        .then(player_place_blocks_subtree)
                        .then(Literal("ppb").redirects(player_place_blocks_subtree))
                    )
                )
                .then(Literal("component").then(Text("tracker_id").then(
                    Text("component_id").runs(self.cmd_add_component)
                    .then(Integer("x1").then(Integer("y1/z1").then(Integer("z1/x2")
                    .then(Integer("x2/z2").runs(self.cmd_add_component)
                          .then(Integer("y2").then(Integer("z2").runs(self.cmd_add_component)))))))
                )))
                .then(
                    Literal("scoreboard")
                    .then(
                        Text("scoreboard_id").runs(self.cmd_add_scoreboard)
                        .then(QuotableText("display_name").runs(self.cmd_add_scoreboard))
                    )
                )
            ).then(
                Literal("list").runs(self.cmd_help)  # Placeholder for listing trackers/scoreboards
            ).then(
                Literal("show")
                .then(
                    Literal("tracker").then(Text("tracker_id").runs(self.cmd_show_tracker))
                )
            )
            .then(Literal("tracker").then(Text("tracker_id")))
            .then(Literal("component").then(Text("tracker_id").then(Text("component_id"))))
            .then(Literal("scoreboard").then(Text("scoreboard_id")))
            .then(Literal("show_raw").then(Literal("scoreboard").runs(self.cmd_showraw_scoreboard))
                  .then(Literal("tracker").runs(self.cmd_showraw_tracker)))
            .then(Literal("debug").then(Literal("config").runs(self.show_config)))
        )
