import argparse
from pathlib import Path

import common
from custom_logger import setVerbosity

parser = argparse.ArgumentParser()

def _load_args():
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser.add_argument("repo_path", type=str, default=".", help=\
        "Path to repository (default to current)."
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    analyse_prsr = subparsers.add_parser("analyse", help=\
        "Safe checking the current repository via info.json"
    )
    # fix_prsr = subparsers.add_parser("fix", help="Fix faults found by analyser's result")
    run_prsr = subparsers.add_parser("run", help="Run some module")

    args = parser.parse_args()
    return args

def main():
    args = _load_args()
    setVerbosity(args.verbose)
    common.REPO_PATH = str(Path(args.repo_path).resolve(True))

    with open("vendor.list", "r") as file:
        vendors = [
            vendor
            for vendor in file.readlines()
            if vendor
        ]

    if args.command == "analyse":
        from tools import analyser
        analyser.analyse(vendors)
    elif args.command == "run":
        from tools import runner
        runner.run(vendors)

if __name__ == "__main__":
    main()