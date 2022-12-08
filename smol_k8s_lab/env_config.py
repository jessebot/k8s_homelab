#!/usr/bin/env python3.11

from importlib.metadata import version as get_version
from getpass import getuser
from os import getenv, path, uname

from rich.console import Console
from rich.theme import Theme
from rich.prompt import Confirm
from rich.live import Live
from rich.table import Table
from sys import exit
import yaml
from .console_logging import print_panel


HOME_DIR = getenv("HOME")
USER = getuser()

# this is for rich text, to pretty print things
soft_theme = Theme({"info": "dim cornflower_blue",
                    "warn": "yellow on black",
                    "danger": "bold magenta"})
CONSOLE = Console(theme=soft_theme)

PWD = path.dirname(__file__)


def load_yaml(yaml_config_file=path.join(HOME_DIR,
                                         ".config/smol-k8s-lab/config.yaml")):
    """
    load config yaml files for smol-k8s-lab and return as dicts
    """
    if path.exists(yaml_config_file):
        with open(yaml_config_file, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    else:
        print(f"Config file does not exist: {yaml_config_file}")
        exit()


# pathing
PWD = path.dirname(__file__)

# version of smol-k8s-lab
VERSION = get_version('smol-k8s-lab')

# defaults
USR_CONFIG_FILE = load_yaml()

# env
SYSINFO = uname()
# this will be something like ('Darwin', 'x86_64')
OS = (SYSINFO.sysname, SYSINFO.machine)


def check_os_support(supported_os=('Linux', 'Darwin')):
    """
    verify we're on a supported OS and ask to quit if not.
    """
    if OS[0] not in supported_os:
        offical_supported_list = ", ".join(supported_os)
        msg = (f"[ohno]{OS[0]}[/ohno] isn't officially supported in {VERSION}."
               f" We have only tested the following: {offical_supported_list}")
        print_panel(msg, "⚠️  [warn]WARNING")

        quit_y = Confirm.ask("🌊 You're in uncharted waters. Wanna quit?")
        if quit_y:
            print_panel("That's probably safer. Have a safe day, friend.",
                        "Safety Award ☆ ")
            quit()
        else:
            print_panel("[red]Yeehaw, I guess.", "¯\\_(ツ)_/¯")
    else:
        print_panel("Operating System and Architechure [green]supported ♥",
                    "[cornflower_blue]Compatibility Check")


def generate_table() -> Table:
    """
    Make a new table.
    """
    table = Table()
    table.add_column("Parameter")
    table.add_column("Value")

    table.add_row("")
    return table


def create_new_config():
    """
    interactive create new config
    """

    with Live(generate_table(), refresh_per_second=4) as live:
        live.update(generate_table())

        return


def process_configs():
    """
    process the config in ~/.config/smol-k8s-lab/config.yaml if it exists,
    then process the cli dict, and fill in defaults for anything not explicitly
    defined. Returns full final config as dict for use in script.
    """

    if USR_CONFIG_FILE:
        print(f"🗂 ⚙️  user_config_file: \n{USR_CONFIG_FILE}\n")
    else:
        USR_CONFIG_FILE = create_new_config()

    return USR_CONFIG_FILE
