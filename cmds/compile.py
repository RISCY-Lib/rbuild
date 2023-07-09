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

from cmds.base import BaseCmd, cmd_arg
from dataclasses import dataclass

from cmds._build_tree import build_tree
from cmds._common import run_cmd

import os

from pathlib import Path


#####################################################################################
# Sub-Command Class
#####################################################################################
@dataclass
class Compile(BaseCmd):
    """The command use to compile the test-bench and dut for simulation"""

    verbose: bool = cmd_arg(
        default=False,
        abrv="v",
        help="Prints additional verbose information to the command line"
    )
    """Print additional verbose information to the command line"""
    build_tree: bool = cmd_arg(
        default=False,
        help="Only construct and check the build tree, don't actually compile"
    )
    """Only construct and check the build tree, don't actually compile"""
    force: bool = cmd_arg(
        default=False,
        abrv="f",
        help="Force an overwrite of pre-existing compile"
    )
    """Force an overwrite of pre-existing compile"""
    defines: list[str] = cmd_arg(
        default_factory=list,
        help="A list of defines to use during the elaboration stage of the compile"
    )
    """A list of defines to use during the elaboration stage of the compile"""

    def __post_init__(self):
        """Setup any variables after creation before running the command
        """
        pass

    def __call__(self) -> None:
        """Executes the Compile command
        """
        # Setup the build tree
        self.btree = build_tree(os.environ['RISCY_DIR'] + "/tb/tb_top.bld")

        if self.verbose:
            logging.info("Build tree generated:")
            logging.raw(self.btree.stringify())

        if self.build_tree:
            exit(0)

        self.parse()
        self.elaborate()

        logging.success_banner("Test-bench Compiled Successfully!")

    def parse(self) -> None:
        """Parse all of the files in the build tree
        """
        include_dirs = self.include_dirs()

        success = True

        for node in self.btree.traverse():
            for src in node.src:
                if src.suffix in [".sv", ".v"]:
                    cmd = "xvlog -sv"
                else:
                    cmd = "xvhdl"

                if Path(os.environ['RISCY_DIR']) in src.parents:
                    cmd += " -L uvm"

                ret_val = run_cmd(f"{cmd} {include_dirs} {src}")

                if ret_val != 0:
                    logging.error(f"Error parsing: {src}")
                    success = False

        if not success:
            logging.critical(f"Stopping due to parsing errors.")
            exit(1)

    def elaborate(self) -> None:
        """Elaborate the design for simulation
        """
        include_dirs = self.include_dirs()

        cmd = f"xelab tb_top {include_dirs} -L uvm"
        cmd += " --debug all -O0"

        for define in self.defines:
            cmd += f" -d {define}"

        if run_cmd(cmd) != 0:
            logging.critical(f"Error performing elaboration.")
            exit(1)

    def include_dirs(self) -> str:
        """Get a list of all the include dirs from the build tree

        Returns:
            list[str]: The list of include dirs from the build tree
        """
        dirs = set()

        for node in self.btree.traverse():
            for inc in node.includes:
                dirs.add(str(inc))

        icmd = " -i ".join(dirs)

        if icmd != "":
            icmd = "-i " + icmd

        return icmd

#####################################################################################
# Script Entry Point
#####################################################################################
if __name__ == "__main__":
    raise NotImplementedError("rbuild.cmds.compile is not a stand-alone script.")
