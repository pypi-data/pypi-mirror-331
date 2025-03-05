import importlib
import platform
import subprocess
import sys
from pathlib import Path


def get_path() -> Path:
    plat = ""
    machine = ""
    match sys.platform:
        case "linux":
            plat = "linux"
        case "darwin":
            plat = "darwin"
        case "win32":
            plat = "win32"
        case _:
            raise ValueError(f"Unsupported platform: {sys.platform}")
    match platform.machine().lower():
        case "x86_64" | "amd64":
            machine = "x64"
        case "arm64" | "aarch64":
            machine = "arm64"
        case _:
            raise ValueError(f"Unsupported architecture: {platform.machine()}")
    mod = f"changesets_{plat}_{machine}"
    module = importlib.import_module(mod)
    return module.get_path()


def run() -> None:
    path = get_path()
    path.chmod(0o774)
    try:
        subprocess.run([path, *sys.argv[1:]], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    run()
