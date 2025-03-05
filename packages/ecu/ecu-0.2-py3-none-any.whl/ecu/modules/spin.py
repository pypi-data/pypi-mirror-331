import time
import enum
import typing
import threading
import contextlib
from .. import utils

class Spinner(enum.Enum):
    ASCII = '|/-\\'
    BRAILLE = '⣾⣽⣻⢿⡿⣟⣯⣷'
    DOTS = ('','·','··','···')
    SCROLL = ('.  ','.. ','...',' ..','  .','   ')

@contextlib.contextmanager
@utils.ensure('?25h', '0m')
def spin(
    message: str,
    spinner: Spinner | str = Spinner.BRAILLE,
    delay: float = 0.2,
    color: int | str = 36,
) -> typing.Generator[None, None, None]:
    '''
    A context manager for displaying a long task.

    :param message: Wait message.
    :param spinner: Custom spinner.
    :param frequency: Animation delay.
    :param color: Spinner color.
    '''

    if isinstance(spinner, Spinner):
        spinner = spinner.value

    stop = threading.Event()

    def _run() -> None:
        i = 0
        while not stop.is_set():
            print(f'\x1b[?25l\x1b[2K\x1b[0m{message} \x1b[{color}m{spinner[i % len(spinner)]}\x1b[0m', end = '\r')
            i += 1
            time.sleep(delay)
        
        print('\x1b[?25h')
    
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    try:
        yield
    finally:
        stop.set()
        thread.join()

# EOF