from msys2_wrapper.parse_args import parse_args
from msys2_wrapper.start_shell import start_shell


def main():
    largs = parse_args()
    start_shell(largs)


if __name__ == "__main__":
    main()
