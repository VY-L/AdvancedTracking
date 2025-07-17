import json
from typing import Optional, Dict, Callable, List

from mcdreforged.command.builder.common import CommandContext
from mcdreforged.command.builder.nodes.basic import Literal, AbstractNode
from mcdreforged.command.command_source import CommandSource
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.command.builder.nodes.arguments import Text, QuotableText, Integer

from advanced_tracking import ScriptLoader
from advanced_tracking.config import Config
from advanced_tracking.tracker import Tracker, TrackerRegistry
from advanced_tracking.scoreboard import Scoreboard, ScoreboardRegistry
from advanced_tracking.utils.command_nodes import MarkingLiteral

TRACKER_TYPE_DICT: Dict[str, str] = {
    "player_break_blocks": "pbb",
    "player_place_blocks": "ppb",
    "ppb": "ppb",
    "pbb": "pbb"
}

NONE_ALIASES = ["None", "none", "null", "no", "n", 'N', '=', '.']


def construct_flexible_region_subtree(parent: AbstractNode,
                                      exec: Callable[[CommandSource, CommandContext], None],
                                      children: Optional[List[AbstractNode]] = None) -> AbstractNode:
    """
    Constructs a subtree for region commands that can be used in multiple places.
    :param exec: The function to execute when the command is run.
    :param children: Optional children nodes to add to the subtree.
    :return: A Literal node representing the subtree.
    """
    if children is None:
        children = []
    for name in ["x1", "y1", "z1", "x2", "y2", "z2"][::-1]:
        int_node = Integer(name)
        plus_node = MarkingLiteral("+").set_mark('+', name)
        minus_node = MarkingLiteral("-").set_mark('-', name)
        none_nodes = [Literal(alias) for alias in NONE_ALIASES]
        int_node.runs(exec)
        plus_node.runs(exec)
        minus_node.runs(exec)
        for none_node in none_nodes:
            none_node.runs(exec)
        for child in children:
            int_node.then(child)
            plus_node.then(child)
            minus_node.then(child)
            for none_node in none_nodes:
                none_node.then(child)
        children = [int_node, plus_node, minus_node, *none_nodes]
    for child in children:
        parent.then(child)
    parent.runs(exec)
    return parent


