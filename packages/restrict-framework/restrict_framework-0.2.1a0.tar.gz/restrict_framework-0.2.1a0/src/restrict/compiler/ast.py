from __future__ import annotations

import ast as pyast
import random
import string
from abc import ABC, abstractmethod
from collections.abc import (
    Callable,
    Generator,
    Mapping,
    MutableSequence,
    Sequence,
)
from copy import copy
from dataclasses import InitVar, dataclass
from decimal import Decimal
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Literal, Type, TypeVar, cast, override

from .compiled import AppResource
from .exceptions.compile import InvalidExpressionError
from .types import (
    Data,
    Datum,
    Effect,
    EffName,
    Field,
    FuncParam,
    Function,
    LayeredMapping,
    OptionalDatum,
    OptionalResource,
    ParameterizedFunction,
    Relation,
    Resource,
    ResourceCollection,
    Rule,
    RuleName,
)

# Data section
type DataConstraintExpr = (
    Lit
    | Func[Lit | Self | Value | Selves | TaggedLit | Value]
    | Self
    | Selves
    | TaggedLit
    | Value
)
type DataComputedExpr = (
    Lit | Func[Lit | Ref | Self | Selves | TaggedLit] | Ref | Self | Selves | TaggedLit
)
type DataField = DataConstrainedField | DataComputedField
type DataFields = dict[str, DataField]

# Dnc section
type Rels = Mapping[str, Relation]
type Dir = Literal["next", "previous", "root", "details", ""]

# Dnc and data sections
type CollectionType = Type[set] | Type[list] | None

# Effects section
type EffEntries = Mapping[str, Effect]
type Effects = Mapping[EffName, EffEntries]
type EffectsComputedExpr = (
    Create
    | Lit
    | Func[Create | Lit | Modify | Ref | Self | Selves | TaggedLit]
    | Modify
    | Ref
    | Self
    | Selves
    | TaggedLit
)

# Security section
type SecurityConstraintExpr = (
    Lit | Func[Lit | Ref | Self | TaggedLit] | Ref | Self | TaggedLit
)
type Rules = Mapping[RuleName, Rule | Mapping[str, Rule]]

# Workflow section
type TransitionComputedExpr = (
    Lit | Func[Lit | Ref | Self | Selves | TaggedLit] | Ref | Self | Selves | TaggedLit
)
type TransitionEntries = dict[str, TransitionComputedField]
type Transitions = dict[RuleName, Transition]
type TxDec = Literal["entrypoint", "alias", ""]


def rs(length):
    return "".join([random.choice(string.ascii_letters) for _ in range(length)])


class ResolveMixin:
    def resolve_type(self):
        return self.res  # type: ignore


class NodeMixin:
    @property
    def is_leaf(self) -> bool:
        return False


class LeafMixin(NodeMixin):
    @property
    def is_leaf(self) -> bool:
        return True


class ExprMarker(ResolveMixin, ABC):
    @abstractmethod
    def to_py(
        self,
        return_value: bool | None,
    ) -> pyast.expr | list[pyast.stmt]: ...

    def get_imports(self):
        return set()


