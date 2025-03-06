import os
import re
import json

from colorama import Fore, Style
from typing import List, Tuple, Optional

import gupi.common as common
from gupi.errors import *
from gupi.error_handler import error_handler
from gupi.custom_logger import getLogger, log

logger = getLogger("gupi")

REQUIRED_FIELDS = {'name', 'version'}
ACCEPTED_FIELDS = {'name', 'dependencies', 'disabled', 'description', 'version'}


disableds = set()
pkg_info = {}
_processed = set()
_in_process = []


def parse_dependency(s):
    pattern = r"([a-zA-Z0-9_.-]+)([<>=!~]+)?([0-9.*]+)?"
    match = re.match(pattern, s)
    
    if match:
        name = match.group(1)
        type_ = match.group(2) if match.group(2) else None
        version = match.group(3) if match.group(3) else None
        return [name, type_, version]
    return [s, None, None]


def examine_dependency(
    vendor: str,
    org_pkg: dict,
    dependency: Tuple[str, Optional[str], Optional[str]]
):
    dep_pkg: dict = pkg_info[vendor][dependency[0]]

    if dependency[1] == '==' and dep_pkg.get('version') != dependency[2] \
    or dependency[1] == '>=' and dep_pkg.get('version') <  dependency[2] \
    or dependency[1] == '<=' and dep_pkg.get('version') >  dependency[2] \
    or dependency[1] == '>'  and dep_pkg.get('version') <= dependency[2] \
    or dependency[1] == '<'  and dep_pkg.get('version') >= dependency[2]:
        raise DepVersionException(org_pkg, dep_pkg, dependency)

    return dep_pkg


def topo_sort(vendor: str, pkg: dict, result: List[str]):
    _in_process.append(pkg['name'])

    for dependency in pkg['dependencies']:
        try:
            _depend = examine_dependency(vendor, pkg, dependency)
        except KeyError:
            _is_disabled = dependency[0] in disableds
            reason = "disabled" if _is_disabled else "non-existing"
            raise DepMissingException(pkg, dependency, reason)

        if _depend['name'] in _in_process:
            raise DepCycleException(_depend['name'], [p for p in _in_process] + [_depend['name']])

        if _depend['name'] not in _processed:
            topo_sort(vendor, _depend, result)
    
    _processed.add(pkg['name'])
    assert _in_process.pop() == pkg['name']

    result.append(pkg['name'])
    logger.info('Analysed %s', pkg['name'])


def _analyse(vendors: List[str]):
    """
    Returns:
        `(pkg_info, orders)`

        `pkg_info` and `orders` are both `dict[vendor_name, ...]`
    """
    orders = {}

    for vendor in vendors:
        logger.info(f'{f" {vendor.upper()} PACKAGES ":=^25}')

        pkg_info[vendor] = {}
        vendor_path = os.path.join(common.REPO_PATH, vendor)
        if not os.path.isdir(vendor_path):
            raise VendorNotDirectory(vendor_path)

        for pkg_name in os.listdir(vendor_path):
            pkg_path = os.path.join(vendor_path, pkg_name)
            if os.path.isfile(pkg_path): continue
            if pkg_name == '__pycache__': continue

            if '.' in pkg_name:
                log(logger.warning,
                    title=f'Package {Fore.CYAN}{pkg_name}{Fore.RESET}',
                    message=(
                        'contain a dot (.) character in its name '
                        f'({Fore.RED}skipped{Fore.RESET})'
                    )
                )
                continue

            pkg_info_path = os.path.join(pkg_path, 'info.json')

            try:
                with open(pkg_info_path, 'r', encoding='utf-8') as file:
                    pkg = json.load(file)
                    for field in REQUIRED_FIELDS:
                        if field not in pkg.keys():
                            raise MissingInfoField(pkg_name, field)
                    invalid_fields = [
                        field for field in pkg.keys()
                        if field not in ACCEPTED_FIELDS
                        and not field.startswith('_')
                    ]
                    if invalid_fields:
                        raise InvalidInfoField(pkg_name, invalid_fields[0])

                    assert pkg['name'] == pkg_name
                    if pkg.get('disabled', False):
                        disableds.add(pkg_name)
                        continue
                    pkg_info[vendor][pkg_name] = pkg
                
                pkg['dependencies'] = [
                    parse_dependency(dep)
                    for dep in pkg.get('dependencies', [])
                ]

            except FileNotFoundError as e:
                assert e.filename == pkg_info_path
                log(logger.warning,
                    title=f'Module {Fore.CYAN}{pkg_name}{Fore.RESET}',
                    message=(
                        'doesn\'t contain an info.json file '
                        f'({Fore.RED}skipped{Fore.RESET})'
                    )
                )
                continue

            except json.decoder.JSONDecodeError:
                raise InvalidInfoJsonSyntax(pkg_name)


        if pkg_info[vendor] == {}:
            logger.info(f'{Style.DIM}Nothing to load.{Style.RESET_ALL}')
            continue
        
        order = []
        for pkg in pkg_info[vendor].values():
            if pkg['name'] not in _processed:
                topo_sort(vendor, pkg, order)

        _processed.clear()
        _in_process.clear()

        orders[vendor] = order

    return pkg_info, orders


@error_handler
def analyse(vendors: List[str]):
    """
    Same as `_analyse`, but with the `error_handler` decorator.

    Returns:
        `(pkg_info, orders)`

        `pkg_info` and `orders` are both `dict[vendor_name, ...]`
    """
    return _analyse(vendors)
