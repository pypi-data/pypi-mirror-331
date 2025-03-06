import os
import traceback
import functools

import gupi.common as common
from gupi.errors import GupiBaseException
from gupi.custom_logger import getLogger, log


def error_handler(fun=None, *, reraise=False):
    if fun is None:
        return lambda f: error_handler(f, reraise=reraise)

    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except GupiBaseException as e:
            tb = traceback.extract_tb(e.__traceback__)
            filename, lineno, func, text = tb[-1]

            filename = os.path.relpath(filename, common.REPO_PATH)
            filename = filename.split('.')[0].replace('/', '.')
            
            logger = getLogger(filename)
            log(logger.error, e.message, title=e.title, exc_info=e.exc_info)
            
            if reraise: raise

    return wrapper
