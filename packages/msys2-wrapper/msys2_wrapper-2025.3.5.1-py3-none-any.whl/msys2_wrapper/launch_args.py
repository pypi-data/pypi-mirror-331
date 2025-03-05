import os
import sys

from msys2_wrapper.find_msys2 import find_msys2
from pathlib import Path


class LaunchArgs:
    def __init__(self):
        self.base = find_msys2()

        self.WD = self.base
        if not Path(self.WD).joinpath("msys-2.0.dll").exists():
            self.WD = self.WD / "usr/bin"

        self.shell = "bash"
        self.msystem = "msys"
        self.shell_args = ["-l"]
        self.working_directory = os.getcwd()
        self.path_type = ""
        self.console = "mintty.exe"

    def get_title_and_icon(largs) -> (str, str):
        title = "MSYS2 MSYS"
        icon = "msys2.ico"
        if largs.msystem == "MINGW32":
            title = "MinGW x32"
            icon = "mingw32.ico"
        elif largs.msystem == "MINGW64":
            title = "MinGW x64"
            icon = "mingw64.ico"
        elif largs.msystem == "UCRT64":
            title = "MinGW UCRT x64"
            icon = "ucrt64.ico"
        elif largs.msystem == "CLANG64":
            title = "MinGW Clang x64"
            icon = "clang64.ico"
        elif largs.msystem == "CLANGARM64":
            title = "MinGW Clang ARM64"
            icon = "clangarm64.ico"

        return title, icon

    def get_shell_exe(self):
        shell_exe = self.base / f"usr/bin/{self.shell}.exe"
        if not shell_exe.exists():
            print(f"shell `{self.shell}` not exist", file=sys.stderr)
            exit(-1)
        return str(shell_exe).replace("\\", "/")

    def get_shell_env(largs) -> dict[str, str]:
        env = {"CHERE_INVOKING": "1", "MSYSTEM": largs.msystem}
        if largs.path_type != "":
            env["MSYS2_PATH_TYPE"] = largs.path_type

        # insert default env
        for k in os.environ.keys():
            if k not in env:
                env[k] = os.environ.get(k, "")

        return env