class ResToResourceBridge(Resource):
    def __init__(self, resource: Res):
        self._resource = resource

    def __eq__(self, other):
        try:
            return self.compiled_name() == other.compiled_name()
        except (AttributeError, TypeError):
            return False

    @property
    def is_singleton(self) -> bool:
        if self._resource.base is not None:
            return self._resource.base._is_singleton
        return self._is_singleton

    @property
    @override
    def field_order(self) -> list[str]:
        return self._resource.field_sort or []

    @override
    def get_rules(
        self,
    ) -> Mapping[RuleName, Rule | Mapping[str, Rule]]:
        return self._resource.rules

    @override
    def get_effects(self) -> Mapping[EffName, Mapping[str, Effect]]:
        return self._resource.effects

    @override
    def get_fields(self) -> Mapping[str, Field]:
        if self._resource.fields_updated:
            return self._resource.fields

        base_fields = {}
        if self._resource.base is not None:
            base_fields = {
                k: copy(v) for k, v in self._resource.base.get_fields().items()
            }

        fields = {k: copy(v) for k, v in self._resource.fields.items()}
        return base_fields | fields

    @override
    def get_relations(self) -> Mapping[str, Relation]:
        if self._resource.dnc_updated:
            return self._resource.dnc

        base_rels = {}
        if self._resource.base is not None:
            base_rels = {
                k: copy(v) for k, v in self._resource.base.get_relations().items()
            }

        fields = {k: copy(v) for k, v in self._resource.dnc.items()}
        return base_rels | fields

    @override
    def resolve_path(self, path: list[str]):
        return self._resource.resolve_path(path)

    def __repr__(self):
        return f"Bridge<{self.compiled_name()}>"

    @override
    def get_singular_relations(self) -> Mapping[str, Relation]:
        base_rels = {}
        if self._resource.base is not None:
            base_rels = {
                k: v.clone() for k, v in self._resource.base.get_relations().items()
            }

        fields = base_rels | {k: v for k, v in self._resource.dnc.items()}
        return {k: v for k, v in fields.items() if not isinstance(v.res, Data)}

    @override
    def compiled_name(self) -> str:
        path = "?"
        if self._resource.file is not None:
            path = self._resource.file.path.as_posix()

        return path + "/" + self.name

    @override
    def get_global_names(self) -> Sequence[str]:
        if self._resource.base is None:
            return []

        return self._resource.base.get_global_names()

    @property
    @override
    def name(self) -> str:
        return self._resource.name

    @property
    @override
    def used(self) -> bool:
        return self._resource.used

    @used.setter
    @override
    def used(self, value: bool):
        self._resource.used = value

    @override
    def to_schema(self) -> dict[str, Any]:
        raise NotImplementedError()


@dataclass
class Ref(LeafMixin, ExprMarker):
    path: list[str]
    path_res: Sequence[Datum | Resource] | None = None

    @property
    def res(self):
        if self.path_res is not None:
            return self.path_res[-1]

    @override
    def to_py(self, return_value: bool | None) -> pyast.Subscript | pyast.Attribute:
        node = pyast.Subscript(
            value=pyast.Name(id="ctx", ctx=pyast.Load()),
            slice=pyast.Constant(value=self.path[0]),
            ctx=pyast.Load(),
        )
        for name in self.path[1:]:
            node = pyast.Attribute(value=node, attr=name, ctx=pyast.Load())
        return node


@dataclass
class TaggedLit(LeafMixin, ExprMarker):
    tag: str
    prefix: list[str]
    value: str
    res: Datum | None = None

    @override
    def get_imports(self):
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not happen)
        return self.res.get_imports()

    @override
    def to_py(self, return_value: bool | None) -> pyast.Call:
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not happen)
        value = self.res.parse(self.value)
        module = pyast.parse(repr(value))
        expr = cast(pyast.Expr, module.body[0])
        return cast(pyast.Call, expr.value)


@dataclass
class Lit(LeafMixin, ExprMarker):
    value: (
        str
        | bool
        | int
        | Decimal
        | list[str]
        | list[bool]
        | list[int]
        | list[Decimal]
        | set[str]
        | set[bool]
        | set[int]
        | set[Decimal]
    )
    res: Datum | None = None

    @override
    def to_py(self, return_value: bool | None) -> pyast.expr:
        if isinstance(self.value, Decimal):
            return pyast.Call(
                func=pyast.Name("Decimal", ctx=pyast.Load()),
                args=[pyast.Constant(str(self.value))],
                keywords=[],
            )
        elif isinstance(self.value, list):
            return pyast.List(
                elts=[pyast.Constant(value=v) for v in self.value],
                ctx=pyast.Load(),
            )
        elif isinstance(self.value, set):
            return pyast.Set(
                elts=[pyast.Constant(value=v) for v in self.value],
            )
        return pyast.Constant(value=self.value)


@dataclass
class Value(LeafMixin, ExprMarker):
    res: Datum | None = None

    @override
    def to_py(self, return_value: bool | None) -> pyast.Subscript:
        return pyast.Subscript(
            value=pyast.Name(id="ctx", ctx=pyast.Load()),
            slice=pyast.Constant(value="value"),
            ctx=pyast.Load(),
        )


