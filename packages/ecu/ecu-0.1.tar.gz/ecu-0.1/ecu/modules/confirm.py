import readchar
from .. import utils

@utils.hide_cursor()
def confirm(
    prompt: str,
    confirm: str = 'Yes',
    refute: str = 'No',
    default: bool = True,
    throw: bool = False,
    hover: int = 106
) -> bool:
    '''
    A prompt for confirming an option.

    :param prompt: Prompt message.
    :param confirm: Confirmation button content.
    :param refute: Refute button content.
    :param throw: Whether to raise an error if confirm fails.
    
    :return: The confirmation result.
    '''

    result = default
    style = [0, hover]
    
    while 1:
        style.sort(reverse = result)
        print(
            f'\x1b[0m{prompt} '
            f'\x1b[{style[0]}m {confirm} '
            f'\x1b[0m\x1b[{style[1]}m {refute} \x1b[0m',
            end = '\r'
        )

        key = readchar.readkey()

        if key == readchar.key.LEFT and not result: result = True
        if key == readchar.key.RIGHT and result: result = False
        if key == readchar.key.ENTER: break
    
    print()
    if throw and not result:
        pass # TODO raise
    
    return result

# EOF