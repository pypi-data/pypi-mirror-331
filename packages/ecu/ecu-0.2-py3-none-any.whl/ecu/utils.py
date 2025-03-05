import typing
import contextlib

def ensure(*codes: str) -> typing.ContextManager:
    '''
    Ensures to cleanup after a function exit.
    '''

    cleanup = ''.join('\x1b[' + code for code in codes)

    def decorator(func: typing.Callable):
        def wrapper(*args, **kwargs):
            try:
                print('\x1b7', end = '')
                return func(*args, **kwargs)
            
            finally:
                # Cleanup
                print('\x1b8\x1b[J' + cleanup, end = '')
        
        return wrapper
    
    return decorator

# EOF