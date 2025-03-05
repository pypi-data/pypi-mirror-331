import typing
import readchar
from .. import utils

@utils.ensure('?25h', '0m')
def select(
    prompt: str,
    choices: typing.Iterable,
    max: int | None = 1,
    size: int | None = None,
    hover: int | str = 36
) -> list | typing.Any:
    '''
    A prompt for selecting item(s) in a list.

    :param prompt: Prompt to display before the menu.
    :param choices: Iterable of choices.
    :param max: Max amount of choices. Set to null for infinite.
    :param size: Display length of the menu. Set to null to display entire menu.
    :param hover: ANSI code to apply when hovering.

    :return: List of choices, or the choice directly if `max` is set to 1.
    '''

    row = 0
    scroll = 0
    sel: list[int] = []
    choices = list(choices) # Convenient for passing iterator directly
    size = size or len(choices)

    print(prompt)
    
    while 1:
        for choice_index, choice in enumerate(choices[scroll:scroll + size]):
            i = scroll + choice_index
            print(f'\x1b[?25l\x1b[0m\x1b[2K{"-+"[i in sel]}\x1b[{hover if i == row else 0}m {choice}\x1b[0m')
        
        print(f'\x1b[{size}A', end = '')
        key = readchar.readkey()

        # Move cursor up
        if key == readchar.key.UP:
            if row > 0: row -= 1
            if row < scroll: scroll -= 1

        # Move cursor down
        if key == readchar.key.DOWN:
            if row < len(choices) - 1: row += 1
            if row >= scroll + size: scroll += 1
        
        # Toggle line
        if key == readchar.key.SPACE and max != 1:
            if row in sel:
                sel.remove(row)
            
            elif len(sel) < max or not max:
                sel.append(row)
        
        # Confirm or direct select
        if key == readchar.key.ENTER:
            if max == 1: sel = [row]
            break
    
    sel.sort()
    result = [choices[i] for i in sel]
    return result if max != 1 else result[0]

# EOF