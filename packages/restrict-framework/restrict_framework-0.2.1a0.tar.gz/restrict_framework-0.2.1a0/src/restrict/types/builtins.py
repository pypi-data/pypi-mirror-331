from __future__ import annotations

import ast as pyast
from collections.abc import Callable
from functools import singledispatchmethod
from typing import Any as TypeAny
from typing import overload, override

from ..compiler.exceptions.compile import InvalidFuncCallError
from ..compiler.types import (
    Data,
    Datum,
    DatumTuple,
    Function,
    OptionalDatum,
    OptionalResource,
    ParameterizedFunction,
    Resource,
    ResourceCollection,
    ResourceTuple,
)


class Boolean(Datum):
    @property
    @override
    def name(self) -> str:
        return "boolean"

    @override
    def can_compare(self, other: Datum) -> bool:
        if other == Boolean():
            return True
        return super().can_compare(other)

    @override
    def parse(self, value: str) -> bool:
        if value == "true" or value is True:
            return True

        if value == "false" or value is False:
            return False

        return super().parse(value)

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        return {"type": "boolean"}


class BinaryBooleanFunction(Function):
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
        if left == Boolean() and right == Boolean():
            return Boolean()


class And(BinaryBooleanFunction):
    module = "operator"
    name = "and_"
    num_args = 2


class Or(BinaryBooleanFunction):
    module = "operator"
    name = "or_"
    num_args = 2


class Not(Function):
    module = "operator"
    name = "not_"
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
        if args[0] == Boolean():
            return Boolean()


class BinaryComparableFunction(Function):
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
        if isinstance(left, Resource) or isinstance(right, Resource):
            raise ValueError(f"{self.name} cannot accept resource arguments")
        comparable = (
            left.can_compare(right) or right.can_compare(left)
            if left is not None and right is not None
            else None
        )
        if comparable:
            return Boolean()


class Equals(BinaryComparableFunction):
    module = "operator"
    name = "eq"
    num_args = 2


class LessThan(BinaryComparableFunction):
    module = "operator"
    name = "lt"
    num_args = 2


class LessThanOrEqual(BinaryComparableFunction):
    module = "operator"
    name = "le"
    num_args = 2


class GreaterThan(BinaryComparableFunction):
    module = "operator"
    name = "gt"
    num_args = 2


class GreaterThanOrEqual(BinaryComparableFunction):
    module = "operator"
    name = "ge"
    num_args = 2


class BooleanReductionFunction(Function):
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
        arg = args[0]
        if isinstance(arg, Data) and arg.internal_type == Boolean():
            return Boolean()


class All(BooleanReductionFunction):
    module = ""
    name = "all"


class Any(BooleanReductionFunction):
    module = ""
    name = "any"


class SwapArgPositionsMixin:
    _coll_type: type[list] | type[set]
    to_py_name: Callable[[], pyast.Name | pyast.Attribute]
    num_args = tuple[int, int] | int
    name: str

    def to_py(
        self,
        is_optional: bool,
        pyasts: list[pyast.expr],
        return_value: bool | None,
    ) -> pyast.expr:
        if len(pyasts) != 2:
            raise InvalidFuncCallError(self.name, 2, len(pyasts), None, None)
        return pyast.Call(
            func=pyast.Name(id=self._coll_type.__name__, ctx=pyast.Load()),
            args=[
                pyast.Call(
                    func=self.to_py_name(),
                    args=[
                        pyast.Lambda(
                            args=pyast.arguments(
                                args=[pyast.arg(x.name) for x in self._params]  # type: ignore
                            ),
                            body=pyasts[1],
                        ),
                        pyasts[0],
                    ],
                    keywords=[],
                )
            ],
            keywords=[],
        )


class Filter(SwapArgPositionsMixin, ParameterizedFunction):
    module = ""
    name = "filter"
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
        if isinstance(args[-1], Datum):
            return Data(list, args[-1])
        if isinstance(args[-1], Resource):
            return ResourceCollection(list, args[-1])

    @override
    def prepare_params(self, value: Datum | Resource):
        self._value = value
        if isinstance(value, OptionalDatum):
            value = value.internal_type
        if isinstance(value, OptionalResource):
            value = value.internal_type
        if not isinstance(value, Data) and not isinstance(value, ResourceCollection):
            raise ValueError(f"Filter requires a collection. Got {value}.")
        self._set_param_types(value.internal_type)
        self._coll_type = value.collection_type

    @singledispatchmethod
    def _set_param_types(self, _): ...

    @_set_param_types.register
    def _(self, tup: ResourceTuple):
        for t, p in zip(tup.internal_types, self._params):
            p.res = t

    @_set_param_types.register
    def _(self, t: Resource):
        self._params[0].res = t

    @_set_param_types.register
    def _(self, tup: DatumTuple):
        for t, p in zip(tup.internal_types, self._params):
            p.res = t

    @_set_param_types.register
    def _(self, t: Datum):
        self._params[0].res = t


class Map(SwapArgPositionsMixin, ParameterizedFunction):
    module = ""
    name = "map"
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
        if isinstance(args[-1], Datum):
            return Data(list, args[-1])
        if isinstance(args[-1], Resource):
            return ResourceCollection(list, args[-1])

    @override
    def prepare_params(self, value: Datum | Resource):
        self._value = value
        if isinstance(value, OptionalDatum):
            value = value.internal_type
        if isinstance(value, OptionalResource):
            value = value.internal_type
        if not isinstance(value, Data) and not isinstance(value, ResourceCollection):
            raise ValueError(f"Map requires a collection. Got {value}.")
        self._set_param_types(value.internal_type)
        self._coll_type = value.collection_type

    @singledispatchmethod
    def _set_param_types(self, _): ...

    @_set_param_types.register
    def _(self, tup: ResourceTuple):
        for t, p in zip(tup.internal_types, self._params):
            p.res = t

    @_set_param_types.register
    def _(self, t: Resource):
        self._params[0].res = t

    @_set_param_types.register
    def _(self, tup: DatumTuple):
        for t, p in zip(tup.internal_types, self._params):
            p.res = t

    @_set_param_types.register
    def _(self, t: Datum):
        self._params[0].res = t


class Zip(Function):
    module = ""
    name = "zip"
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
        result = None
        if isinstance(left, Data) and isinstance(right, Data):
            t = DatumTuple([left.internal_type, right.internal_type])
            result = Data(list, t)
        elif isinstance(left, ResourceCollection) and isinstance(
            right, ResourceCollection
        ):
            t = ResourceTuple([left.internal_type, right.internal_type])
            result = ResourceCollection(list, t)
        return result


types: dict[str, Datum] = {o.name: o for o in [Boolean()]}
functions: dict[str, Function] = {
    "all": All(),
    "and": And(),
    "any": Any(),
    "eq": Equals(),
    "filter": Filter(),
    "gt": GreaterThan(),
    "gte": GreaterThanOrEqual(),
    "map": Map(),
    "not": Not(),
    "or": Or(),
    "zip": Zip(),
}
