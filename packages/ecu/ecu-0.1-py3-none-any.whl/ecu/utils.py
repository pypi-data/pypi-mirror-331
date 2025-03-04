import contextlib

@contextlib.contextmanager
def hide_cursor() -> object:
    '''
    Hide cursor while a function is running.
    '''

    try:
        yield print('\x1b[?25l', end = '')
    
    finally:
        print('\x1b[?25h', end = '')

# EOF