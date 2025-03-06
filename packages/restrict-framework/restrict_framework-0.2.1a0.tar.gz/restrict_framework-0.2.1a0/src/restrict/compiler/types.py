from __future__ import annotations

import ast as pyast
import random
import string
from abc import ABC, abstractmethod
from collections.abc import (
    Callable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any as TypeAny
from typing import Literal, Type, cast, overload, override

from .exceptions.compile import InvalidFuncCallError


def rs(length):
    return "".join([random.choice(string.ascii_letters) for _ in range(length)])


@dataclass
class Module:
    types: dict[str, Datum]
    functions: dict[str, Function]
    resources: dict[str, Resource]


@dataclass
class FuncParamRef:
    param: FuncParam
    path: list[str]

    @property
    def res(self) -> Datum | Resource | None:
        return self.param.res

    def resolve_type(self):
        if len(self.path) > 0:
            res = cast(Resource, self.res)
            resolved = res.resolve_path(self.path)
            if resolved is not None:
                return resolved[-1]
        return self.res

    @property
    def is_leaf(self) -> bool:
        return False

    def get_imports(self) -> set:
        return set()

    def to_py(self, return_value: bool | None):
        return pyast.Name(id=self.param.name, ctx=pyast.Load())


@dataclass
class FuncParam:
    name: str
    res: Datum | Resource | None = None

    def create_ref(self, path: list[str]):
        return FuncParamRef(self, path)


class Datum(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def to_schema(self) -> dict[str, TypeAny]: ...

    def parse(self, value: TypeAny) -> TypeAny:
        raise ValueError(f"{self.name}: Cannot parse {value}")

    def get_imports(self) -> set:
        return set()

    def __eq__(self, value):
        return type(value) is type(self)

    def __str__(self):
        return self.name

    def can_compare(self, other: Datum) -> bool:
        if type(self) is type(other):
            return True
        return False

    def can_handle_tag(self, tag: str) -> bool:
        return False

    def can_handle_value(self, value: str) -> bool:
        return False

    def __repr__(self):
        return type(self).__name__ + "()"

    def to_json(self, value):
        return value


class OptionalDatum(Datum):
    def __init__(self, internal_type: Datum):
        self._internal_type = internal_type

    @staticmethod
    def wrap(value: Datum) -> OptionalDatum:
        if not isinstance(value, OptionalDatum):
            return OptionalDatum(value)
        return value

    def parse(self, value: TypeAny) -> TypeAny:
        if value is None:
            return None
        return self._internal_type.parse(value)

    def can_compare(self, other: Datum) -> bool:
        if isinstance(other, OptionalDatum):
            other = other._internal_type
        return self._internal_type.can_compare(other)

    def __eq__(self, other):
        return (
            isinstance(other, OptionalDatum)
            and self._internal_type == other.internal_type
        )

    def __repr__(self):
        return f"OptionalDatum({repr(self._internal_type)})"

    @property
    def internal_type(self):
        return self._internal_type

    @property
    def name(self) -> str:
        return "optional " + self._internal_type.name

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        return self._internal_type.to_schema()

    @property
    def is_required(self) -> bool:
        return False


class Data(Datum):
    def __init__(
        self,
        collection_type: Type[set[Datum]] | Type[list[Datum]],
        internal_type: Datum,
    ):
        self._collection_type = collection_type
        self._internal_type = internal_type

    def __repr__(self):
        return f"Data({self.collection_type.__name__}, {repr(self._internal_type)})"

    @override
    def parse(self, value: TypeAny) -> TypeAny:
        if isinstance(value, list):
            return self._collection_type([self._internal_type.parse(x) for x in value])
        return super().parse(value)

    @property
    def used(self) -> bool:
        try:
            return self._internal_type.used  # type: ignore
        except AttributeError:
            return False

    @used.setter
    def used(self, value: bool):
        try:
            self._internal_type.used = value  # type: ignore
        except AttributeError:
            pass

    @property
    @override
    def name(self) -> str:
        return f"{self._collection_type.__name__}[{self.internal_type.name}]"

    @property
    def collection_type(self) -> Type[set] | Type[list]:
        return self._collection_type

    @property
    def internal_type(self) -> Datum:
        return self._internal_type

    def __eq__(self, other):
        if isinstance(other, Data):
            return (
                other.internal_type == self.internal_type
                and self.collection_type is other.collection_type
            )
        return False

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        uniquity = {"uniqueItems": self._collection_type is set}
        return uniquity | {
            "type": "array",
            "items": self._internal_type.to_schema(),
        }

    def to_json(self, value):
        return list(self._internal_type.to_json(v) for v in value)


class DatumTuple(Datum):
    def __init__(self, internal_types: list[Datum]):
        self._internal_types = internal_types

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        return {
            "type": "array",
            "prefixItems": [t.to_schema() for t in self._internal_types],
            "uniqueItems": False,
        }

    @property
    def used(self) -> bool:
        for t in self._internal_types:
            try:
                return t.used  # type: ignore
            except AttributeError:
                pass
        return False

    @used.setter
    def used(self, value: bool):
        for t in self._internal_types:
            try:
                t.used = value  # type: ignore
            except AttributeError:
                pass

    @property
    @override
    def name(self) -> str:
        names = [t.name for t in self._internal_types]
        return f"tuple[{', '.join(names)}]"

    @property
    def internal_types(self) -> list[Datum]:
        return self._internal_types

    def to_json(self, value):
        if len(value) != len(self._internal_types):
            raise ValueError("Wrong number of types")
        return list([t.to_json(v) for t, v in zip(self._internal_types, value)])

    def parse(self, value):
        if len(value) != len(self._internal_types):
            raise ValueError("Wrong number of types")
        return tuple([t.parse(v) for t, v in zip(self._internal_types, value)])


class Function(ABC):
    module = ""
    name = ""
    num_args: tuple[int, int] | int
    can_return_optional = True

    def clone(self):
        return type(self)()

    @overload
    def calculate_return_type(self, args: list[Datum]) -> Datum: ...

    @overload
    def calculate_return_type(self, args: list[Resource]) -> Resource: ...

    def calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource:
        lower = -1
        upper = -1
        if type(self.num_args) is tuple:
            lower = self.num_args[0]
            upper = self.num_args[1]
        elif type(self.num_args) is int:
            lower = self.num_args
            upper = self.num_args
        if len(args) < lower or len(args) > upper:
            raise InvalidFuncCallError(self.name, lower, len(args), None, None)
        is_optional_datum = False
        is_optional_resource = False
        unwrapped = []
        for a in args:
            if isinstance(a, OptionalDatum) and self.can_return_optional:
                is_optional_datum = True
                a = a.internal_type
            elif isinstance(a, OptionalResource) and self.can_return_optional:
                is_optional_resource = True
                a = a.internal_type
            elif isinstance(a, OptionalDatum) or isinstance(a, OptionalResource):
                raise ValueError(f"{self.name} cannot accept optional arguments")
            unwrapped.append(a)
        t = self._calculate_return_type(unwrapped)
        if t is None:
            msg = (
                f"{self.name} cannot accept args {', '.join(str(x) for x in unwrapped)}"
            )
            raise ValueError(msg)
        if is_optional_datum and isinstance(t, Datum):
            t = OptionalDatum(t)
        elif is_optional_resource and isinstance(t, Resource):
            t = OptionalResource(t)
        return t

    def to_py_name(self):
        if len(self.module) > 0:
            pieces = self.module.split(".") + [self.name]
        else:
            pieces = [self.name]
        o = pyast.Name(id=pieces[0], ctx=pyast.Load())
        for piece in pieces[1:]:
            o = pyast.Attribute(value=o, attr=piece, ctx=pyast.Load())
        return o

    def to_py(
        self,
        is_optional: bool,
        pyasts: list[pyast.expr],
        return_value: bool | None,
    ) -> pyast.expr | list[pyast.stmt]:
        o = self.to_py_name()
        if not is_optional:
            return pyast.Call(func=o, args=pyasts, keywords=[])

        arg_names = [f"a{i}" for i in range(len(pyasts))]
        comparisons: list[pyast.expr] = [
            pyast.Compare(
                left=pyast.Name(id=a, ctx=pyast.Load()),
                ops=[pyast.IsNot()],
                comparators=[pyast.Constant(value=None)],
            )
            for a in arg_names
        ]
        if len(arg_names) == 1:
            test = comparisons[0]
        else:
            test = pyast.BoolOp(op=pyast.And(), values=comparisons)
        fn_name = rs(10)
        fn = pyast.FunctionDef(
            name=fn_name,
            args=pyast.arguments(
                posonlyargs=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                args=[pyast.arg(name) for name in arg_names],
            ),
            body=[
                pyast.If(  # type: ignore
                    test=test,
                    body=[
                        pyast.Return(
                            value=pyast.Call(  # type: ignore
                                func=o,
                                args=[
                                    pyast.Name(id=a, ctx=pyast.Load())
                                    for a in arg_names
                                ],
                                keywords=[],
                            )
                        )
                    ],
                    orelse=[pyast.Return(value=pyast.Constant(value=return_value))],
                )
            ],
            decorator_list=[],
        )
        return [
            fn,
            pyast.Try(
                body=[
                    pyast.Return(
                        value=pyast.Call(
                            func=pyast.Name(id=fn_name, ctx=pyast.Load()),
                            args=pyasts,
                            keywords=[],
                        )
                    )
                ],
                handlers=[
                    pyast.ExceptHandler(
                        type=pyast.Name(id="AttributeError", ctx=pyast.Load()),
                        body=[
                            pyast.Return(
                                value=pyast.Constant(value=None),
                            ),
                        ],
                    ),
                ],
                orelse=[],
                finalbody=[],
            ),
        ]

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @abstractmethod
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None: ...


class ParameterizedFunction(Function):
    _value: Datum | Resource

    @overload
    def calculate_return_type(self, args: list[Datum]) -> Datum: ...

    @overload
    def calculate_return_type(self, args: list[Resource]) -> Resource: ...

    def calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource:
        if args[0] != self._value:
            raise ValueError("Got different args than prepared with")
        return super().calculate_return_type(args)

    def define_params(self, params: list[FuncParam]):
        self._params = params

    @abstractmethod
    def prepare_params(self, value: Datum): ...


class Relation:
    def __init__(
        self,
        name: str,
        res: Resource,
    ):
        self._name = name
        self._res = res

    def clone(self) -> Relation:
        return copy(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def res(self):
        return self._res

    @res.setter
    def res(self, value: Resource):
        self._res = value


class Field:
    @property
    def res(self) -> Datum: ...

    @res.setter
    def res(self, value): ...

    @property
    def compiled(self) -> Callable[[LayeredMapping], TypeAny]: ...

    @property
    def is_computed(self) -> bool: ...


type EffName = Literal["create", "modify", "delete"]


class Effect:
    @property
    def compiled(self) -> Callable[[LayeredMapping], TypeAny]: ...

    @property
    def res(self) -> Resource | Datum | None: ...

    @res.setter
    def res(self, value): ...


type RuleName = Literal["list", "details", "create", "modify", "delete"]


class Rule:
    @property
    def compiled(self) -> Callable[[LayeredMapping], TypeAny] | None: ...


class Resource(ABC):
    _used: bool
    _is_singleton: bool = False

    @property
    def is_singleton(self):
        return self._is_singleton

    def __eq__(self, value):
        return type(value) is type(self)

    def __repr__(self):
        return f"<{self.name}>"

    @property
    def used(self) -> bool:
        try:
            return type(self)._used
        except AttributeError:
            return False

    @used.setter
    def used(self, value: bool):
        type(self)._used = value

    @property
    def name(self) -> str: ...

    @property
    @abstractmethod
    def field_order(self) -> list[str]: ...

    @abstractmethod
    def get_effects(self) -> Mapping[EffName, Mapping[str, Effect]]: ...

    @abstractmethod
    def get_fields(self) -> Mapping[str, Field]: ...

    @abstractmethod
    def get_relations(self) -> Mapping[str, Relation]: ...

    @abstractmethod
    def get_rules(
        self,
    ) -> Mapping[RuleName, Rule | Mapping[str, Rule]]: ...

    @abstractmethod
    def get_global_names(self) -> Sequence[str]: ...

    @abstractmethod
    def get_singular_relations(self) -> Mapping[str, Relation]: ...

    @abstractmethod
    def resolve_path(self, path: list[str]) -> list[Datum | Resource] | None: ...

    @abstractmethod
    def compiled_name(self) -> str: ...

    @abstractmethod
    def to_schema(self) -> dict[str, TypeAny]: ...


class OptionalResource(Resource):
    def __init__(self, resource: Resource):
        self._resource = resource

    @staticmethod
    def wrap(value: Resource) -> OptionalResource:
        if not isinstance(value, OptionalResource):
            return OptionalResource(value)
        return value

    def __eq__(self, other):
        return isinstance(other, OptionalResource) and self._resource == other._resource

    def __repr__(self):
        return f"OptionalResource({repr(self._resource)})"

    @property
    @override
    def field_order(self) -> list[str]:
        return self._resource.field_order

    @property
    def internal_type(self):
        return self._resource

    @property
    def name(self) -> str:
        return self._resource.name

    @override
    def get_effects(self) -> Mapping[EffName, Mapping[str, Effect]]:
        return self._resource.get_effects()

    @override
    def get_fields(self) -> Mapping[str, Field]:
        return self._resource.get_fields()

    @override
    def get_relations(self) -> Mapping[str, Relation]:
        return self._resource.get_relations()

    @override
    def get_rules(
        self,
    ) -> Mapping[RuleName, Rule | Mapping[str, Rule]]:
        return self._resource.get_rules()

    @override
    def get_global_names(self) -> Sequence[str]:
        return self._resource.get_global_names()

    @override
    def get_singular_relations(
        self,
    ) -> Mapping[str, Relation]:
        return self._resource.get_singular_relations()

    @override
    def resolve_path(self, path: list[str]):
        return self._resource.resolve_path(path)

    @override
    def compiled_name(self) -> str:
        return self._resource.compiled_name()

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        return self._resource.to_schema()


class ResourceCollection(Resource):
    def __init__(
        self,
        collection_type: type[set[Resource]] | type[list[Resource]],
        resource: Resource,
    ):
        self._resource = resource
        self._collection_type = collection_type

    def __repr__(self):
        return f"ResourceCollection({self.collection_type.__name__}, {repr(self._resource)})"

    @property
    @override
    def field_order(self) -> list[str]:
        return self._resource.field_order

    @property
    def used(self) -> bool:
        return self._resource.used

    @used.setter
    def used(self, value: bool):
        self._resource.used = value

    @property
    def collection_type(self) -> Type[set] | Type[list]:
        return self._collection_type

    @property
    def internal_type(self) -> Resource:
        return self._resource

    def __eq__(self, other):
        if isinstance(other, ResourceCollection):
            return (
                other.internal_type == self.internal_type
                and self.collection_type is other.collection_type
            )
        return False

    @property
    def name(self) -> str:
        return self._resource.name

    def get_effects(self) -> Mapping[EffName, Mapping[str, Effect]]:
        return self._resource.get_effects()

    def get_fields(self) -> Mapping[str, Field]:
        return self._resource.get_fields()

    def get_relations(self) -> Mapping[str, Relation]:
        return self._resource.get_relations()

    def get_rules(
        self,
    ) -> Mapping[RuleName, Rule | Mapping[str, Rule]]:
        return self._resource.get_rules()

    def get_global_names(self) -> Sequence[str]:
        return self._resource.get_global_names()

    def get_singular_relations(
        self,
    ) -> Mapping[str, Relation]:
        return self._resource.get_singular_relations()

    def resolve_path(self, path: list[str]):
        return self._resource.resolve_path(path)

    def compiled_name(self) -> str:
        return self._resource.compiled_name()

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        uniquity = {"uniqueItems": self._collection_type is set}
        return uniquity | {
            "type": "array",
            "items": self._resource.to_schema(),
        }


class ResourceTuple(Resource):
    def __init__(self, internal_types: list[Resource]):
        self._internal_types = internal_types

    def __repr__(self):
        return f"ResourceTuple({', '.join([repr(x) for x in self._internal_types])})"

    @property
    @override
    def field_order(self) -> list[str]:
        return [name for t in self._internal_types for name in t.field_order]

    @override
    def to_schema(self) -> dict[str, TypeAny]:
        return {
            "type": "array",
            "prefixItems": [t.to_schema() for t in self._internal_types],
            "uniqueItems": False,
        }

    @property
    def used(self) -> bool:
        for t in self._internal_types:
            return t.used
        return False

    @used.setter
    def used(self, value: bool):
        for t in self._internal_types:
            t.used = value

    @property
    @override
    def name(self) -> str:
        names = [t.name for t in self._internal_types]
        return f"tuple[{', '.join(names)}]"

    @property
    def internal_types(self) -> list[Resource]:
        return self._internal_types

    def get_effects(self) -> Mapping[EffName, Mapping[str, Effect]]:
        d = {}
        for t in self._internal_types:
            d = d | dict(t.get_effects())
        return d

    def get_fields(self) -> Mapping[str, Field]:
        d = {}
        for t in self._internal_types:
            d = d | dict(t.get_fields())
        return d

    def get_relations(self) -> Mapping[str, Relation]:
        d = {}
        for t in self._internal_types:
            d = d | dict(t.get_relations())
        return d

    def get_rules(
        self,
    ) -> Mapping[RuleName, Rule | Mapping[str, Rule]]:
        d = {}
        for t in self._internal_types:
            d = d | dict(t.get_rules())
        return d

    def get_global_names(self) -> Sequence[str]:
        d = set()
        for t in self._internal_types:
            d = d | set(t.get_global_names())
        return list(d)

    def get_singular_relations(self) -> Mapping[str, Relation]:
        d = {}
        for t in self._internal_types:
            d = d | dict(t.get_singular_relations())
        return d

    def resolve_path(self, path: list[str]):
        result = None
        for t in self._internal_types:
            result = t.resolve_path(path)
            if result != []:
                break
        return result

    def compiled_name(self) -> str:
        raise NotImplementedError()


class LayeredMapping(MutableMapping):
    def __init__(self, values: dict[str, TypeAny] = {}):
        self.__prev: LayeredMapping | None = None
        self.__values: dict[str, TypeAny] = dict(values)

    def __repr__(self) -> str:
        value_stack = [self.__values]
        prev = self.__prev
        while prev is not None:
            value_stack.append(prev.__values)
            prev = prev.__prev
        value_stack = list(reversed(value_stack))
        contents = [f"LayeredMapping({repr(value_stack[0])})"]
        for entry in value_stack[1:]:
            contents.append(f"layer({repr(entry)})")
        return ".".join(contents)

    def get(self, key: str, default: TypeAny | None = None) -> TypeAny | None:
        d = self.__prev.__values if self.__prev is not None else {}
        return self.__values.get(key, default) or d.get(key, default)

    def __getitem__(self, key: str, /) -> TypeAny:
        try:
            return self.__values[key]
        except KeyError:
            if self.__prev is not None:
                return self.__prev[key]
            raise KeyError(f"{key} not in layered mapping")

    def __setitem__(self, key: str, value: TypeAny, /) -> None:
        self.__values[key] = value

    def __delitem__(self, key: str, /) -> None:
        del self.__values[key]

    def __iter__(self) -> Iterator[str]:
        keys = list(self.__values)
        if self.__prev is not None:
            for key in self.__prev:
                if key not in keys:
                    keys.append(key)
        return iter(keys)

    def __len__(self) -> int:
        d = self.__values
        p = self.__prev
        while p is not None:
            d = d | p.__values
            p = p.__prev
        return len(d)

    def layer(self, values: dict[str, TypeAny] = {}):
        lm = LayeredMapping(values)
        lm.__prev = self
        return lm

    def copy(self) -> LayeredMapping:
        lm = LayeredMapping(self.__values)
        lm.__prev = self.__prev
        return lm


class ModuleDictionary(dict[Path, Module]):
    def __init__(self, *args, **kwargs):
        from ..types.builtins import functions, types

        super().__init__(*args, **kwargs)
        self._type_cache: dict[str, Sequence[Datum]] = {}
        self[Path("<builtins>")] = Module(
            types,
            functions,
            {},
        )

    def get_functions(
        self,
        name: str,
        keys: Sequence[Path],
    ) -> Sequence[Function]:
        sources = [Path("<builtins>")] + list(keys)
        return [
            mod.functions[name]
            for mod in [v for k, v in self.items() if k in sources]
            if name in mod.functions
        ]

    def get_resources(
        self,
        name: str,
        keys: Sequence[Path],
    ) -> Sequence[Resource]:
        return [
            mod.resources[name]
            for mod in [v for k, v in self.items() if k in keys]
            if name in mod.resources
        ]

    def get_types(
        self,
        keys: Sequence[Path],
        name: str | None = None,
    ) -> Sequence[Datum]:
        sources = [Path("<builtins>")] + list(keys)
        if name is None:
            return [
                t
                for mod in [v for k, v in self.items() if k in sources]
                for t in mod.types.values()
            ]

        return [
            mod.types[name]
            for mod in [v for k, v in self.items() if k in sources]
            if name in mod.types
        ]
