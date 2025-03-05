from pathlib import Path
import os
import logging
import functools
from msys2_wrapper.helper import remove_quote


def check_ext(s: Path) -> bool:
    if s.suffix == ".cmd":
        return True
    return False


# config_base, config_file, retcode
def detect_config() -> (str, str, int):
    config_file = Path.home().joinpath(".config").joinpath("msys2_wrapper.ini")
    if not config_file.exists():
        return "", "", -1
    import configparser

    config = configparser.ConfigParser()
    config.read(config_file)

    if "default" not in config or "base" not in config["default"]:
        print(f"""incorrect config file {config_file}.
please replace it with the following structure,
with the "D:/msys64" replaced by your msys2 installation path:
`
[default]
base = "D:/msys64"
`""")
        exit(-1)
    p = config["default"]["base"]
    p = remove_quote(p)
    return p, config_file, 0


@functools.cache
def find_msys2() -> Path:
    config_base, config_file, retcode = detect_config()
    if retcode == 0:
        p = Path(config_base)
        if not p.exists():
            print(f"configed base {p} (in {config_file}) was not found")
            exit(-1)
        if not p.joinpath("msys2_shell.cmd").exists():
            print(
                f"configed base {p} (in {config_file}) was not an valid msys2 installation ({p.joinpath('msys2_shell.cmd')} was not found)"
            )
        return p

    p = os.environ["PATH"]
    results: list[Path] = []
    for d in p.split(";"):
        pd = Path(d)
        if not (pd.exists() and pd.is_dir()):
            continue
        for i in os.listdir(d):
            pi = Path(d) / i
            if not pi.is_file():
                continue
            if pi.stem == "msys2":
                results.append(pi)

    if len(results) == 0:
        for i in [chr(i + ord("C")) for i in range(26 - 2)]:
            p = f"{i}:/msys64"
            p2 = Path(p).joinpath("msys2_shell.cmd")
            if p2.exists():
                results.append(p2)
                break

    results = list(filter(check_ext, results))
    if len(results) == 0:
        logging.critical("msys2 not found")
        exit(-1)

    p1 = results[0].parent

    # check scoop
    if "scoop/shims" in str(p1).replace("\\", "/"):
        real_loc = Path.home() / "scoop/apps/msys2/current/msys2_shell.cmd"
        p1 = real_loc.parent

    return p1