def parse_area(ctx: CommandContext) -> Dict[str, int]:
    for axis in ["x", "y", "z"]:
        # number of bounds
        area = {}
        key1 = axis+"1"
        key2 = axis+"2"
        key_min = axis+"_min"
        key_max = axis+"_max"
        type1 = type(ctx[key1])
        type2 = type(ctx[key2])
        if type1 is int:
            if type2 is int:
                area[key_min] = min(ctx[key1], ctx[key2])
                area[key_max] = max(ctx[key1], ctx[key2])
            elif ctx[key2] == "-":
                area[key_max] = ctx[key1]
            else:
                area[key_min] = ctx[key1]
        else:
            if ctx[key2] == "+":
                area[key_min] = ctx[key1]
            else:
                area[key_max] = ctx[key1]
    return area


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
        self.script_loader = ScriptLoader(self.server, self.tracker_registry, self.scoreboard_registry)





    # region list commands
    def cmd_list_trackers(self, src: CommandSource, ctx: CommandContext) -> None:
        self.tracker_registry.list_trackers(src)

    def cmd_list_scoreboards(self, src: CommandSource, ctx: CommandContext) -> None:
        self.scoreboard_registry.list_scoreboards(src)
    # endregion

    # region other show info commands
    def cmd_show_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker = self.tracker_registry.get_tracker(ctx["tracker_id"])
        if tracker is None:
            src.reply(f"Tracker '{ctx['tracker_id']}' not found.")
        else:
            tracker.show_info(src)

    def cmd_show_component(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker = self.tracker_registry.get_tracker(ctx["tracker_id"])
        if tracker is None:
            src.reply(f"Tracker '{ctx['tracker_id']}' not found.")
            return

        component = tracker.get_component(ctx["component_id"])
        if component is None:
            src.reply(f"Component '{ctx['component_id']}' not found in tracker '{ctx['tracker_id']}'.")
        else:
            component.show_info(src)

    def cmd_show_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        scoreboard = self.scoreboard_registry.get_scoreboard(ctx["scoreboard_id"])
        if scoreboard is None:
            src.reply(f"Scoreboard '{ctx['scoreboard_id']}' not found.")
        else:
            scoreboard.show_info(src)
    # endregion

    # def cmd_list_components(self, src: CommandSource, ctx: CommandContext) -> None:
    #     pass

    def cmd_help(self, src:CommandSource, ctx:CommandContext) -> None:
        src.reply("To be written.\n") # TODO: Write a proper help message.

    # region create trackers
    def cmd_add_ppb_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker = Tracker(id=ctx["tracker_id"], type="player_place_blocks")
        self.tracker_registry.add(tracker)
        self.script_loader.inject_tracker_data()

    def cmd_add_pbb_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker = Tracker(id=ctx["tracker_id"], type="player_break_blocks")
        self.tracker_registry.add(tracker)
        self.script_loader.inject_tracker_data()

    # endregion




    def cmd_add_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        print(ctx)
        display_name = ctx.get("display_name", ctx["scoreboard_id"])
        scoreboard = Scoreboard(id=ctx["scoreboard_id"], display_name=display_name, comments=ctx.get("comments", ""))
        if "tracker_id" in ctx:
            scoreboard.add_tracker(ctx["tracker_id"])
        self.scoreboard_registry.add(scoreboard)
    def cmd_add_component(self, src: CommandSource, ctx: CommandContext) -> None:
        pass

    def cmd_showraw_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        reply = json.dumps(self.scoreboard_registry.serialize(), indent=4, sort_keys=True)
        src.reply(reply)

    def cmd_showraw_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        reply = json.dumps(self.tracker_registry.serialize(), indent=4, sort_keys=True)
        src.reply(reply)

    def cmd_show_config(self, src: CommandSource, ctx: CommandContext) -> None:
        src.reply(json.dumps(self.config.serialize(), indent=4, sort_keys=True))

    def cmd_test(self, src: CommandSource, ctx: CommandContext) -> None:
        for key in ctx.keys():
            src.reply(f"{key}: {ctx[key]}")

    def register_commands(self) -> None:
        # tracker creation commands
        player_break_blocks_subtree = Literal("player_break_blocks").runs(self.cmd_add_pbb_tracker)
        player_place_blocks_subtree = Literal("player_place_blocks").runs(self.cmd_add_ppb_tracker)

        test_tree = Literal("test").then(Literal("-").runs(self.cmd_test)).then(Integer("test_int").runs(self.cmd_test))

        self.server.register_command(
            Literal("!!at").runs(self.cmd_help)
            .then(
                Literal("help").runs(self.cmd_help)
            )
            .then(
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
            )
            .then(
                Literal("list")
                .then(Literal("tracker").runs(self.cmd_list_trackers))
                .then(Literal("trackers").runs(self.cmd_list_trackers))
                .then(Literal("scoreboard").runs(self.cmd_list_scoreboards))
                .then(Literal("scoreboards").runs(self.cmd_list_scoreboards))
            )
            .then(
                Literal("show")
                .then(Literal("tracker").then(Text("tracker_id").runs(self.cmd_show_tracker)))
                .then(Literal("scoreboard").then(Text("scoreboard_id").runs(self.cmd_show_scoreboard)))
                .then(Literal("component").then(Text("tracker_id").then(Text("component_id").runs(self.cmd_show_component))))
            )
            .then(Literal("tracker").then(
                Text("tracker_id").runs(self.cmd_show_tracker)
                .then(Literal("add").then(Text("component_id")).runs(self.cmd_add_component))

            ))
            .then(Literal("component").then(Text("tracker_id").then(Text("component_id").runs(self.cmd_show_component))))
            .then(Literal("scoreboard").then(Text("scoreboard_id").runs(self.cmd_show_scoreboard)))
            .then(Literal("show_raw").then(Literal("scoreboard").runs(self.cmd_showraw_scoreboard))
                  .then(Literal("tracker").runs(self.cmd_showraw_tracker)))
            .then(Literal("debug").then(Literal("config").runs(self.cmd_show_config)))
            .then(test_tree)
        )
