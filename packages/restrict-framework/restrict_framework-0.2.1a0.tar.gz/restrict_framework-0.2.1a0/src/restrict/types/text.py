from __future__ import annotations

from typing import Any, overload, override

from ..compiler.types import (
    Datum,
    Function,
    Module,
    Resource,
)
from .numeric import Integer


class Text(Datum):
    @property
    @override
    def name(self) -> str:
        return "text"

    @override
    def can_compare(self, other: Datum) -> bool:
        if other in [Hash(), Email()]:
            return True
        return super().can_compare(other)

    @override
    def parse(self, value: str) -> str:
        if isinstance(value, str):
            return value
        return super().parse(value)

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "string"}


class Email(Datum):
    @property
    @override
    def name(self) -> str:
        return "email"

    @override
    def can_compare(self, other: Datum) -> bool:
        if other in [Text(), Hash()]:
            return True
        return super().can_compare(other)

    @override
    def parse(self, value: str) -> str:
        if isinstance(value, str):
            return value
        return super().parse(value)

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "string", "format": "email"}


class Hash(Datum):
    @property
    @override
    def name(self) -> str:
        return "hash"

    @override
    def can_compare(self, other: Datum) -> bool:
        if other in [Text(), Email()]:
            return True
        return super().can_compare(other)

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "string", "contentEncoding": "base64"}

    @override
    def parse(self, value: str) -> str:
        if isinstance(value, str):
            return value
        return super().parse(value)


def rs(length):
    import random
    import string

    return "".join(random.choice(string.ascii_letters) for _ in range(length))


class RandomString(Function):
    module = __module__
    name = "rs"
    num_args = 1
    can_return_optional = False

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        if args[0] == Integer():
            return Text()


class TextLen(Function):
    name = "len"
    num_args = 1

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        operand = args[0]
        if operand in [Text(), Email(), Hash()]:
            return Integer()


restrict_module = Module(
    {o.name: o for o in [Text(), Hash(), Email()]},
    {
        "random_string": RandomString(),
        "text_len": TextLen(),
    },
    {},
)
