import os
from typing import overload, override

from ..compiler.types import Datum, Function, Module, Resource
from .text import Text


def getenv(name, default=None):
    if default is None:
        return os.environ[name]
    return os.getenv(name, default)


class EnvVar(Function):
    module = __module__
    name = "getenv"

    num_args = (1, 2)

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        if len(args) == 1 and args[0] == Text():
            return Text()

        left, right = args
        if left == Text() and right == Text():
            return Text()


restrict_module = Module(
    {},
    {"env": EnvVar()},
    {},
)