@dataclass
class Self(LeafMixin, ExprMarker):
    path: list[str]
    path_res: Sequence[Datum | Resource] | None = None

    @property
    def res(self):
        if self.path_res is not None:
            return self.path_res[-1]

    @override
    def get_imports(self):
        return set(["operator"])

    @override
    def to_py(
        self,
        return_value: bool | None,
        dict_name: str = "ctx",
    ) -> pyast.Subscript | pyast.Attribute:
        node = pyast.Subscript(
            value=pyast.Name(id=dict_name, ctx=pyast.Load()),
            slice=pyast.Constant(value="self"),
            ctx=pyast.Load(),
        )
        for name in self.path:
            node = pyast.Attribute(value=node, attr=name, ctx=pyast.Load())
        return node


@dataclass
class Selves(LeafMixin, ExprMarker):
    res: ResourceCollection | None = None

    @override
    def to_py(self, return_value: bool | None) -> pyast.Call:
        return pyast.Call(
            func=pyast.Subscript(
                value=pyast.Name(id="ctx", ctx=pyast.Load()),
                slice=pyast.Constant(value="selves"),
                ctx=pyast.Load(),
            ),
            args=[],
            keywords=[],
        )


@dataclass
class Create(NodeMixin, ExprMarker):
    type: str
    prefix: str
    values: EffEntries
    res: Resource | None = None

    @override
    def to_py(self, return_value: bool | None):
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not occur)
        local = rs(10)
        statements: MutableSequence[pyast.stmt] = [
            pyast.Assign(
                targets=[pyast.Name(local, pyast.Store())],
                value=pyast.Call(
                    func=pyast.Attribute(
                        value=pyast.Name(id="ctx", ctx=pyast.Load()),
                        attr="copy",
                        ctx=pyast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            )
        ]
        for k, v in self.values.items():
            subscript = pyast.Subscript(
                value=pyast.Name(id=local, ctx=pyast.Load()),
                slice=pyast.Constant(value=k),
                ctx=pyast.Store(),
            )
            if isinstance(v, EffectsComputedField):
                py = v.func.treeify().to_py(return_value)
                if not isinstance(py, list):
                    statements.append(
                        pyast.Assign(
                            targets=[subscript],
                            value=py,
                        )
                    )
                else:
                    sub_name = rs(10)
                    statements.append(
                        pyast.FunctionDef(
                            name=sub_name,  # type: ignore
                            args=pyast.arguments(args=[pyast.arg(arg="ctx")]),  # type: ignore
                            body=py,
                        )
                    )
                    statements.append(
                        pyast.Assign(
                            targets=[subscript],
                            value=pyast.Call(
                                func=pyast.Name(id=sub_name, ctx=pyast.Load()),
                                args=[pyast.Name(id=local, ctx=pyast.Load())],
                                keywords=[],
                            ),
                        )
                    )
        statements.append(
            pyast.Return(
                value=pyast.Call(
                    func=pyast.Attribute(
                        value=pyast.Subscript(
                            value=pyast.Name(id=local, ctx=pyast.Load()),
                            slice=pyast.Constant(value=self.res.compiled_name()),
                            ctx=pyast.Load(),
                        ),
                        attr="_create",
                        ctx=pyast.Load(),
                    ),
                    args=[pyast.Name(id=local, ctx=pyast.Load())],
                    keywords=[],
                )
            )
        )
        return list(statements)


@dataclass
class Modify(NodeMixin, ExprMarker):
    ref: Self
    values: EffEntries
    res: Resource | None = None

    @override
    def to_py(self, return_value: bool | None):
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not occur)
        local = rs(10)
        statements: list[pyast.stmt] = [
            pyast.Assign(
                targets=[pyast.Name(local, pyast.Store())],
                value=pyast.Call(
                    func=pyast.Attribute(
                        value=pyast.Name(id="ctx", ctx=pyast.Load()),
                        attr="copy",
                        ctx=pyast.Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            )
        ]
        for k, v in self.values.items():
            subscript = pyast.Subscript(
                value=pyast.Name(id=local, ctx=pyast.Load()),
                slice=pyast.Constant(value=k),
                ctx=pyast.Store(),
            )
            if isinstance(v, EffectsComputedField):
                py = v.func.treeify().to_py(return_value)
                if not isinstance(py, list):
                    statements.append(
                        pyast.Assign(
                            targets=[subscript],
                            value=py,
                        )
                    )
                else:
                    sub_name = rs(10)
                    sub_local = rs(10)
                    statements.append(
                        pyast.FunctionDef(
                            name=sub_name,  # type: ignore
                            args=pyast.arguments(args=[pyast.arg(arg="ctx")]),  # type: ignore
                            body=py,
                        )
                    )
                    statements.append(
                        pyast.Assign(
                            targets=[pyast.Name(sub_local, pyast.Store())],
                            value=pyast.Call(
                                func=pyast.Attribute(
                                    value=pyast.Name(id="ctx", ctx=pyast.Load()),
                                    attr="copy",
                                    ctx=pyast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            ),
                        )
                    )
                    statements.append(
                        pyast.Assign(
                            targets=[subscript],
                            value=pyast.Call(
                                func=pyast.Name(id=sub_name, ctx=pyast.Load()),
                                args=[pyast.Name(id=sub_local, ctx=pyast.Load())],
                                keywords=[],
                            ),
                        )
                    )
        statements.append(
            pyast.Return(
                value=pyast.Call(
                    func=pyast.Attribute(
                        value=self.ref.to_py(return_value),
                        attr="_alter",
                        ctx=pyast.Load(),
                    ),
                    args=[pyast.Name(id=local, ctx=pyast.Load())],
                    keywords=[],
                )
            )
        )
        return statements


T = TypeVar("T", bound=ExprMarker, covariant=True)


@dataclass
class Func[T](NodeMixin, ExprMarker):
    name: str
    prefix: list[str]
    params: list[FuncParam]
    args: list[PipedExprList[T]]
    res: Function | None = None

    @override
    def to_py(self, return_value: bool | None) -> pyast.expr | list[pyast.stmt]:
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not happen)
        if not hasattr(self, "_type"):
            self.resolve_type()

        asts = [t.to_py(return_value) for t in self._trees]
        asts = [cast(pyast.expr, a) for a in asts if a is not None]
        return self.res.to_py(
            isinstance(self._type, OptionalDatum),
            asts,
            return_value,
        )

    @override
    def get_imports(self):
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not happen)
        values = set([self.res.module]) if len(self.res.module) > 0 else set()
        for a in self.args:
            imps = a.treeify().get_imports()
            if len(imps) > 0:
                values = values | imps
        return values

    @override
    def resolve_type(self):
        try:
            return self._type
        except AttributeError:
            pass
        if self.res is None:
            raise ValueError()  # pragma: nocover (should not happen)
        self._trees = [n.treeify() for n in self.args if n is not None]
        self._define_params(self.res)
        arg_types = [x.resolve_type() for x in self._trees]
        self._type = self.res.calculate_return_type(arg_types)
        return self._type

    @singledispatchmethod
    def _define_params(self, _) -> None:
        pass

    @_define_params.register
    def _(self, fn: ParameterizedFunction):
        fn.define_params(self.params)
        fn.prepare_params(self._trees[0].resolve_type())


@dataclass
class DataConstrainedField(NodeMixin, Field):
    type: str
    prefix: str
    is_optional: bool
    is_unique: bool
    collection: CollectionType
    func: PipedExprList[DataConstraintExpr]
    res: Datum | None = None  # type: ignore
    compiled: Callable[[LayeredMapping], Any] | None = None  # type: ignore

    @property
    def is_computed(self) -> bool:
        return False

    def __post_init__(self):
        super().__init__()


@dataclass
class DataComputedField(NodeMixin, Field):
    func: PipedExprList[DataComputedExpr]
    func_res: Datum | None = None
    compiled: Callable[[LayeredMapping], Any] | None = None  # type: ignore

    @property
    def res(self):  # type: ignore
        return self.func_res

    @property
    def is_computed(self) -> bool:
        return True

    def __post_init__(self):
        super().__init__()


@dataclass
class EffectsComputedField(NodeMixin, Effect):
    func: PipedExprList[EffectsComputedExpr]
    res: Resource | Datum | None = None  # type: ignore
    compiled: Callable[[LayeredMapping], Any] | None = None  # type: ignore


@dataclass
class SecurityConstraintField(NodeMixin, Rule):
    func: PipedExprList[SecurityConstraintExpr]
    compiled: Callable[[LayeredMapping], Any] | None = None  # type: ignore


@dataclass
class TransitionComputedField(NodeMixin):
    func: PipedExprList[TransitionComputedExpr]
    compiled: Callable[[LayeredMapping], Any] | None = None


class PipedExprList[T](list[T]):
    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return "PipedExprList(" + super().__repr__() + ")"

    def treeify(self, default=Lit(True)) -> ExprMarker:
        exprs = [x for x in self if x is not None]
        if len(exprs) > 0:
            try:
                return self._tree
            except AttributeError:
                pass
            expr: T = exprs[0]
            for next in exprs[1:]:
                c = copy(next)
                if not isinstance(c, Func):
                    raise InvalidExpressionError()
                new_list = [PipedExprList[T]([expr])]
                arg: PipedExprList[T]
                for arg in c.args:
                    new_list.append(arg)
                c.args = new_list
                expr = c
            self._tree = cast(ExprMarker, expr)
            return self._tree
        return default


@dataclass
class Rel(LeafMixin, Relation):
    type: str
    prefix: str
    is_optional: bool
    is_unique: bool
    collection: CollectionType
    cardinality: tuple[int, int | Literal["*"]] | None
    dir: Dir
    res_: InitVar[Resource | None] = None
    name_: InitVar[str] = ""

    def __post_init__(self, res_, name_):
        super().__init__(name_, res_)

    def clone(self):
        c = copy(self)
        c.res = self.res
        c.name = self.name
        return c


@dataclass
class Transition(NodeMixin):
    type: str
    prefix: str
    decorator: TxDec
    method: RuleName | Literal[""]
    mappings: TransitionEntries


@dataclass
class Res(NodeMixin):
    type: str
    name: str
    prefix: str
    override: bool
    fields: DataFields
    dnc: Rels
    effects: Effects
    rules: Rules
    workflow: Transitions
    base: Resource | None = None
    file: File | None = None
    used: bool = False
    fields_updated: bool = False
    dnc_updated: bool = False
    effects_updated: bool = False
    security_updated: bool = False
    compiled: type[AppResource] | None = None
    field_sort: list[str] | None = None

    @property
    def bridge(self) -> ResToResourceBridge:
        if not hasattr(self, "_bridge"):
            self._bridge = ResToResourceBridge(self)
        return self._bridge

    @property
    def source(self) -> Path:
        if self.file is None:
            raise ValueError("File is not resolved")
        return self.file.path

    def resolve_path(self, path: list[str]) -> list[Resource | Datum]:
        path_res: list[Resource | Datum] = [self.bridge]
        if len(path) > 0:
            head, *tail = path
            if len(tail) == 0 and head in self.fields:
                field = self.fields[head]
                res = field.res
                if res is not None:
                    path_res.append(res)
                elif isinstance(field, DataComputedField):
                    raise ValueError()
            elif len(tail) == 0 and head in self.dnc:
                res = self.dnc[head].res
                if res is not None:
                    path_res.append(res)
                else:
                    raise NotImplementedError()
            elif len(tail) > 0 and head in self.dnc:
                res = self.dnc[head].res
                if res is not None:
                    resolved = res.resolve_path(tail)
                    if resolved is not None:
                        first = resolved[0]
                        if isinstance(res, OptionalResource) and isinstance(
                            first, Resource
                        ):
                            resolved[0] = OptionalResource.wrap(first)
                        path_res.extend(resolved)
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()
        return path_res


@dataclass
class Import(LeafMixin):
    path: Path
    prefix: str


@dataclass
class File(NodeMixin):
    path: Path
    imports: list[Import]
    resources: list[Res]

    def get_imports(self, prefix: str):
        return [i for i in self.imports if i.prefix == prefix]

    def resolved_imports(self) -> Generator[tuple[Path, bool], None, None]:
        for imp in self.imports:
            if imp.path.as_posix().startswith("/"):
                yield imp.path, True
            else:
                yield imp.path.with_suffix(".restrict"), False
