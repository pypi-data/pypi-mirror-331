from colorama import Fore
from typing import Tuple, List, Optional

from gupi.common import hili


class GupiBaseException(Exception):
    def __init__(
        self,
        message: str,
        title: Optional[str] = None,
        exc_info = None,
        hint: Optional[str] = None
    ):
        self.message = message
        self.hint = hint
        self.title = title
        self.exc_info = exc_info
        super().__init__(message)

class DepVersionException(GupiBaseException):
    def __init__(self, org_pkg: dict, dep_pkg: dict, dependency: Tuple[str]):
        super().__init__(
            title=f'From package {Fore.CYAN}{org_pkg["name"]}{Fore.RESET}:',
            message=f"Package {hili(dep_pkg['name'])} "
            f"(v{dep_pkg.get('version')}) doesn't match with "
            f'required ({dependency[1]}{dependency[2]}).'
        )

class DepMissingException(GupiBaseException):
    def __init__(self, pkg: dict, dependency: Tuple[str], reason: str):
        self.reason = reason
        super().__init__(
            title=f'Package {hili(pkg["name"])}',
            message=f'depends on a {reason} package {hili(dependency[0])}.'
        )

class DepCycleException(GupiBaseException):
    def __init__(self, pkg_name: str, traceback: List[str]):
        self.pkg_name = pkg_name
        self.traceback = traceback
        super().__init__(
            title=f'Package {hili(pkg_name)}',
            message=(
                'creates a dependency cycle while trying to load it.\n'
                f'Traceback: {" -> ".join(traceback)}'
            )
        )

class VendorNotDirectory(GupiBaseException):
    def __init__(self, vendor: str):
        super().__init__(
            f'{hili(vendor)} is not a directory!',
            hint=(
                f'This issue usually occurs if {hili(vendor)}'
                'neither exists or presents as a folder in '
                'this repository path.'
            )
        )

class InvalidInfoJsonSyntax(GupiBaseException):
    def __init__(self, pkg_name: str):
        super().__init__(
            title=f'Package {hili(pkg_name)}',
            message='has a syntax-invalid info.json file'
        )

class InvalidInfoField(GupiBaseException):
    def __init__(self, pkg_name: str, invalid_field: str):
        self.field = invalid_field
        super().__init__(
            title=f'Package {hili(pkg_name)}',
            message=(
                f"has an invalid field '{self.field}'"
                ' in its info.json file.'
            ),
            hint=(
                'Remove this field manually or check if '
                "there's any typo in it."
            )
        )

class MissingInfoField(GupiBaseException):
    def __init__(self, pkg_name: str, missing_field: str):
        self.field = missing_field
        super().__init__(
            title=f'Package {hili(pkg_name)}',
            message=f"is missing a required field: '{self.field}'"
        )
