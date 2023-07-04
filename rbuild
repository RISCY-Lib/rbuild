#!/usr/bin/env python3

#####################################################################################
# The rbuild tool which is used to compile, sim, etc. for the RISCY-Lib Org Projects
# Copyright (C) 2023  RISCY-Lib Contributors
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; If not, see <https://www.gnu.org/licenses/>.
#####################################################################################

from __future__ import annotations

import py_pretty_logger.full_logger as logging
from py_pretty_logger.pretty_logging import SimpleFormatter, PrettyFormatter
from datetime import datetime

from pathlib import Path

import argparse

import os

#####################################################################################
# Main Body
#####################################################################################
def main():
    """The entry point for the rbuild program
    """

    # Check that the setup.sh file has been sourced
    if 'RISCY_DIR' not in os.environ:
        logging.critical("Project setup.sh must be sourced before rbuild can be called")
        exit(1)

    # Handle the command lines
    args = handle_command_line()

    # Check the rbuild command is being called from run directory
    if Path(os.environ['RISCY_DIR'] + "/run") not in Path(".").absolute().parents:
        logging.critical("rbuild must be run in valid project rundir")
        exit(1)

    # Setup logging
    log_lvl = logging.DEBUG if args.debug else logging.INFO

    log_filename = args.logfile

    if not Path("logs").exists():
        Path("logs").mkdir(parents=True)

    fHandler = logging.FileHandler(log_filename, mode="w")
    fHandler.setFormatter(SimpleFormatter())
    fDateHandler = logging.FileHandler(
        datetime.now().strftime('logs/dv_%Y_%m_%d_%H_%M.log'),
        mode = "w"
    )
    fDateHandler.setFormatter(SimpleFormatter())
    cHandler = logging.StreamHandler()
    cHandler.setFormatter(PrettyFormatter())

    logging.basicConfig(
        level=log_lvl,
        handlers=[fHandler, fDateHandler, cHandler]
    )

    # Print the project settings if that is desired
    if args.print_settings:
        raise NotImplementedError("rbuild --print_settings not yet implemented")

    # Execute the sub-command
    if args.subcommand_name is not None:
        logging.info(f"Using sub-command {args.subcommand_name}")
        cmd = args.subcmd(args)
        cmd()
    else:
        logging.info("No rbuild sub-command selected. Use rbuild -h/--help for usage")


#####################################################################################
# Helper Functions
#####################################################################################
def handle_command_line() -> argparse.Namespace:
    """Handles the CLI (argument parsing) for the rbuild program

    Returns:
        argparse.Namespace: The parsed command line arguments as a Namespace
    """
    # Main CLI Arguments
    parser = argparse.ArgumentParser(
        "rbuild", description="The top-level CLI for RISCY-Lib projects"
    )
    parser.add_argument(
        "--debug", default=False, action="store_true",
        help="Enables debug logging messages"
    )
    parser.add_argument(
        "--print_settings", default=False, action="store_true",
        help="Prints the current project settings prior to executing any sub-command"
    )
    parser.add_argument(
        "--logfile", "-a", default="dv_log.log", type=str,
        help="Changes the default logfile name"
    )

    # Add Sub-Commands
    sub_parsers = parser.add_subparsers(
        title="Sub-Commands",
        help="Sub-Command Help",
        dest="subcommand_name"
    )

    return parser.parse_args()


#####################################################################################
# Script Entry Point
#####################################################################################
if __name__ == "__main__":
    main()
