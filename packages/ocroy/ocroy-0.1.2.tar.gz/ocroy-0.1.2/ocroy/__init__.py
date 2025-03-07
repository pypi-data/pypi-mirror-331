from ocroy.parser import parse_args

__version__ = "0.1.2"


def main() -> None:
    args = parse_args()
    print(args.func(args))
