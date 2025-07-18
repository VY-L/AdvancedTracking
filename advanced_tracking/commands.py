import json
from typing import Optional, Dict, Callable, List, Tuple, get_args

from mcdreforged.command.builder.tools import SimpleCommandBuilder
from typing_extensions import Self

from mcdreforged.command.builder.common import CommandContext
from mcdreforged.command.builder.nodes.basic import Literal, AbstractNode
from mcdreforged.command.command_source import CommandSource, PlayerCommandSource
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
from mcdreforged.command.builder.nodes.arguments import Text, QuotableText, Integer, GreedyText
from mcdreforged.utils.serializer import Serializable

from advanced_tracking import ScriptLoader
from advanced_tracking.config import Config
from advanced_tracking.project_types import TrackerType, TrackerMode, BlockTypes, BlockTypeMode
from advanced_tracking.tracker import Tracker, TrackerRegistry, TrackerComponent
from advanced_tracking.scoreboard import Scoreboard, ScoreboardRegistry
from advanced_tracking.utils.command_nodes import MarkingLiteral

from time import time

CONFIRM_TIME = 60

TRACKER_TYPE_DICT: Dict[str, str] = {
    'player_break_blocks': 'pbb',
    'player_place_blocks': 'ppb',
    'ppb': 'ppb',
    'pbb': 'pbb'
}

NONE_ALIASES: List[str] = ['None', 'none', 'null', 'no', 'n', 'N', '=', '.']

REMOVE_ALIASES: List[str] = ['remove', 'rm', 'del', 'delete']

def reg_flexible_region_selection(parent: AbstractNode,
                                  exec: Callable[[CommandSource, CommandContext], None],
                                  children: Optional[List[AbstractNode]] = None) -> AbstractNode:
    if children is None:
        children = []
    for name in ['x1', 'y1', 'z1', 'x2', 'y2', 'z2'][::-1]:
        int_node = Integer(name)
        plus_node = MarkingLiteral('+').set_mark('+', name)
        minus_node = MarkingLiteral('-').set_mark('-', name)
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
    area = {}
    print('Parsing area from context:', ctx)
    for axis in ['x', 'y', 'z']:
        # number of bounds
        key1 = axis + '1'
        key2 = axis + '2'
        key_min = axis + '_min'
        key_max = axis + '_max'
        type1 = type(ctx.get(key1))
        type2 = type(ctx.get(key2))
        if type1 is int:
            if type2 is int:
                area[key_min] = min(ctx[key1], ctx[key2])
                area[key_max] = max(ctx[key1], ctx[key2])
            elif ctx.get(key2) == '-':
                print(f'Check {key_max}, {ctx[key1]}')
                area[key_max] = ctx[key1]
            else:
                area[key_min] = ctx[key1]
        elif type2 is int:
            if ctx.get(key1) == '+':
                area[key_min] = ctx[key2]
            else:
                area[key_max] = ctx[key2]
    print('Parsed area:', area)
    return area


class ConfirmCache(Serializable):
    func: Optional[Callable[[CommandSource, CommandContext], None]] = None
    src: Optional[CommandSource] = None
    ctx: Optional[CommandContext] = None
    time: float = 0.0


