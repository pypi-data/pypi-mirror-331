from colorama import Fore

REPO_PATH = None

def hili(txt: str, clr: str = Fore.CYAN):
    return clr + txt + Fore.RESET
