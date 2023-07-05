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
from typing import Iterator

from pathlib import Path

import yaml

from dataclasses import dataclass, field

from py_pretty_logger import full_logger as logging


class DependencyLoopError(Exception):
    """Indicates there is a loop in the dependency tree"""
    pass


class NotAFileError(OSError):
    """Raised when trying to access a non-file object as a file"""
    pass


def build_tree(roots: list[str] | str) -> BuildTree:
    """Create the build tree using the provided file or files as the roots

    Args:
        roots (list[str] | str): The root (or list of roots) to use as the base

    Returns:
        BuildTree: The build tree generated from the roots
    """
    builder = _TreeBuilder()
    return builder.build_tree(roots)


class _TreeBuilder:
    def __init__(self):
        self.nodes : dict[Path, BuildNode] = {}

    @classmethod
    def resolve_path(cls, path: str, current_dir: Path) -> Path:
        if path.startswith('/'):
            return Path(path)

        return current_dir.joinpath(path).resolve()

    def build_tree(self, roots: list[str] | str) -> BuildTree:
        """Create the build tree using the provided file or files as the roots

        Args:
            roots (list[str] | str): The root (or list of roots) to use as the base

        Returns:
            BuildTree: The build tree generated from the roots
        """
        btree = BuildTree()

        if isinstance(roots, str):
            roots = [roots]

        for root in roots:
            root_path = Path(root)

            if not root_path.exists():
                logging.error(f"Root Build File ({root}) does not exist")

            btree.roots.append(self.build_node(root_path, list()))

        return btree

    def build_node(self, node_path: Path, nstack: list[Path]) -> BuildNode:
        """The recursive method which creates a BuildNode and all child nodes

        Args:
            node_path (Path): The path to the bld file to add a node from
            nstack (list[Path]): The stack of previous bld files to detect loops

        Raises:
            FileNotFoundError: When the specified bld node file is not found
            NotAFileError: When the specified bld node path is not a file
            DependencyLoopError: When the specified bld node path is already in the nstack.
                Indicates that a loop is present in the build files
            TypeError: When values from the bld node file are not the expected type

        Returns:
            BuildNode: _description_
        """

        if not node_path.exists():
            msg = f"Path to build node ({node_path}) does not exist"
            logging.error(msg)
            raise FileNotFoundError(msg)

        if not node_path.is_file():
            msg = f"Path to build node ({node_path}) is not a file"
            logging.error(msg)
            raise NotAFileError(msg)

        if node_path in nstack:
            msg = f"Loop in build dependencies ({node_path} from {nstack[-1]})"
            logging.error(msg)
            raise DependencyLoopError(msg)

        if node_path in self.nodes:
            return self.nodes[node_path]

        bnode_dir = node_path.parent

        bnode = BuildNode(node_path)

        with open(bnode.path, "r") as bnode_yaml:
            bnode_dict = yaml.safe_load(bnode_yaml)

        if bnode_dict is None:
            logging.warning(f"Build node is empty")
            self.nodes[node_path] = bnode
            return bnode

        if 'src' in bnode_dict:
            for src in bnode_dict['src']:
                bnode.src.append(self.resolve_path(src, bnode_dir))

        if 'include' in bnode_dict:
            for inc in bnode_dict['include']:
                bnode.includes.append(self.resolve_path(inc, bnode_dir))

        if 'needs' in bnode_dict:
            for need in bnode_dict['needs']:
                if not isinstance(need, str):
                    raise TypeError(f"A need defined in {node_path} is not a string")

                try:
                    nstack.append(node_path)
                    bnode.needs.append(
                        self.build_node(
                            self.resolve_path(need, bnode_dir), nstack
                        )
                    )
                except NotAFileError as _:
                    pass
                except FileNotFoundError as _:
                    pass
                except DependencyLoopError as _:
                    pass

        self.nodes[node_path] = bnode

        return bnode


@dataclass(slots=True)
class BuildTree:
    """The Top-Level Build Tree for compile"""

    includes: list[Path] = field(default_factory=list)
    """A list of all the include paths"""
    roots: list[BuildNode] = field(default_factory=list)
    """The root of the build """

    def stringify(self) -> str:
        """Creates a nicely human-readable representation of the tree

        Returns:
            str: The human readable string
        """
        ret_val = ""
        for node in self.roots:
            ret_val += node.stringify()

        return ret_val

    def traverse(self, unique: bool = True) -> Iterator[BuildNode]:
        """Post-Order traverse of the build tree

        Yields:
            Iterator[BuildNode]: The next node in the tree
        """
        visited = []

        for root in self.roots:
            for node in root.traverse([]):
                if not unique:
                    yield node
                else:
                    if not node in visited:
                        visited.append(node)
                        yield node
            yield root


@dataclass(slots=True)
class BuildNode:
    """A node in the build tree"""

    path: Path
    src: list[Path] = field(default_factory=list)
    needs: list[BuildNode] = field(default_factory=list)
    includes: list[Path] = field(default_factory=list)

    def stringify(self) -> str:
        """Creates a nicely human-readable representation of the tree

        Returns:
            str: The human readable string
        """
        ret_val = f"- {self.path}\n"

        for node in self.needs:
            ret_val += "  " + node.stringify().replace("\n  ", "\n    ")

        return ret_val

    def traverse(self, tstack: list[Path]) -> Iterator[BuildNode]:
        tstack.append(self.path)

        for needed in self.needs:
            for node in needed.traverse(tstack):
                yield node
            yield needed


#####################################################################################
# Script Entry Point
#####################################################################################
if __name__ == "__main__":
    raise NotImplementedError("rbuild.cmds.build_tree is not a stand-alone script.")