class ConfirmCacheManager:
    '''
    Cache for commands that require confirmation.
    '''

    def __init__(self):
        self._player_cache: Dict[str, ConfirmCache] = {}
        self.console_cache: ConfirmCache = ConfirmCache()

    def confirm(self, src: CommandSource, ctx: CommandContext) -> None:
        '''
        Confirm a command.
        '''
        if src.is_console:
            if self.console_cache.func is None:
                src.reply('No command to confirm.')
                return
            if time() - self.console_cache.time > CONFIRM_TIME:
                src.reply('Confirmation time expired.')
                self.console_cache = (None, None, None, 0)
                return
            self.console_cache.func(self.console_cache.src, self.console_cache.ctx)
        elif src.is_player:
            src: PlayerCommandSource
            player_name = src.player
            if player_name not in self._player_cache:
                src.reply('No command to confirm.')
                return
            cache = self._player_cache[player_name]
            if cache.func is None:
                src.reply('No command to confirm.')
                return
            if time() - cache.time > CONFIRM_TIME:
                src.reply('Confirmation time expired.')
                del self._player_cache[player_name]
                return
            cache.func(cache.src, cache.ctx)
            del self._player_cache[player_name]
        else:
            src.reply('Unknown command source type. Cannot confirm command. WHO ARE YOU?')

    def register_confirmable(self, src: CommandSource, ctx: CommandContext,
                             func: Callable[[CommandSource, CommandContext], None]) -> None:
        if src.is_console:
            self.console_cache.func = func
            self.console_cache.src = src
            self.console_cache.ctx = ctx
            self.console_cache.time = time()
        elif src.is_player:
            src: PlayerCommandSource
            player_name = src.player
            if player_name not in self._player_cache:
                self._player_cache[player_name] = ConfirmCache()
            cache = self._player_cache[player_name]
            cache.func = func
            cache.src = src
            cache.ctx = ctx
            cache.time = time()
        else:
            src.reply('Unknown command source type. Cannot register confirmable command. WHO ARE YOU?')


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
        self.confirm_cache: ConfirmCacheManager = ConfirmCacheManager()

    def parse_tracker(self, src: CommandSource, ctx: CommandContext) -> Optional[Tracker]:
        '''
        Parse a tracker from the context.
        '''
        tracker_id = ctx['tracker_id']
        tracker = self.tracker_registry.get_tracker(tracker_id)
        if tracker is None:
            src.reply(f"Tracker '{tracker_id}' not found.")
        return tracker

    def parse_component(self, src: CommandSource, ctx: CommandContext) -> Tuple[
        Optional[Tracker], Optional[TrackerComponent]]:
        '''
        Parse a component from the context.
        '''
        tracker_id = ctx['tracker_id']
        component_id = ctx['component_id']
        tracker = self.tracker_registry.get_tracker(tracker_id)
        if tracker is None:
            src.reply(f"Tracker '{tracker_id}' not found.")
            return None, None
        component = tracker.get_component(component_id)
        if component is None:
            src.reply(f"Component '{component_id}' not found in tracker '{tracker_id}'.")
        return tracker, component

    @staticmethod
    def confirmable(func: Callable[['CommandManager', CommandSource, CommandContext], None]) \
            -> Callable[['CommandManager', CommandSource, CommandContext], None]:
        '''
        Decorator to require confirmation for a command.
        '''

        def wrapper(cmd_manager: Self, src: CommandSource, ctx: CommandContext) -> None:
            src.reply('Please confirm this command by `!!at confirm` within 60 seconds.')
            cmd_manager.confirm_cache.register_confirmable(src, ctx, lambda s, c: func(cmd_manager, s, c))

        return wrapper

    def cmd_confirm(self, src: CommandSource, ctx: CommandContext) -> None:
        self.confirm_cache.confirm(src, ctx)

    @confirmable
    def cmd_reset_all(self, src: CommandSource, ctx: CommandContext) -> None:
        '''
        Reset all trackers and scoreboards.
        '''
        self.tracker_registry.reset_all()
        self.scoreboard_registry.reset_all()
        self.script_loader.inject_all()
        src.reply('All trackers and scoreboards have been reset.')

    # region list commands
    def cmd_list_trackers(self, src: CommandSource, ctx: CommandContext) -> None:
        self.tracker_registry.list_trackers(src)

    def cmd_list_scoreboards(self, src: CommandSource, ctx: CommandContext) -> None:
        self.scoreboard_registry.list_scoreboards(src)

    # endregion

    # region other show info commands
    def cmd_show_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker = self.tracker_registry.get_tracker(ctx['tracker_id'])
        if tracker is None:
            src.reply(f"Tracker '{ctx['tracker_id']}' not found.")
        else:
            tracker.show_info(src)

    def cmd_show_component(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker = self.tracker_registry.get_tracker(ctx['tracker_id'])
        if tracker is None:
            src.reply(f"Tracker '{ctx['tracker_id']}' not found.")
            return

        component = tracker.get_component(ctx['component_id'])
        if component is None:
            src.reply(f"Component '{ctx['component_id']}' not found in tracker '{ctx['tracker_id']}'.")
        else:
            component.show_info(src)

    def cmd_show_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        scoreboard = self.scoreboard_registry.get_scoreboard(ctx['scoreboard_id'])
        if scoreboard is None:
            src.reply(f"Scoreboard '{ctx['scoreboard_id']}' not found.")
        else:
            scoreboard.show_info(src)

    def cmd_showraw_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        reply = json.dumps(self.scoreboard_registry.serialize(), indent=4, sort_keys=True)
        src.reply(reply)

    def cmd_showraw_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        reply = json.dumps(self.tracker_registry.serialize(), indent=4, sort_keys=True)
        src.reply(reply)

    # endregion

    # def cmd_list_components(self, src: CommandSource, ctx: CommandContext) -> None:
    #     pass

    def cmd_help(self, src: CommandSource, ctx: CommandContext) -> None:
        src.reply('To be written.\n')  # TODO: Write a proper help message.

    # region tracker commands
    # region create trackers

    @confirmable
    def override_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Override an existing tracker with the same ID.
        """
        tracker = self.tracker_registry.get_tracker(ctx['tracker_id'])
        tracker: Tracker
        tracker.type = ctx['tracker_type']
        tracker.area = parse_area(ctx)
        tracker.mode = 'union'
        tracker.components = []
        tracker.comments = ctx.get('comments', '')
        self.script_loader.inject_tracker_data()
        src.reply(f"Tracker '{ctx['tracker_id']}' has been overridden.")

    def add_tracker(self, src: CommandSource, ctx: CommandContext, tracker_type: TrackerType) -> None:
        if self.tracker_registry.get_tracker(ctx['tracker_id']) is not None:
            src.reply(f"Tracker '{ctx['tracker_id']}' already exists. Please use !!at confirm to override.")
            self.override_tracker(src, ctx)
            return
        tracker = Tracker(id=ctx['tracker_id'], type=tracker_type, area=parse_area(ctx))
        self.tracker_registry.add(tracker)
        self.script_loader.inject_tracker_data()

    def cmd_add_ppb_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        self.add_tracker(src, ctx, 'player_place_blocks')

    def cmd_add_pbb_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        self.add_tracker(src, ctx, 'player_break_blocks')

    # endregion

    @confirmable
    def cmd_remove_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Remove a tracker by ID.
        """
        tracker_id = ctx['tracker_id']
        if self.tracker_registry.remove(tracker_id):
            src.reply(f"Tracker '{tracker_id}' has been removed.")
        else:
            src.reply(f"Tracker '{tracker_id}' not found.")

    # region edit trackers
    @confirmable
    def cmd_set_tracker_area(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        set the area of an existing tracker.
        """
        tracker_id = ctx['tracker_id']
        tracker = self.parse_tracker(src, ctx)
        if tracker is None:
            return
        area = parse_area(ctx)
        tracker.area = area
        self.tracker_registry.add(tracker)
        self.script_loader.inject_tracker_data()
        src.reply(f"Tracker '{tracker_id}' area has been updated to {area}.")

    def set_tracker_type(self, src: CommandSource, ctx: CommandContext, tracker_type: TrackerType) -> None:
        """
        set the type of an existing tracker.
        """
        tracker_id = ctx['tracker_id']
        tracker = self.parse_tracker(src, ctx)
        if tracker is None:
            return
        if tracker.type == tracker_type:
            src.reply(f"Tracker '{tracker_id}' is already of type '{tracker_type}'.")
            return
        tracker.type = tracker_type
        self.tracker_registry.add(tracker)
        self.script_loader.inject_tracker_data()
        src.reply(f"Tracker '{tracker_id}' type has been updated to '{tracker_type}'.")

    def cmd_set_tracker_ppb(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Set the tracker type to player_place_blocks.
        """
        self.set_tracker_type(src, ctx, 'player_place_blocks')

    def cmd_set_tracker_pbb(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Set the tracker type to player_break_blocks.
        """
        self.set_tracker_type(src, ctx, 'player_break_blocks')

    def set_tracker_mode(self, src: CommandSource, ctx: CommandContext, mode: TrackerMode) -> None:
        """
        set the mode of an existing tracker.
        """
        tracker_id = ctx['tracker_id']
        tracker = self.parse_tracker(src, ctx)
        if tracker is None:
            return
        if mode not in get_args(TrackerMode):
            src.reply(f"Invalid mode '{mode}'. Valid modes are 'default' and 'advanced'.")
            return
        tracker.mode = mode
        self.script_loader.inject_tracker_data()
        src.reply(f"Tracker '{tracker_id}' mode has been updated to '{mode}'.")

    def cmd_set_tracker_sum(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Set the tracker mode to 'sum'.
        """
        self.set_tracker_mode(src, ctx, 'sum')

    def cmd_set_tracker_union(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Set the tracker mode to 'union'.
        """
        self.set_tracker_mode(src, ctx, 'union')

    # endregion
    # endregion
    # component commands
    @confirmable
    def override_component(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Override an existing component in a tracker.
        """
        tracker_id = ctx['tracker_id']
        component_id = ctx['component_id']
        tracker = self.tracker_registry.get_tracker(tracker_id)
        component = tracker.get_component(component_id)
        area = parse_area(ctx)
        component.area = area
        component.comments = ''
        component.block_type = BlockTypes()
        self.script_loader.inject_tracker_data()
        src.reply(f"Component '{component_id}' has been overridden in tracker '{tracker_id}' with area {area}.")

    def cmd_add_component(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Add a component to a tracker.
        """
        src.reply('Adding component to tracker...')
        tracker_id = ctx['tracker_id']
        component_id = ctx['component_id']
        tracker = self.tracker_registry.get_tracker(tracker_id)
        if tracker is None:
            src.reply(f"Tracker '{tracker_id}' not found.")
            return
        src.reply('tracker found, creating component...')
        if tracker.get_component(component_id) is not None:
            src.reply(
                f"Component '{component_id}' already exists in tracker '{tracker_id}', please use !!at confirm to override.")
            self.override_component(src, ctx)
            return
        src.reply('Component not found, creating new one...')
        area = parse_area(ctx)
        component = TrackerComponent(id=component_id, area=area, comments='', block_type=BlockTypes())
        tracker.add_component(component)
        self.script_loader.inject_tracker_data()
        src.reply(f"Component '{component_id}' has been added to tracker '{tracker_id}' with area {area}.")

    @confirmable
    def cmd_remove_component(self, src: CommandSource, ctx: CommandContext) -> None:
        tracker, component = self.parse_component(src, ctx)
        if component is None:
            return
        tracker.remove_component(component.id)

    # region component editing
    def set_component_list_mode(self, src: CommandSource, ctx: CommandContext, mode: BlockTypeMode) -> None:
        """
        Set the component mode to 'list'.
        """
        tracker, component = self.parse_component(src, ctx)
        if component is None:
            return
        component.block_type.mode = mode
        self.script_loader.inject_tracker_data()
        src.reply(f"Component '{component.id}' in tracker '{tracker.id}' has been set to 'list' mode.")

    def cmd_set_component_whitelist(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Set the component mode to 'whitelist'.
        """
        self.set_component_list_mode(src, ctx, 'whitelist')
        # TODO: click+confirm to reset list

    def cmd_set_component_blacklist(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Set the component mode to 'blacklist'.
        """
        self.set_component_list_mode(src, ctx, 'blacklist')
        # TODO: click+confirm to reset list

    @confirmable
    def cmd_overwrite_block_list(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Edit the block list of a component.
        """
        lst = dict(ctx['list'])
        tracker, component = self.parse_component(src, ctx)
        if component is None:
            return
        if component.block_type.mode is None:
            src.reply(f"Component '{component.id}' in tracker '{tracker.id}' has no block type mode set. "
                      f"Please set it to 'whitelist' or 'blacklist' first.")
            return
        component.block_type.list = lst
        self.script_loader.inject_tracker_data()

    def cmd_add_block_type_to_list(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Add a block type to a component.
        """
        tracker, component = self.parse_component(src, ctx)
        if component is None:
            return
        if component.block_type.mode is None:
            src.reply(f"Component '{component.id}' in tracker '{tracker.id}' has no block type mode set. "
                      f"Please set it to 'whitelist' or 'blacklist' first.")
            return
        block_type = ctx['block_type']
        if block_type not in component.block_type.list:
            component.block_type.list[block_type] = [{}] # TODO: blockstate support
        component.block_type.list[block_type].append(ctx['block_data'])
        self.script_loader.inject_tracker_data()

    # endregion
    # endregion

    # region scoreboard commands
    @confirmable
    def override_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Override an existing scoreboard with the same ID.
        """

        scoreboard_id = ctx['scoreboard_id']
        if not self.scoreboard_registry.remove(scoreboard_id):
            src.reply(f"Scoreboard '{scoreboard_id}' not found.")
            return
        self.cmd_add_component(src, ctx)

    def cmd_add_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        if self.scoreboard_registry.get_scoreboard(ctx['scoreboard_id']) is not None:
            src.reply(f"Scoreboard '{ctx['scoreboard_id']}' already exists. Please use !!at confirm to override.")
            self.override_scoreboard(src, ctx)
            return
        display_name = ctx.get('display_name', ctx['scoreboard_id'])
        scoreboard = Scoreboard(id=ctx['scoreboard_id'], display_name_=display_name, comments=ctx.get('comments', ''))
        if 'tracker_id' in ctx:
            scoreboard.add_tracker(ctx['tracker_id'])
        self.scoreboard_registry.add(scoreboard)
        self.script_loader.inject_scoreboard_data()

    def cmd_scoreboard_add_tracker(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Add a tracker to a scoreboard.
        """
        scoreboard_id = ctx['scoreboard_id']
        tracker_id = ctx['tracker_id']
        scoreboard = self.scoreboard_registry.get_scoreboard(scoreboard_id)
        flag = False
        if scoreboard is None:
            src.reply(f"Scoreboard '{scoreboard_id}' not found.")
            flag = True
        if self.tracker_registry.get_tracker(tracker_id) is None:
            src.reply(f"Tracker '{tracker_id}' not found.")
            flag = True
        if flag:
            return
        scoreboard.add_tracker(tracker_id)
        self.script_loader.inject_data()
        src.reply(f"Tracker '{tracker_id}' has been added to scoreboard '{scoreboard_id}'.")

    @confirmable
    def cmd_remove_scoreboard(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Remove a scoreboard by ID.
        """
        scoreboard_id = ctx['scoreboard_id']
        if self.scoreboard_registry.remove(scoreboard_id):
            src.reply(f"Scoreboard '{scoreboard_id}' has been removed.")
        else:
            src.reply(f"Scoreboard '{scoreboard_id}' not found.")
    # endregion

    def cmd_reload_scripts(self, src: CommandSource, ctx: CommandContext) -> None:
        """
        Reload the scripts.
        """
        self.script_loader.inject_tracker_data()
        src.reply('Scripts have been reloaded.')

    def cmd_show_config(self, src: CommandSource, ctx: CommandContext) -> None:
        src.reply(json.dumps(self.config.serialize(), indent=4, sort_keys=True))

    def cmd_test(self, src: CommandSource, ctx: CommandContext) -> None:
        for key in ctx.keys():
            src.reply(f'{key}: {ctx[key]}')
        try:
            hash(src)
            src.reply('hashable')
        except TypeError:
            src.reply('not hashable')

    def register_commands(self) -> None:

        root = Literal('!!at').runs(self.cmd_help)

        builder = SimpleCommandBuilder()

        builder.command('help', self.cmd_help)
        builder.command('help <command>', self.cmd_help)

        builder.arg('command', Text)


        builder.command('reset_all', self.cmd_reset_all)
        builder.command('confirm', self.cmd_confirm)

        # List commands
        builder.command('list tracker', self.cmd_list_trackers)
        builder.command('list trackers', self.cmd_list_trackers)
        builder.command('list scoreboard', self.cmd_list_scoreboards)
        builder.command('list scoreboards', self.cmd_list_scoreboards)

        # show commands
        builder.command('show tracker <tracker_id>', self.cmd_show_tracker)
        builder.command('show component <tracker_id> <component_id>', self.cmd_show_component)
        builder.command('show scoreboard <scoreboard_id>', self.cmd_show_scoreboard)
        builder.command('showraw tracker', self.cmd_showraw_tracker)
        builder.command('showraw scoreboard', self.cmd_showraw_scoreboard)
        builder.command('showraw all', self.cmd_show_config)

        builder.arg('tracker_id', Text)
        builder.arg('component_id', Text)
        builder.arg('scoreboard_id', Text)

        # remove
        for alias in REMOVE_ALIASES:
            builder.command(f'{alias} tracker <tracker_id>', self.cmd_remove_tracker)
            builder.command(f'{alias} component <tracker_id> <component_id>', self.cmd_remove_component)
            # builder.command(f'{alias} scoreboard <scoreboard_id>', self.cmd_remove_scoreboard)


        # builder.print_tree(print)
        builder.add_children_for(root)

        # region add
        # tracker creation commands
        pbb_subtree = reg_flexible_region_selection(Literal('player_break_blocks'), self.cmd_add_pbb_tracker)
        ppb_subtree = reg_flexible_region_selection(Literal('player_place_blocks'), self.cmd_add_ppb_tracker)

        create_tracker_tree = (Text('tracker_id').then(pbb_subtree).then(Literal('pbb').redirects(pbb_subtree))
                               .then(ppb_subtree).then(Literal('ppb').redirects(ppb_subtree)))

        create_scoreboard_tree = (Text('scoreboard_id').runs(self.cmd_add_scoreboard)
                                  .then(QuotableText('display_name').runs(self.cmd_add_scoreboard)))

        create_component_tree = Text('tracker_id').then(
            reg_flexible_region_selection(Text('component_id'), self.cmd_add_component))

        add_tree = (Literal('add')
                    .then(Literal('tracker').then(create_tracker_tree))
                    .then(Literal('component').then(create_component_tree))
                    .then(Literal('scoreboard').then(create_scoreboard_tree)))
        root.then(add_tree)
        # endregion

        # region tracker subtree
        tree_end = Text('tracker_id').runs(self.cmd_show_tracker)
        for alias in REMOVE_ALIASES:
            tree_end = tree_end.then(Literal(alias).runs(self.cmd_remove_tracker)
                                     .then(Text('component_id').runs(self.cmd_remove_component)))
        tree_end = tree_end.then(Literal('add').then(Text('component_id').redirects(create_component_tree))) # FIXME


        tree_head = Literal('tracker').then(tree_end)
        root.then(tree_head)
        # endregion

        # region component subtree
        tree_end = Text('component_id').runs(self.cmd_show_tracker)
        for alias in REMOVE_ALIASES:
            tree_end = tree_end.then(Literal(alias).runs(self.cmd_remove_component))
        tree_end = tree_end.then(Literal('add').redirects(create_component_tree))
        tree_end = tree_end.then(Literal('blacklist').runs(self.cmd_set_component_blacklist))
        tree_end = tree_end.then(Literal('whitelist').runs(self.cmd_set_component_whitelist))
        # list stuff
        tree_end = tree_end.then(Literal('list').then(Literal('set').then(GreedyText('list').runs(
            self.cmd_overwrite_block_list))))
        tree_end = tree_end.then(Literal('set').then(Literal('list').then(GreedyText('list').runs(
            self.cmd_overwrite_block_list))))
        tree_end = tree_end.then(Literal('list').then(Literal('add').then(GreedyText('block_type').runs(
            self.cmd_add_block_type_to_list))))

        tree_head = Literal('component').then(Text('tracker_id').then(tree_end))
        root.then(tree_head)
        # endregion

        # region scoreboard subtree
        tree_end = Text('scoreboard_id').runs(self.cmd_show_scoreboard)
        tree_end = tree_end.then(Literal('add').then(Text('tracker_id').runs(self.cmd_scoreboard_add_tracker)
                                                     .then(Integer('weight').runs(self.cmd_scoreboard_add_tracker))))


        tree_head = Literal('scoreboard').then(tree_end)
        root.then(tree_head)
        # endregion

        self.server.register_command(root)


if __name__ == '__main__':
    print(1)