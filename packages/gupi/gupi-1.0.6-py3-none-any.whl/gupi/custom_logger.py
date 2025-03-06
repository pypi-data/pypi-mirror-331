import logging

from functools import lru_cache
from colorama import Style, Fore, Back


_lf = f'{Back.LIGHTBLACK_EX}'
_rg = f'{Back.RESET}{Fore.RESET}'
lvlname = {
    'INFO':    f'     {_lf} INFO {_rg}',
    'DEBUG':   f'    {_lf} DEBUG {_rg}',
    'WARNING': f'  {_lf} WARNING {_rg}',
    'ERROR':   f'    {_lf} ERROR {_rg}',
}

class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_format = (
            f'{lvlname[record.levelname]}  '
            f'{Fore.CYAN}'
            '{name} \033[1;37m| '
            f'{Style.RESET_ALL}'
        )

        if hasattr(record, 'title'):
            log_format += '{title}\n' + ' ' * (13 + len(record.name)) + ' | '
        log_format += '{message}'
        
        formatter = logging.Formatter(log_format, style='{')
        return formatter.format(record)

def log(f, message: str, *, title: str = None, exc_info=None):
    '''
    A custom log function tailored to use with title.
    >>> log(logger.info, 'Title', 'Message')
    '''
    if title is None:
        f(message, exc_info=exc_info)
    else:
        f(message, exc_info=exc_info, extra={'title': title})

@lru_cache(maxsize=1)
def _getHandler():
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    return handler

_verbose_lvl = logging.INFO
def setVerbosity(_debug: bool):
    global _verbose_lvl
    if _debug:
        _verbose_lvl = logging.DEBUG

def getLogger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(_verbose_lvl)
    logger.addHandler(_getHandler())
    return logger
