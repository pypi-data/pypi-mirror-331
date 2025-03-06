from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, overload, override

from ..compiler.types import (
    Datum,
    Function,
    Module,
    Resource,
)


class Integer(Datum):
    @property
    @override
    def name(self) -> str:
        return "integer"

    @override
    def can_compare(self, other: Datum) -> bool:
        if other == Decimal_():
            return True
        return super().can_compare(other)

    @override
    def parse(self, value: str | int) -> int:
        if type(value) is int:
            return value

        if isinstance(value, str):
            return int(value)
        return super().parse(value)

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "integer"}


class Decimal_(Datum):
    @property
    def name(self) -> str:
        return "decimal"

    @override
    def to_json(self, value):
        return float(value)

    @override
    def can_compare(self, other: Datum) -> bool:
        if other == Integer():
            return True
        return super().can_compare(other)

    @override
    def parse(self, value: str | Decimal) -> Decimal:
        if type(value) is Decimal:
            return value

        try:
            if isinstance(value, str) or isinstance(value, int):
                return Decimal(str(value))
            return super().parse(value)
        except InvalidOperation:
            return super().parse(value)

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "number"}


class Add(Function):
    module = "operator"
    name = "add"
    num_args = 2

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        left, right = args
        if left == Integer() and right == Integer():
            return Integer()
        elif left in [Integer(), Decimal_()] and right in [
            Integer(),
            Decimal_(),
        ]:
            return Decimal_()


class Negate(Function):
    module = "operator"
    name = "neg"
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
        value = args[0]
        if value in [Integer(), Decimal_()]:
            return value


class Subtract(Function):
    module = "operator"
    name = "sub"
    num_args = 2

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        left, right = args
        if left == Integer() and right == Integer():
            return Integer()
        elif left in [Integer(), Decimal_()] and right in [
            Integer(),
            Decimal_(),
        ]:
            return Decimal_()


restrict_module = Module(
    {o.name: o for o in [Integer(), Decimal_()]},
    {
        "add": Add(),
        "negate": Negate(),
        "subtract": Subtract(),
    },
    {},
)
