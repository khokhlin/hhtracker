import sys
from argparse import ArgumentParser
from hhtracker.hhtracker import run
from hhtracker import config


def parse_args():
    parser = ArgumentParser("hhtracker")
    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--region", type=int, default=config.api.moscow_code)
    parser.add_argument("--keywords", nargs="+", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    sys.exit(run(args.region, args.keywords, args.init_db))


if __name__ == "__main__":
    main()
