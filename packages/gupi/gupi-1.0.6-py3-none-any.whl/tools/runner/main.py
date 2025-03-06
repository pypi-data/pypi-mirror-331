import os
import importlib
from typing import List
from colorama import Fore
from gupi.errors import GupiBaseException
from gupi.custom_logger import getLogger
from gupi.error_handler import error_handler

from tools.analyser import _analyse

logger = getLogger("gupi")


@error_handler
def run(vendors: List[str]):
    pkg_info, orders = _analyse(vendors)
    for vendor in vendors:
        for pkg_name in orders[vendor]:
            pkg = pkg_info[vendor][pkg_name]
            main_mod = f'{vendor}.{pkg_name}.main'
            main_path = f'{vendor}/{pkg_name}/main.py'
            try:
                assert os.path.isfile(main_path)
                module_obj = importlib.import_module(main_mod)
                logger.info(f'Loaded module \'{pkg_name}\'')
            except AssertionError:
                pass
            except ImportError as e:
                raise GupiBaseException(
                    title=f'From module {Fore.CYAN}{pkg["name"]}{Fore.RESET}:',
                    message=e.msg + '.',
                    exc_info=(type(e), e, e.__traceback__)
                )

