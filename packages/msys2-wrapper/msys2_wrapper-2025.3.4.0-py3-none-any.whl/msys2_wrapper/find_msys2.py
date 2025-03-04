from pathlib import Path
import os
import logging
import functools


def check_ext(s: Path) -> bool:
    if s.suffix == ".cmd":
        return True
    return False


@functools.cache
def find_msys2() -> Path:
    p = os.environ["PATH"]
    results = []
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
    results = list(filter(check_ext, results))
    if len(results) == 0:
        logging.critical("msys2 not found")
        exit(-1)
    p1 = results[0]
    real_loc = p1.parent
    if "scoop/shims" in str(p1).replace("\\", "/"):
        real_loc = Path.home() / "scoop/apps/msys2/current/msys2_shell.cmd"
    return real_loc.parent
