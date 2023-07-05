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
from typing import Any, TypeVar, Type

from dataclasses import dataclass, field, MISSING
import dataclasses
from abc import ABC, abstractmethod

from argparse import _SubParsersAction, ArgumentParser, Namespace


CommandBaseT = TypeVar("CommandBaseT", bound="BaseCmd")


def cmd_arg(
        default: Any = MISSING,
        default_factory: Any = MISSING,
        abrv: str | None = None,
        help: str | None = None,
        choices: list[Any] | None = None,
        optional: bool = False
    ) -> Any:
    """A wrapper around dataclasses.field() which add automatic metadata creations

    Args:
        default (Any, optional): The default value of the argument. Defaults to MISSING.
        default_factory (Any, optional): The default factory of the argument. Defaults to MISSING.
        abrv (str | None, optional): The abbreviation (if there is one) of the argument flag.
            Defaults to None.
        help (str | None, optional): The help string to display on the argument.
            Defaults to None.
        choices (list[Any] | None, optional): The valid choices the argument can be.
            Defaults to None.
        optional (bool, optional): Whether a value after the argument is optional.
            Defaults to False.

    Returns:
        Any: The dataclasses.field() object which represents the arg
    """
    metadata = {}
    if abrv is not None:
        metadata['abrv'] = abrv
    if help is not None:
        metadata['help'] = help
    metadata['optional'] = optional

    if choices is not None:
        metadata['choices'] = choices

    return field(default=default, default_factory=default_factory, metadata=metadata)


@dataclass
class BaseCmd(ABC):
    @classmethod
    def add_subcmd(cls, parser: _SubParsersAction[ArgumentParser]) -> None:
        subparser = parser.add_parser(
            cls.__name__.lower(),
            help=cls.__doc__
        )

        for fld in dataclasses.fields(cls):
            kwargs = {}

            if 'list' in fld.type:
                kwargs["nargs"] = "+"
            elif 'bool' in fld.type:
                kwargs['action'] = "store_true"
            elif 'str' in fld.type:
                kwargs['type'] = str
            elif 'int' in fld.type:
                kwargs['type'] = int

            if 'optional' in fld.metadata and fld.metadata['optional']:
                if 'nargs' in kwargs:
                    kwargs['nargs'] = '*'
                else:
                    kwargs['nargs'] = '?'

            if 'choices' in fld.metadata:
                kwargs['choices'] = fld.metadata['choices']

            if not isinstance(fld.default, dataclasses._MISSING_TYPE):
                kwargs["default"] = fld.default
            elif not isinstance(fld.default_factory, dataclasses._MISSING_TYPE):
                kwargs["default"] = fld.default_factory()
            else:
                kwargs["default"] = None

            kwargs["help"] = fld.metadata['help']

            if isinstance(fld.default, dataclasses._MISSING_TYPE) and \
               isinstance(fld.default_factory, dataclasses._MISSING_TYPE):
                subparser.add_argument(fld.name, **kwargs)
            elif 'abrv' in fld.metadata:
                subparser.add_argument(f"--{fld.name}", f"-{fld.metadata['abrv']}", **kwargs)
            else:
                subparser.add_argument(f"--{fld.name}", **kwargs)

        subparser.set_defaults(subcmd=cls.from_args)

    @classmethod
    def from_args(cls: Type[CommandBaseT], args: Namespace) -> CommandBaseT:
        """Convert the argparser arguments into the Commandbase type

        Args:
            cls (Type[CommandBaseT]): The class to convert to
            args (Namespace): The ArgParser namespace containing the command line args

        Returns:
            CommandBaseT: The instance from the args
        """
        kwargs = {}

        for fld in dataclasses.fields(cls):
            kwargs[fld.name] = getattr(args, fld.name)

            if 'list' in fld.type and 'optional' in fld.metadata and fld.metadata['optional']:
                if kwargs[fld.name] is None:
                    kwargs[fld.name] = []
                elif len(kwargs[fld.name]) == 0:
                    kwargs[fld.name] = None

        return cls(**kwargs)

    @abstractmethod
    def __call__(self) -> None: pass


#####################################################################################
# Script Entry Point
#####################################################################################
if __name__ == "__main__":
    raise NotImplementedError("rbuild.cmds.base is not a stand-alone script.")
