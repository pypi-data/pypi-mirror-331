from msys2_wrapper.parse_args import LaunchArgs
import subprocess
import os
import contextlib
from pathlib import Path


@contextlib.contextmanager
def CD(d):
    cwd = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(cwd)


def str_path(p: Path) -> str:
    return str(p).replace("\\", "/")


def mintty(largs: LaunchArgs, env):
    title, icon = largs.get_title_and_icon()
    try:
        with CD(largs.working_directory):
            subprocess.call(
                [
                    str_path(largs.WD.joinpath("mintty")),
                    "-i",
                    "/" + icon,
                    "-t",
                    title,
                    "/usr/bin/" + largs.shell,
                    *largs.shell_args,
                ],
                env=env,
            )
    except KeyboardInterrupt:
        exit()


def start_shell(largs: LaunchArgs):
    env = largs.get_shell_env()

    if largs.console == "mintty.exe":
        mintty(largs, env)
    if largs.console == "defterm":
        shell_exe = largs.get_shell_exe()
        shell_args = [shell_exe, *largs.shell_args]
        # print(" ".join(shell_args))
        try:
            with CD(largs.working_directory):
                subprocess.call(shell_args, env=env)
        except KeyboardInterrupt:
            exit()
