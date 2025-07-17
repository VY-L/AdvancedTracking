from typing import Optional

from mcdreforged.command.builder.common import CommandContext, ParseResult
from mcdreforged.command.builder.nodes.basic import Literal
from typing_extensions import Self


class MarkingLiteral(Literal):
    """
    A custom Literal node that can be used to mark a command node.
    This is useful for command nodes that are not intended to be executed directly,
    but rather to be used as a marker for other command nodes.
    """
    _mark: Optional[str] = None
    _mark_pos: Optional[str] = None
    def _on_visited(self, context: CommandContext, parsed_result: ParseResult):
        if self._mark is not None:
            context[self._mark_pos] = self._mark
    def set_mark(self, mark: str, key: str) -> Self:
        """
        Set a mark for this command node.
        :param mark: The mark to set.
        :return: This command node with the mark set.
        """
        self._mark_pos = key
        self._mark = mark
        return self