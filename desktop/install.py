#!/usr/bin/env python3
"""Install the Valley of Tears launcher for the current Linux desktop user."""

import os
from pathlib import Path
import shutil
import subprocess


def exec_argument(value):
    # Desktop entries unescape strings before parsing the quoted Exec arguments.
    quoted = "".join("\\" + char if char in '\\"`$' else char for char in str(value))
    return '"' + quoted.replace("\\", "\\\\").replace("%", "%%") + '"'


def entry_value(value):
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")


def main():
    repository = Path(__file__).resolve().parent.parent
    project = repository / "godot"
    godot = shutil.which("godot") or shutil.which("godot4")
    if not godot:
        raise SystemExit("Install Godot 4 before installing this launcher.")
    if not (project / "project.godot").is_file():
        raise SystemExit("The Godot project is missing from this checkout.")

    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    applications = data_home / "applications"
    icon = data_home / "icons/hicolor/256x256/apps/valley-of-tears.png"
    applications.mkdir(parents=True, exist_ok=True)
    icon.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(repository / "desktop/valley-of-tears.png", icon)

    command = f"{exec_argument(godot)} --path {exec_argument(project)} --disable-vsync"
    launcher = applications / "org.sd5913.ValleyOfTears.desktop"
    launcher.write_text(
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Valley of Tears\n"
        "GenericName=3D Valley Explorer\n"
        "Comment=Explore The Weeping Wardens with WASD and a flying camera\n"
        f"Exec={command}\n"
        f"TryExec={entry_value(godot)}\n"
        f"Path={entry_value(project)}\n"
        f"Icon={entry_value(icon)}\n"
        "Terminal=false\n"
        "StartupNotify=false\n"
        "StartupWMClass=Valley of Tears\n"
        "Categories=Game;AdventureGame;\n"
        "Keywords=Valley;Tears;Godot;Wardens;Explore;\n"
        "Actions=Editor;\n"
        "\n[Desktop Action Editor]\n"
        "Name=Edit in Godot\n"
        f"Exec={command} --editor\n",
        encoding="utf-8",
    )
    launcher.chmod(0o644)
    if shutil.which("update-desktop-database"):
        subprocess.run(["update-desktop-database", str(applications)], check=True)
    print(f"Installed {launcher}")
    print("Search for Valley of Tears in the application launcher.")


if __name__ == "__main__":
    main()
