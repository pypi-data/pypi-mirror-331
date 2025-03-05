from msys2_wrapper.parse_args import LaunchArgs
import subprocess
import os
import contextlib
from pathlib import Path
import sys


@contextlib.contextmanager
def CD(d):
    cwd = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(cwd)


def str_path(p: Path) -> str:
    return str(p).replace("\\", "/")


# conemucommand, msyscon, exitcode
def detect_conemu(env: dict[str, str]) -> (str, str, int):
    conemucommand = ""
    msyscon = ""
    if "ConEmuCommand" in env.keys():
        if Path(env["ConEmuCommand"]).joinpath("ConEmu64.exe").exists():
            conemucommand = os.path.join(env["ConEmuCommand"], "ConEmu64.exe")
            msyscon = "conemu64.exe"
            return conemucommand, msyscon, 0
        elif Path(env["ConEmuCommand"]).joinpath("ConEmu.exe").exists():
            conemucommand = os.path.join(env["ConEmuCommand"], "ConEmu.exe")
            msyscon = "conemu.exe"
            return conemucommand, msyscon, 0

    ret = subprocess.run("ConEmu64.exe /Exit 2>nul", shell=True, check=False)
    if ret.returncode == 0:
        conemucommand = "ConEmu64.exe"
        msyscon = "conemu64.exe"
        return conemucommand, msyscon, 0
    ret = subprocess.run("ConEmu.exe /Exit 2>nul", shell=True, check=False)
    if ret.returncode == 0:
        conemucommand = "ConEmu.exe"
        msyscon = "conemu.exe"
        return conemucommand, msyscon, 0

    out = subprocess.getoutput(
        r'reg.exe QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\ConEmu64.exe"'
    )
    if "REG_SZ" in out:
        conemucommand = out.split("REG_SZ")[1].strip()
        msyscon = "conemu64.exe"
        return conemucommand, msyscon, 0

    out = subprocess.getoutput(
        r'reg.exe QUERY "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\ConEmu.exe"'
    )
    if "REG_SZ" in out:
        conemucommand = out.split("REG_SZ")[1].strip()
        msyscon = "conemu.exe"
        return conemucommand, msyscon, 0

    return "", "", 2


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


def conemu(env, largs: LaunchArgs):
    (coneucommand, msyscon, retcode) = detect_conemu(env)
    if retcode != 0:
        print("ConEmu not found. Exiting.", file=sys.stderr)
        exit(1)

    title, icon = largs.get_title_and_icon()
    try:
        with CD(largs.working_directory):
            subprocess.call(
                [
                    coneucommand,
                    "/Here",
                    "/Icon",
                    str_path(largs.WD.parent.parent.joinpath(icon)),
                    "/cmd",
                    str_path(largs.WD.joinpath(largs.shell)),
                    # "-l",
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
    if largs.console == "conemu":
        conemu(env, largs)
    if largs.console == "defterm":
        env["MSYSCON"] = ""
        shell_exe = largs.get_shell_exe()
        shell_args = [shell_exe, *largs.shell_args]
        # print(" ".join(shell_args))
        try:
            with CD(largs.working_directory):
                subprocess.call(shell_args, env=env)
        except KeyboardInterrupt:
            exit()
