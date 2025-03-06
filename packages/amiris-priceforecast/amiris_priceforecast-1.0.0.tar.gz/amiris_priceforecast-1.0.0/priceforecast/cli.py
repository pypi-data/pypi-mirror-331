# SPDX-FileCopyrightText: 2025 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

from priceforecast.logs import LogLevels
from priceforecast.models.registry import Models

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_LOG_COMMUNICATION = False

PRICEFORECAST_PARSER = (
    "Command-line interface to AMIRIS-PriceForecast - an extension to the agent-based electricity market model AMIRIS"
)
PRICEFORECAST_LOG_FILE_HELP = "Provide logging file (default: None)"
PRICEFORECAST_LOG_LEVEL_HELP = f"Choose logging level (default: {LogLevels.ERROR.name})"
PRICEFORECAST_COMMAND_HELP = "Choose one of the following commands:"

RUN_HELP = "Starts AMIRIS-PriceForecast main runner"
RUN_HOST_HELP = f"Provide host (default: {DEFAULT_HOST})"
RUN_PORT_HELP = f"Provide port (default: {DEFAULT_PORT})"
RUN_MODEL_HELP = f"Provide your model from available models '{Models}'"
RUN_CONFIG_PATH_HELP = "Provide path to your model config. Not necessary for naive models."
RUN_LOG_COMMUNICATION_HELP = (f"If provided, all requests and responses are logged and written to disk (default: "
                              f"{DEFAULT_LOG_COMMUNICATION})")


class GeneralOptions(Enum):
    """Specifies general options"""

    LOG = auto()
    LOGFILE = auto()


class Command(Enum):
    """Specifies command to execute"""

    RUN = auto()


class RunOptions(Enum):
    """Options for command `run`"""

    HOST = auto()
    PORT = auto()
    MODEL = auto()
    CONFIG_PATH = auto()
    LOG_COMMUNICATION = auto()


Options = {
    Command.RUN: RunOptions,
}


def arg_handling_run(input_args: Optional[list[str]] = None) -> tuple[Command, dict[Enum, Any]]:
    """Handles command line arguments  and returns `command` and its options `args`"""
    parent_parser = argparse.ArgumentParser(prog="amiris-priceforecast", description=PRICEFORECAST_PARSER)
    parent_parser.add_argument("-lf", "--logfile", type=Path, required=False, help=PRICEFORECAST_LOG_FILE_HELP)
    parent_parser.add_argument(
        "-l",
        "--log",
        default=LogLevels.ERROR.name,
        choices=[level.name.lower() for level in LogLevels],
        help=PRICEFORECAST_LOG_LEVEL_HELP,
    )
    subparsers = parent_parser.add_subparsers(dest="command", required=True, help=PRICEFORECAST_COMMAND_HELP)

    create_parser = subparsers.add_parser("run", help=RUN_HELP)
    create_parser.add_argument("--host", "-ho", type=str, default=DEFAULT_HOST, help=RUN_HOST_HELP)
    create_parser.add_argument("--port", "-po", type=int, default=DEFAULT_PORT, help=RUN_PORT_HELP)
    create_parser.add_argument("--model", "-m", required=True, type=Models.instantiate, choices=Models,
                               help=RUN_MODEL_HELP)
    create_parser.add_argument("--config_path", "-cp", required=False, type=Path, help=RUN_CONFIG_PATH_HELP)
    create_parser.add_argument("--log_communication", "-lc", default=DEFAULT_LOG_COMMUNICATION, action="store_true",
                               help=RUN_LOG_COMMUNICATION_HELP)

    args = vars(parent_parser.parse_args(input_args))
    command = Command[args.pop("command").upper()]

    args = resolve_relative_paths(args)

    return command, enumify(command, args)


def resolve_relative_paths(args: dict) -> dict:
    """Returns given `args` with relative paths resolved as absolute paths"""
    for option in args:
        if isinstance(args[option], Path):
            args[option] = args[option].resolve()
    return args


def enumify(command: Command, args: dict) -> dict[Enum, Any]:
    """Matches `args` for given `command` to their respective Enum"""
    result = {}
    for option in GeneralOptions:
        result[option] = args.pop(option.name.lower())

    for option in Options[command]:
        result[option] = args.pop(option.name.lower())
    return result
