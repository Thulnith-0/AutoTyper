from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
APP_NAME = "AutoTyper"
DATA_SEPARATOR = ";" if sys.platform == "win32" else ":"


def build_command() -> list[str]:
    icon_path: Path | None = ASSETS_DIR / "icon.ico"
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        f"--name={APP_NAME}",
        f"--add-data={ASSETS_DIR}{DATA_SEPARATOR}assets",
        "--collect-all=pyautogui",
        "--collect-all=pymsgbox",
        "--collect-all=pyscreeze",
        "--collect-all=pytweening",
        "--collect-all=mouseinfo",
    ]

    if sys.platform == "darwin":
        mac_icon = ASSETS_DIR / "icon.icns"
        if mac_icon.exists():
            icon_path = mac_icon
        else:
            icon_path = None
        command.append("--osx-bundle-identifier=com.thulnith.autotyper")

    if icon_path is not None and icon_path.exists():
        command.append(f"--icon={icon_path}")

    command.append(str(ROOT / "autotyper.py"))
    return command


def clean_build_outputs() -> None:
    for path in (DIST_DIR, BUILD_DIR):
        if path.exists():
            shutil.rmtree(path)


def ensure_pyinstaller_installed() -> bool:
    if importlib.util.find_spec("PyInstaller") is not None:
        return True

    print("PyInstaller is not installed in the active Python environment.")
    print("Install it with: pip install pyinstaller")
    return False


def main() -> int:
    if not ensure_pyinstaller_installed():
        return 1

    clean_build_outputs()
    command = build_command()
    print("Running:", " ".join(str(part) for part in command))
    subprocess.run(command, cwd=ROOT, check=True)

    if sys.platform == "darwin":
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if app_path.exists():
            print(f"Built macOS bundle: {app_path}")
            return 0

    if sys.platform == "win32":
        exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
        if exe_path.exists():
            print(f"Built Windows executable: {exe_path}")
            return 0

    print(f"Build completed. Check {DIST_DIR} for output files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
