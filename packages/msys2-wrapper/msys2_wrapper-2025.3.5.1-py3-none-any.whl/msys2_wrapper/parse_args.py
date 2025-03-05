import sys
from msys2_wrapper.help import print_help
from msys2_wrapper.helper import remove_quote
from msys2_wrapper.launch_args import LaunchArgs
from pathlib import Path


def parse_args() -> LaunchArgs:
    largs = LaunchArgs()
    msystem = largs.msystem

    args = sys.argv[1:]

    arg0 = sys.argv[0]
    base = Path(arg0).name
    if base == "msys2c":
        largs.console = "defterm"

    def shift_args(times=1):
        nonlocal args
        for _ in range(times):
            args = args[1:]

    while len(args) > 0:
        arg = args[0]
        if arg in ("-help", "--help", "-?", "/?"):
            print_help()
            exit()

        if arg in ("-msys", "-msys2"):
            msystem = "msys"
            shift_args()
            continue
        if arg in ("-mingw32", "-mingw64", "-clang64", "-ucrt64", "-clangarm64"):
            msystem = arg[1:]
            shift_args()
            continue
        if arg == "-mingw":
            msystem = "mingw64"
            shift_args()
            continue
        if arg == "-shell":
            if len(args) == 1:
                print("Shell not specified for -shell parameter.", file=sys.stderr)
                exit(2)
            largs.shell = remove_quote(args[1])
            shift_args(2)  # two times
            continue

        if arg == "-where":
            if len(args) == 1:
                print(
                    "Working directory is not specified for -where parameter.",
                    file=sys.stderr,
                )
                exit(2)
            largs.working_directory = remove_quote(args[1])
            shift_args(2)
            continue

        if arg in ("-full-path", "-use-full-path"):
            largs.path_type = "inherit"
            shift_args()
            continue

        if arg == "-defterm":
            largs.console = "defterm"
            shift_args()
            continue

        if arg == "-conemu":
            largs.console = "conemu"
            shift_args()
            continue

        if arg == "-search":
            if len(args) == 1:
                print("Package not specified for -search parameter.", file=sys.stderr)
                exit(2)
            package = args[1]
            url = f"https://packages.msys2.org/search?t=pkg&q={package}"
            import webbrowser

            webbrowser.open(url)

            shift_args(2)
            continue
        break

    largs.msystem = msystem.upper()
    largs.shell_args.extend(args)
    return largs
