#!/usr/bin/env python3
"""
Install or uninstall the conky-thinkpad setup:
  - conky-all package (apt)
  - thinkpad.conf -> ~/.config/conky/thinkpad.conf
  - conky.service  -> ~/.config/systemd/user/conky.service
"""

import argparse
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

CONF_SRC = SCRIPT_DIR / "thinkpad.conf"
SERVICE_SRC = SCRIPT_DIR / "conky.service"

CONF_DEST = Path.home() / ".config" / "conky" / "thinkpad.conf"
SERVICE_DEST = Path.home() / ".config" / "systemd" / "user" / "conky.service"

SERVICE_NAME = "conky.service"


def log(msg: str) -> None:
    """Print an indented informational message."""
    print(f"  {msg}")


def run(cmd: list[str], dry_run: bool, check: bool = True) -> None:
    """Print and optionally execute a shell command, skipping execution in dry-run mode."""
    log(f"$ {' '.join(cmd)}")
    if not dry_run:
        subprocess.run(cmd, check=check)


def install(dry_run: bool) -> None:
    """Install conky-all, deploy the config file, and enable the systemd user service."""
    print("==> Installing conky-all via apt")
    run(["sudo", "apt-get", "install", "-y", "conky-all"], dry_run=dry_run)

    print(f"==> Copying thinkpad.conf to {CONF_DEST}")
    if not dry_run:
        CONF_DEST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CONF_SRC, CONF_DEST)
    else:
        log(f"mkdir -p {CONF_DEST.parent}")
        log(f"cp {CONF_SRC} {CONF_DEST}")

    print(f"==> Installing systemd user service to {SERVICE_DEST}")
    if not dry_run:
        SERVICE_DEST.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SERVICE_SRC, SERVICE_DEST)
    else:
        log(f"mkdir -p {SERVICE_DEST.parent}")
        log(f"cp {SERVICE_SRC} {SERVICE_DEST}")

    print("==> Enabling and starting conky.service")
    run(["systemctl", "--user", "daemon-reload"], dry_run=dry_run)
    run(["systemctl", "--user", "enable", "--now", SERVICE_NAME], dry_run=dry_run)

    print("Done. Conky is running as a user service.")


def uninstall(dry_run: bool) -> None:
    """Stop and disable the systemd user service, remove config files, and uninstall conky-all."""
    print("==> Stopping and disabling conky.service")
    run(
        ["systemctl", "--user", "disable", "--now", SERVICE_NAME],
        dry_run=dry_run,
        check=False,
    )
    run(["systemctl", "--user", "daemon-reload"], dry_run=dry_run)

    print(f"==> Removing {SERVICE_DEST}")
    if not dry_run:
        SERVICE_DEST.unlink(missing_ok=True)
    else:
        log(f"rm -f {SERVICE_DEST}")

    print(f"==> Removing {CONF_DEST}")
    if not dry_run:
        CONF_DEST.unlink(missing_ok=True)
    else:
        log(f"rm -f {CONF_DEST}")

    print("==> Removing conky-all via apt")
    run(["sudo", "apt-get", "remove", "-y", "conky-all"], dry_run=dry_run)
    run(["sudo", "apt-get", "autoremove", "-y"], dry_run=dry_run)

    print("Done. Conky has been uninstalled.")


def main() -> None:
    """Parse command-line arguments and dispatch to install or uninstall."""
    parser = argparse.ArgumentParser(
        description="Install or uninstall the conky-thinkpad setup on Ubuntu."
    )
    parser.add_argument(
        "action",
        choices=["install", "uninstall"],
        help="Action to perform.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making any changes.",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("[DRY RUN] No changes will be made.\n")

    if args.action == "install":
        install(dry_run=args.dry_run)
    else:
        uninstall(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
