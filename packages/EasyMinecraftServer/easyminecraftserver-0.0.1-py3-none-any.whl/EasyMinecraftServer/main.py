import typer
import json
import os
import psutil
import requests

from pathvalidate import sanitize_filepath
from rich import print
from rich.prompt import Prompt, Confirm
from rich.markup import escape
from .data.version_list import versions
from .data.software_list import softwares
from pathlib import Path

app = typer.Typer()


@app.command()
def install():
    config = json.load(open(f"{conf_dir}/config.json", mode="r", encoding="utf-8"))
    setupmd_api = (
        f"https://jar.setup.md/download/{config['loader']}/{config['version']}/latest"
    )
    jardata = requests.get(setupmd_api)
    if jardata.status_code != 200:
        print("API Errored\n")
        raise typer.Abort()
    dir = Path(config["location"])
    dir.mkdir(parents=True, exist_ok=True)
    with open(f"{config['location']}/server.jar", mode="wb") as jarfile:
        jarfile.write(jardata.content)
    raise typer.Abort()


@app.command()
def configure():
    location: str = pick_location()
    version: str = pick_version()
    loader: str = pick_server()
    ram: int = detect_ram()
    optimized: bool = is_optimized()
    open_port: bool = should_open_port()

    config = {
        "location": location,
        "version": version,
        "loader": loader,
        "ram": ram,
        "optimized": optimized,
        "open_port": open_port,
    }
    with open(f"{conf_dir}/config.json", mode="w", encoding="utf-8") as conf_file:
        json.dump(config, conf_file)
    # conf_dir: str, location: str, version: str, loader: str, ram: int, optimized: bool, open_port: bool


def setup():  # Create a default directory for the config file
    system = os.name
    if system == "posix":
        homepath = os.getenv("HOME")
        directory = f"{homepath}/.config/easymcserver/"
        dir = Path(directory)
        dir.mkdir(parents=True, exist_ok=True)
        return directory
    elif system == "nt":
        homepath = os.getenv("HOMEPATH")
        directory = f"{homepath}\\easymcserver\\config"
        dir = Path(directory)
        dir.mkdir(parents=True, exist_ok=True)
        return directory


conf_dir: str = setup()


def pick_location():
    def define_default():
        system = os.name
        if system == "posix":
            homepath = os.getenv("HOME")
            directory = f"{homepath}/.local/share/easymcserver/"
            return directory
        if system == "nt":
            homepath = os.getenv("HOMEPATH")
            directory = f"{homepath}\\easymcserver\\server"
            return directory

    default = define_default()
    try:
        location = Prompt.ask(
            f"[yellow]Where[/yellow] would you like your server to be created at?\n[grey70](Default: {default}[/grey70]"
        )
    except KeyboardInterrupt:
        print("\n")
        raise typer.Abort()
    if location == "":
        location = default
    location = sanitize_filepath(
        file_path=location, platform="auto"
    )  # Sanitize File Path
    print(f"Selected [bold magenta]{escape(location)}[/bold magenta]")
    return location  # Return location as string


def pick_version():
    try:
        version = Prompt.ask(
            "[yellow]Which version[/yellow] would you like your server to be?\n[grey70](Default: latest)[/grey70]"
        )
    except KeyboardInterrupt:
        print("\n")
        raise typer.Abort()
    if (
        version not in versions and version != ""
    ):  # Exit if version isn't in the versions list or empty
        print(f'[bold red]Version "{escape(version)}" is not supported![/bold red]')
        raise typer.Abort()
    if version == "":  # Set Default for Empty Strings
        version = "latest"
    print(f"Selected [bold magenta]{escape(version)}[/bold magenta]")
    return version  # Return version as string


def pick_server():
    try:
        software = Prompt.ask(
            "[yellow]Which server software[/yellow] would you like your server to use?\n[grey70](Default: paper)[grey70]"
        ).lower()
    except KeyboardInterrupt:
        print("\n")
        raise typer.Abort()
    if software not in softwares and software != "":
        print(
            f"[red bold]Not Supported. List of available softwares:\n[/red bold][green bold]{softwares}[/green bold]"
        )
        raise typer.Abort()
    if software == "":
        software = "paper"
    print(f"Selected [bold magenta]{escape(software)}[/bold magenta]")
    return software  # Return software as string


def detect_ram():
    memory_info = psutil.virtual_memory().total
    total_ram = memory_info / (1024 * 1024)  # Bytes to Megabytes
    usable_ram = total_ram - 1024  # Removing 1 GB Ram for use by OS
    return usable_ram  # Return Megabytes as integer


def is_optimized():
    try:
        optimized = Confirm.ask(
            "Would you like your server to be [yellow]optimized[/yellow]?", default=True
        )
    except KeyboardInterrupt:
        print("\n")
        raise typer.Abort()
    return optimized  # Return true or false as boolean


def should_open_port():
    try:
        open_port = Confirm.ask(
            "Would you like the script to detect the firewall and open ports for you?",
            default=False,
        )
    except KeyboardInterrupt:
        print("\n")
        raise typer.Abort()
    return open_port  # Return true or false as boolean


if __name__ == "__main__":
    app()
