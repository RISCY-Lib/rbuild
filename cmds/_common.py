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

from py_pretty_logger import full_logger as logging

from subprocess import Popen, PIPE, STDOUT

def run_cmd(cmd: str) -> int:
    """Runs the provided string command as a shell command.
    Prints the stdout and stderr as the process executes to the logger

    Args:
        cmd (str): The shell command to run

    Returns:
        int: The return value of the command
    """
    logging.info(f"Running cmd: {cmd}")
    with Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            logging.raw(line.decode('utf-8').rstrip())

    return proc.returncode