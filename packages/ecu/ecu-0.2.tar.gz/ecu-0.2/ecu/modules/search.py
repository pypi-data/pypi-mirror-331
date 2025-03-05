import typing
import readchar
from .. import utils

@utils.ensure('?25h', '0m')
def search(
    prompt: str,
    source: typing.Callable[[str], typing.Iterable],
    
    delay: tuple[int, int | float] = None,

    size: int | None = None,
    hover: int | str = 36
) -> list | typing.Any:
    '''
    A prompt for searching items. The `source` callback is responsible for
    accessing search results.
    You can also use `NotImplemented` to search in an iterable instead.

    :param prompt: Prompt to display before the menu.
    :param source: Callback that returns search results.
    
    :param delay: Delay between

    :param size: Display length of the menu. Set to null to display entire menu.
    :param hover: ANSI code to apply when hovering.

    :return: The selected item.
    '''

    raise NotImplementedError()

# EOF