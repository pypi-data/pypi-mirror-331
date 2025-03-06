from __future__ import annotations

import re
from abc import ABC, abstractmethod
from ast import (
    FunctionDef,
    Import,
    ImportFrom,
    Load,
    Module,
    Name,
    Return,
    alias,
    arg,
    arguments,
    fix_missing_locations,
    stmt,
)
from collections.abc import Callable, Mapping, Sequence
from copy import copy
from decimal import Decimal
from itertools import chain, groupby
from pathlib import Path
from typing import cast, override

import restrict.compiler.ast as ast
import restrict.compiler.types as types
from restrict.compiler.exceptions.runtime import ComputedFieldAssignmentError
from restrict.types.builtins import Boolean

from ..resources.specs import DataConstrainedField, SpecField, SpecResource
from ..types.numeric import Decimal_, Integer
from ..types.text import Text
from .compiled import (
    AppResource,
    CompSpec,
    FieldSpec,
    LayeredMapping,
    RelSpec,
    RestrictRuntimeErrorGroup,
)
from .exceptions.compile import (
    AmbiguousFunctionError,
    AmbiguousTagError,
    AmbiguousTypeError,
    CompileError,
    DuplicateGlobalNameError,
    DuplicatePropertyError,
    DuplicateResourceError,
    InvalidConstraintError,
    InvalidEffectError,
    InvalidExpressionError,
    InvalidFuncCallError,
    InvalidModifyCollectionError,
    InvalidModifyValueError,
    InvalidPathError,
    InvalidPrefixError,
    InvalidRefCollectionError,
    InvalidTaggedValue,
    ReferenceCycleError,
    RestrictError,
    UnknownFunctionError,
    UnknownPropertyError,
    UnknownTagError,
    UnknownTypeError,
)
from .walker_utils import EventMixin, visit_after

type PrefixedItems = (
    ast.Create
    | ast.DataConstrainedField
    | ast.Func
    | ast.Rel
    | ast.Res
    | ast.Transition
)


class AstVisitor(EventMixin):
    snakifier = re.compile(r"(?<!^)(?=[A-Z])")

    def __init__(
        self,
        asts: dict[Path, ast.File],
        mods: types.ModuleDictionary,
        globals_: dict[str, types.Resource | types.Datum],
        root: Path,
    ):
        super().__init__()
        self._asts = asts
        self._mods = mods
        self._globals = globals_
        self._errors = []
        self._path = Path("")
        self._root = root

    def visit_file(
        self,
        ast: ast.File,
    ) -> tuple[ast.File, dict[str, types.Resource | types.Datum]]:
        self._path = ast.path
        self.visit(ast)
        return ast, self._globals

    def visit(self, node):
        match type(node):
            case ast.DataComputedField:
                with self.em("data_computed_field", node):
                    with self.em("pel", node.func):
                        for expr in node.func:
                            self._dispatch_expr(expr)
            case ast.DataConstrainedField:
                with self.em("data_constrained_field", node):
                    with self.em("pel", node.func):
                        for expr in node.func:
                            self._dispatch_expr(expr)
            case ast.EffectsComputedField:
                with self.em("effects_computed_field", node):
                    with self.em("pel", node.func):
                        for expr in node.func:
                            self._dispatch_expr(expr)
            case ast.Create:
                with self.em("create", node):
                    with self.em("values", node.values):
                        for name, field in node.values.items():
                            self._dispatch(name, field)
            case ast.File:
                with self.em("file", node):
                    with self.em("imports", node.imports):
                        for import_ in node.imports:
                            self._dispatch(node.path, import_)
                    with self.em("resources", node.resources):
                        for resource in node.resources:
                            self._dispatch(resource.name, resource)
            case ast.Func:
                with self.em("func", node):
                    with self.em("args", node.args):
                        for arg in node.args:
                            with self.em("pel", arg):
                                for expr in arg:
                                    self._dispatch_expr(expr)
            case ast.Lit:
                with self.em("lit", node):
                    self._dispatch("", node)
            case ast.Modify:
                with self.em("modify", node):
                    with self.em("values", node.values):
                        for name, field in node.values.items():
                            self._dispatch(name, field)
            case ast.Ref:
                with self.em("ref", node):
                    self._dispatch("", node)
            case ast.Rel:
                with self.em("rel", node):
                    self._dispatch("", node)
            case ast.Res:
                with self.em("res", node):
                    with self.em("data", node.fields):
                        for name, field in node.fields.items():
                            self._dispatch(name, field)
                    with self.em("dnc", node.dnc):
                        for name, rel in node.dnc.items():
                            self._dispatch(name, rel)
                    with self.em("effects", node.effects):
                        for section_name, section in node.effects.items():
                            with self.em("effects_section_name", section_name):
                                for name, field in section.items():
                                    self._dispatch(name, field)
                    with self.em("security", node.rules):
                        for name, section in node.rules.items():
                            with self.em("security_section_name", name):
                                if isinstance(section, dict):
                                    for name, field in section.items():
                                        self._dispatch(name, field)
                                else:
                                    self._dispatch(name, section)
                    with self.em("workflow", node.workflow):
                        for name, field in node.workflow.items():
                            self._dispatch(name, field)
            case ast.ResToResourceBridge:
                self.visit(node._resource)
            case ast.SecurityConstraintField:
                with self.em("security_constrained_field", node):
                    with self.em("pel", node.func):
                        for expr in node.func:
                            self._dispatch_expr(expr)
            case ast.Self:
                with self.em("self", node):
                    self._dispatch("", node)
            case ast.Selves:
                with self.em("selves", node):
                    self._dispatch("", node)
            case ast.TaggedLit:
                with self.em("tagged_lit", node):
                    self._dispatch("", node)
            case ast.Transition:
                with self.em("transition", node):
                    with self.em("mappings", node.mappings):
                        for name, field in node.mappings.items():
                            self._dispatch(name, field)
            case ast.TransitionComputedField:
                with self.em("transition_computed_field", node):
                    with self.em("pel", node.func):
                        for expr in node.func:
                            self._dispatch_expr(expr)
            case ast.Value:
                with self.em("value", node):
                    self._dispatch("", node)

    def _dispatch(self, name: str, node):
        node_name = self._snakify(node)
        if node_name != "file" and hasattr(self, f"visit_{node_name}"):
            getattr(self, f"visit_{node_name}")(name, node)
        elif hasattr(node, "is_leaf") and not node.is_leaf:
            self.visit(node)

    def _dispatch_expr(self, expr):
        name = ""
        if hasattr(expr, "name"):
            name = expr.name
        self._dispatch(name, expr)

    def _snakify(self, node):
        name = type(node).__name__
        return self.snakifier.sub("_", name).lower()

    @property
    def errors(self) -> list[RestrictError]:
        return [x for x in self._errors]


class VisitUsedResourcesMixin:
    def visit_res(self, _, node: ast.Res):
        if node.used:
            self.visit(node)  # type: ignore


class AbstractResourceResolutionVisitor(AstVisitor, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file = ast.File(Path("<unknown>"), [], [])

    def handle_file_start(self, node: ast.File):
        self._file = node

    def _resolve(
        self,
        add_file_path: bool,
        node,
        key: str,
    ):
        e: RestrictError | None = None
        imports = self._file.get_imports(node.prefix)
        paths = [i.path for i in imports]
        if add_file_path and node.prefix == "":
            paths.append(self._file.path)

        resources = list(
            chain(
                self._mods.get_resources(key, paths),
                self._ast_lookup(key, paths),
            )
        )

        if len(resources) == 1:
            self._set(node, resources[0])
        elif len(resources) == 0:
            e = self._unknown(node)
        else:
            e = self._ambiguous(node, paths)
        if e is not None:
            self._errors.append(e)

    @abstractmethod
    def _set(self, node, resource: types.Resource): ...

    @abstractmethod
    def _unknown(self, node) -> UnknownTypeError: ...

    @abstractmethod
    def _ambiguous(self, node, paths: list[Path]) -> AmbiguousTypeError: ...

    def _ast_lookup(
        self,
        name: str,
        paths: Sequence[Path],
    ) -> Sequence[types.Resource]:
        return [
            resource.bridge
            for file in self._asts.values()
            for resource in file.resources
            if file.path in paths and resource.name == name
        ]


class CheckDataConstraintTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: N/A

    Requires: Func resolution
    """

    def handle_res_start(self, node: ast.Res):
        self._res_name = node.name

    def handle_res_end(self, _):
        self._res_name = ""

    def visit_data_constrained_field(
        self,
        name: str,
        node: ast.DataConstrainedField,
    ):
        t = node.func.treeify().resolve_type()
        if t != Boolean():
            e = InvalidConstraintError(
                [self._res_name, name],
                t.name,
                self._path,
            )
            self._errors.append(e)


class CheckEffectTypeMatchesFieldType(AstVisitor, VisitUsedResourcesMixin):
    def handle_res_start(self, node: ast.Res):
        self._res_name = node.name

    def handle_res_end(self, _):
        self._res_name = ""

    def handle_effects_section_name_start(self, name: str):
        self._sec_name = name

    def handle_effects_section_name_end(self, _):
        self._sec_name = ""

    def visit_effects_computed_field(
        self,
        name: str,
        node: ast.EffectsComputedField,
    ):
        t = node.func.treeify().resolve_type()
        if node.res is not None and node.res != t:
            e = InvalidEffectError(
                [self._res_name, self._sec_name, name],
                node.res.name,
                t.name,
                self._path,
            )
            self._errors.append(e)


class CheckForCyclesVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: N/A

    Requires: Self.path_res
              Ref.path_res
              Rel and Fields resolved from bases
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_path = []
        self._bad_paths = []
        self._resource = None

    @visit_after
    def visit_res(self, _, node: ast.Res):
        self._bad_paths = []
        self._resource = node

    def handle_res_end(self, _):
        if len(self._bad_paths) > 0:
            by_len = groupby(
                sorted(self._bad_paths, key=lambda x: (len(x), x[0])), key=len
            )
            bad_paths = []
            for _, grp in by_len:
                sets = []
                for p in grp:
                    sp = set(p)
                    if sp not in sets:
                        bad_paths.append(p)
                    sets.append(sp)
            res_name = ""
            if self._resource is not None:
                res_name = self._resource.name
            for bad_path in bad_paths:
                e = ReferenceCycleError(bad_path, res_name, self._path)
                self._errors.append(e)
        self._resource = None

    @visit_after
    def visit_data_constrained_field(self, name: str, _):
        self._current_path = [name]

    def handle_data_constrained_field_end(self, _):
        self._current_path = []

    @visit_after
    def visit_data_computed_field(self, name: str, _):
        self._current_path = [name]

    def handle_data_computed_field_end(self, _):
        self._current_path = []

    def visit_self(self, _, node: ast.Self):
        if len(self._current_path) > 0:
            if len(node.path) > 0 and node.path[0] == self._current_path[0]:
                self._bad_paths.append(self._current_path)
            elif len(node.path) > 0 and self._resource is not None:
                self._current_path.append(node.path[0])
                fields = self._resource.bridge.get_fields()
                field = fields.get(node.path[0])
                if field is not None:
                    if isinstance(field, ast.DataComputedField):
                        for part in field.func:
                            self.visit(part)
                    if isinstance(field, ast.DataConstrainedField):
                        for part in field.func:
                            self.visit(part)


class CheckForDuplicateFieldAndResourceNamesVisitor(AstVisitor):
    """Sets: N/A

    Requires: N/A
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._field_names = set()
        self._resource_names = set()

    def visit_data_constrained_field(self, name: str, _):
        if name in self._field_names:
            self._err(name)  # pragma: nocover (should not happen)
        self._field_names.add(name)

    def visit_data_computed_field(self, name: str, _):
        if name in self._field_names:
            self._err(name)  # pragma: nocover (should not happen)
        self._field_names.add(name)

    def visit_rel(self, name: str, _):
        if name in self._field_names:
            self._err(name)
        self._field_names.add(name)

    @visit_after
    def visit_res(self, name: str, _):
        if name in self._resource_names:
            e = DuplicateResourceError(name, self._path)
            self._errors.append(e)
        self._resource_names.add(name)

    def _err(self, name: str):
        e = DuplicatePropertyError(name, self._path)
        self._errors.append(e)


class CompilePipedExpressionListsToPythonFunctionsVisitor(
    AstVisitor,
    VisitUsedResourcesMixin,
):
    """Sets: DataConstrainedField.compiled
             DataComputedField.compiled
             EffectsComputedField.compiled
             SecurityConstraintField.compiled
             TODO: TransitionComputedField.compiled

    Requires: N/A
    """

    def handle_res_start(self, node: ast.Res):
        self._resource = node

    def handle_res_end(self, _):
        self._resource = None

    def visit_data_constrained_field(self, _, node: ast.DataConstrainedField):
        self._do_node(node, True)

    def visit_data_computed_field(self, _, node: ast.DataComputedField):
        self._do_node(node)

    def visit_effects_computed_field(self, _, node: ast.EffectsComputedField):
        self._do_node(node)

    def visit_security_constraint_field(
        self,
        _,
        node: ast.SecurityConstraintField,
    ):
        self._do_node(node, True)

    def _do_node(
        self,
        node: (
            ast.DataComputedField
            | ast.DataConstrainedField
            | ast.EffectsComputedField
            | ast.SecurityConstraintField
        ),
        return_value: bool | None = None,
    ):
        if node.compiled is not None:
            return

        for expr in node.func:
            self._dispatch_expr(expr)
        try:
            node.compiled = self._compile(node.func, return_value)
        except InvalidExpressionError as iee:
            self._errors.append(iee)
        except InvalidFuncCallError as ifc:
            res_name = ""
            if self._resource is not None:
                res_name = self._resource.name
            e = InvalidFuncCallError(
                ifc.name,
                ifc.expected_num_args,
                ifc.received_num_args,
                res_name,
                self._path,
            )
            self._errors.append(e)

    def _compile(self, func: ast.PipedExprList, return_value: bool | None):
        NAME = "expr"
        body = func.treeify().to_py(return_value)
        if not isinstance(body, list):
            body = cast(list[stmt], [Return(value=body)])
        mod_body: list[stmt] = [
            Import(names=[alias(name=x)]) for x in func.treeify().get_imports()
        ]
        mod_body.append(
            ImportFrom(
                module="decimal",
                names=[alias(name="Decimal")],
                level=0,
            )
        )
        mod_body.append(
            FunctionDef(  # type: ignore
                name=NAME,
                args=arguments(
                    posonlyargs=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                    args=[
                        arg(
                            arg="ctx",
                            annotation=Name(id="dict", ctx=Load()),
                        )
                    ],
                ),
                body=body,
                decorator_list=[],
                type_params=[],
            )
        )
        py = fix_missing_locations(Module(body=mod_body, type_ignores=[]))
        code_object = compile(py, self._path, "exec")

        globals_ = {}
        locals_ = {}
        exec(code_object, globals_, locals_)
        for k, v in locals_.items():
            if k == "expr":
                continue
            locals_["expr"].__globals__[k] = v
        return locals_[NAME]


class CompileResourceVisitor(AstVisitor):
    context = types.LayeredMapping()

    def visit_res(self, _, node: ast.Res):
        if not node.used or node.file is None:
            return

        self._resource = node
        field_order = []
        for name in node.field_sort or []:
            if name not in field_order:
                field_order.append(name)
        eval_order = [self._get_field_name(x) for x in field_order]
        init_layer = self.context.layer()

        init = self._get_init(init_layer, field_order, eval_order)

        try:
            # init = self._get_init(init_layer)
            fields = self._get_fields()
            rels = self._get_rels()
            attrs = {
                "__qualname__": node.bridge.compiled_name(),
                "__module__": node.file.path.as_posix(),
                "_is_singleton": node.bridge.is_singleton,
                "_eval_order": eval_order,
            }
            parents = (AppResource,)
            if node.base is not None and isinstance(node.base, SpecResource):
                parents = (type(node.base), AppResource)
            node.compiled = type(
                node.bridge.name,
                parents,
                fields | init | rels | attrs,
            )
            self.context[node.bridge.compiled_name()] = node.compiled
            self._globals = {
                key: node.compiled if value == node.bridge else value
                for key, value in self._globals.items()
            }
        except CompileError as ce:
            self._errors.append(ce)

    def _get_init(
        self,
        layer: LayeredMapping,
        field_order: list[str],
        eval_order: list[str],
    ):
        compiled_res_name = self._resource.bridge.compiled_name()
        entries = dict(self._resource.fields) | dict(self._resource.dnc)

        default_effects: dict[
            types.EffName, Callable[[LayeredMapping], bool] | None
        ] = {"create": None, "modify": None, "delete": None}
        effects = {x: default_effects.copy() for x in entries}
        for action, section in self._resource.effects.items():
            for key, effect in section.items():
                effects[key][action] = effect.compiled

        default_rules: dict[types.RuleName, Callable[[LayeredMapping], bool] | None] = {
            "list": None,
            "details": None,
            "create": None,
            "modify": None,
            "delete": None,
        }
        rules = {x: default_rules.copy() for x in entries}
        for action, section_or_rule in self._resource.rules.items():
            if isinstance(section_or_rule, types.Rule):
                for prop_rules in rules.values():
                    prop_rules[action] = section_or_rule.compiled
            else:
                for name, rule in section_or_rule.items():
                    field_rules = rules.setdefault(name, {})
                    field_rules[action] = rule.compiled
        for public in field_order:
            field = entries[public]

            if field.res is None:
                msg = f"Cannot compile {compiled_res_name}: {public} does not have a resovled type"
                e = CompileError(msg)
                self._errors.append(e)

            if (
                isinstance(field, DataConstrainedField)
                or (isinstance(field, SpecField) and not field.is_computed)
            ) and field.compiled is None:
                msg = f"Cannot compile {compiled_res_name}: {public} does not have a compiled constraint"
                e = CompileError(msg)
                self._errors.append(e)

        def __init__(self_):
            self_._layer = layer.layer({"self": self_})
            for public, private in zip(field_order, eval_order):
                field = entries[public]
                spec_layer = self_._layer.layer()

                is_optional = isinstance(field.res, types.OptionalDatum) or isinstance(
                    field.res, types.OptionalResource
                )
                spec = None
                if field.res is None:
                    continue

                if isinstance(field, types.Relation):
                    spec = RelSpec(
                        spec_layer,
                        compiled_res_name,
                        public,
                        is_optional,
                        field.res.compiled_name(),
                        effects[public],
                        rules[public],
                    )
                elif (
                    isinstance(field, ast.DataComputedField)
                    and field.compiled is not None
                ):
                    spec = CompSpec(
                        spec_layer,
                        compiled_res_name,
                        public,
                        field.res,
                        field.compiled,
                        effects[public],
                        rules[public],
                    )
                elif (
                    isinstance(field, ast.DataConstrainedField)
                    and field.compiled is not None
                ):
                    spec = FieldSpec(
                        spec_layer,
                        compiled_res_name,
                        public,
                        field.res,
                        field.compiled,
                        effects[public],
                        rules[public],
                    )
                elif (
                    isinstance(field, SpecField)
                    and field.is_computed
                    and field.compiled is not None
                ):
                    spec = CompSpec(
                        spec_layer,
                        compiled_res_name,
                        public,
                        field.res,
                        field.compiled,
                        effects[public],
                        rules[public],
                    )
                elif isinstance(field, SpecField) and field.compiled is not None:
                    spec = FieldSpec(
                        spec_layer,
                        compiled_res_name,
                        public,
                        field.res,
                        field.compiled,
                        effects[public],
                        rules[public],
                    )
                if spec is not None:
                    setattr(self_, private, spec)

        return {"__init__": __init__}

    def _get_fields(self):
        fields = {}

        def const_prop(name):
            field_name = self._get_field_name(name)

            def app_getter(self_):
                return getattr(self_, field_name).get()

            def app_setter(self_, value):
                try:
                    self_._alter_field(name, value)
                except RestrictRuntimeErrorGroup as rreg:
                    raise rreg.errors[0]

            return property(app_getter, app_setter)

        def comp_prop(name, res_name):
            field_name = self._get_field_name(name)

            def app_getter(self_):
                return getattr(self_, field_name).get()

            def app_setter(self_, *_):
                raise ComputedFieldAssignmentError(name, res_name)

            return property(app_getter, app_setter)

        for name, field in self._resource.fields.items():
            if isinstance(field, ast.DataConstrainedField):
                fields[name] = const_prop(name)
            else:
                fields[name] = comp_prop(name, self._resource.bridge.compiled_name())

        return fields

    def _get_rels(self):
        rels = {}

        for name in self._resource.dnc:
            field_name = self._get_field_name(name)

            def app_getter(self_):
                return getattr(self_, field_name).get()

            def app_setter(self_, value):
                try:
                    self_._alter_field(name, value)
                except RestrictRuntimeErrorGroup as rreg:
                    raise rreg.errors[0]

            rels[name] = property(app_getter, app_setter)

        return rels

    def _get_field_name(self, field_name):
        return f"_spec_{field_name}"


class CheckSecurityConstraintTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    def handle_res_start(self, node: ast.Res):
        self._res_name = node.name

    def handle_res_end(self, _):
        self._res_name = ""

    def handle_security_section_name_start(self, name: str):
        self._sec_name = name

    def handle_security_section_name_end(self, _):
        self._sec_name = ""

    def visit_security_constraint_field(
        self,
        name: str,
        node: ast.SecurityConstraintField,
    ):
        t = node.func.treeify().resolve_type()
        if t != Boolean():
            path = [self._res_name, self._sec_name]
            if name != self._sec_name:
                path.append(name)
            e = InvalidConstraintError(path, t.name, self._path)
            self._errors.append(e)


class LoadGlobalsIntoBaseLayeredMapping(AstVisitor, VisitUsedResourcesMixin):
    def __init__(
        self,
        asts: dict[Path, ast.File],
        mods: types.ModuleDictionary,
        globals_: dict[str, types.Resource | types.Datum],
        root: Path,
    ):
        super().__init__(asts, mods, globals_, root)
        for key, value in self._globals.items():
            if key not in CompileResourceVisitor.context:
                CompileResourceVisitor.context[key] = (
                    value._create({})
                    if isinstance(value, type) and issubclass(value, AppResource)
                    else value
                )
            else:
                e = DuplicateGlobalNameError(key)
                self._errors.append(e)

    def visit_file(
        self, ast: ast.File
    ) -> tuple[ast.File, dict[str, types.Resource | types.Datum]]:
        return ast, self._globals


class RepeatAggregateVisitor(AstVisitor, VisitUsedResourcesMixin):
    def __init__(self, visitor_types: list[type[AstVisitor]], num_times: int):
        self._visitor_types = visitor_types
        self._num_times = num_times

    def __call__(
        self,
        asts: dict[Path, ast.File],
        mods: types.ModuleDictionary,
        globals_: dict[str, types.Resource | types.Datum],
        root: Path,
    ):
        self._errors = []
        self._root = root
        self._asts = asts
        self._mods = mods
        self._globals = globals_
        return self

    def visit_file(
        self,
        ast: ast.File,
    ) -> tuple[ast.File, dict[str, types.Resource | types.Datum]]:
        errors = []
        for _ in range(self._num_times):
            errors = []
            for visitor_type in self._visitor_types:
                visitor = visitor_type(
                    self._asts,
                    self._mods,
                    self._globals,
                    self._root,
                )
                ast, self._globals = visitor.visit_file(ast)
                errors.extend(visitor.errors)
        if len(errors) > 0:
            self._errors = errors  # pragma: nocover
        return ast, self._globals


class ResolveBaseResourceTypeVisitor(AbstractResourceResolutionVisitor):
    """Sets: Res.base

    Requires: N/A
    """

    def visit_res(self, _, node: ast.Res):
        if node.override:
            self._resolve(False, node, node.name)

    @override
    def _set(self, node: ast.Res, resource: types.Resource):
        node.base = resource

    @override
    def _unknown(self, node: ast.Res):
        return UnknownTypeError(node.name, node.prefix, self._path)

    @override
    def _ambiguous(self, node: ast.Res, paths: list[Path]) -> AmbiguousTypeError:
        return AmbiguousTypeError(node.name, paths, self._path)


class ResolveCreateTypeVisitor(AbstractResourceResolutionVisitor):
    """Sets: Create.res

    Requires: N/A
    """

    def visit_create(self, _, node: ast.Create):
        self._resolve(True, node, node.type)

    @override
    def _set(self, node: ast.Create, resource: types.Resource):
        node.res = resource

    @override
    def _unknown(self, node: ast.Create):
        return UnknownTypeError(node.type, node.prefix, self._path)

    @override
    def _ambiguous(self, node: ast.Create, paths: list[Path]) -> AmbiguousTypeError:
        return AmbiguousTypeError(node.type, paths, self._path)


class ResolveDataConstrainedFieldTypeVisitor(AstVisitor):
    """Sets: DataConstrainedField.res

    Requires: N/A
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file = ast.File(Path("<unknown>"), [], [])

    def handle_file_start(self, node: ast.File):
        self._file = node

    def visit_data_constrained_field(self, _, node: ast.DataConstrainedField):
        e: RestrictError | None = None
        imports = self._file.get_imports(node.prefix)
        paths = [i.path for i in imports]
        types_ = self._mods.get_types(paths, node.type)
        if len(types_) == 1:
            node.res = types_[0]
            if node.collection is not None:
                node.res = types.Data(
                    node.collection,
                    node.res,
                )
            if node.is_optional:
                node.res = types.OptionalDatum(node.res)
        elif len(types_) == 0:
            e = UnknownTypeError(node.type, node.prefix, self._path)
        else:
            e = AmbiguousTypeError(node.type, paths, self._path)
        if e is not None:
            self._errors.append(e)


class ResolveDataComputedFieldTypeVisitor(AstVisitor):
    """Sets: DataComputedField.func_res

    Requires: Lit.res, Func.res, Ref.res, Self.res, Selves.res, TaggedLit.res
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._adj_list: dict[str, list[tuple[str, bool]]] = {}
        self._current_name = ""
        self._node_sort = []
        self._sorted = False

    def visit_res(self, _, node: ast.Res):
        if not node.used:
            return

        self._adj_list: dict[str, list[tuple[str, bool]]] = {}
        self._current_name = ""
        self._dcsf_list = []
        self._rel_list = []
        self._node_sort = []
        self._sorted = False
        self.visit(node)
        self._topo_sort()
        node.field_sort = self._dcsf_list + self._rel_list + self._node_sort
        if node.base is not None:
            node.field_sort += node.base.field_order
        for key in self._node_sort:
            field = node.fields[key]
            self._dispatch(key, field)
            self_visitor = ResolveSelfPathTypesVisitor(
                self._asts, self._mods, self._globals, self._root
            )
            self_visitor.visit(node)

    def visit_data_computed_field(self, name: str, node: ast.DataComputedField):
        self._current_name = name
        if not self._sorted:
            self._adj_list[self._current_name] = []
            self.visit(node)
        elif node.func_res is None:
            node.func_res = node.func.treeify().resolve_type()

    def handle_data_computed_field_end(self, _):
        self._current_name = ""

    def visit_data_constrained_field(self, name: str, _):
        self._dcsf_list.append(name)

    def visit_rel(self, name: str, _):
        self._rel_list.append(name)

    def visit_self(self, _, node: ast.Self):
        if len(node.path) > 0 and not self._sorted and self._current_name != "":
            self._adj_list[self._current_name].append(
                (
                    node.path[0],
                    node.res is not None,
                )
            )

    def _topo_sort(self):
        adj_list = {k: [(x, y) for x, y in v] for k, v in self._adj_list.items()}
        keys = list(sorted(adj_list.keys()))
        for _ in range(len(adj_list)):
            for key in keys:
                if all([x[1] for x in adj_list[key]]):
                    self._node_sort.append(key)
                    adj_list = {
                        k: [(x, y or x in self._node_sort) for x, y in v]
                        for k, v in adj_list.items()
                    }
            for key in self._node_sort:
                try:
                    keys.remove(key)
                except ValueError:
                    pass
        self._sorted = True


class ResolveEffectFieldTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    def handle_res_start(self, node: ast.Res):
        self._resource = node

    def handle_res_end(self, _):
        self._resource = None

    def handle_effects_section_name_start(self, name: str):
        self._sec_name = name

    def handle_effects_section_name_end(self, _):
        self._sec_name = ""

    def visit_effects_computed_field(
        self,
        name: str,
        node: ast.EffectsComputedField,
    ):
        if self._resource is not None:
            if name in self._resource.fields:
                field = self._resource.fields[name]
                if isinstance(field, ast.DataConstrainedField):
                    node.res = self._resource.fields[name].res
                else:
                    e = InvalidEffectError(
                        [self._resource.name, "effects", self._sec_name, name],
                        "static",
                        "computed",
                        self._path,
                    )
                    self._errors.append(e)
            elif name in self._resource.dnc:
                node.res = self._resource.dnc[name].res
            else:
                path = ".".join([self._resource.name, "effects", self._sec_name, name])
                section = ".".join([self._resource.name, "effects", self._sec_name])
                e = UnknownPropertyError(
                    name, section, self._resource.name, path, self._path
                )
                self._errors.append(e)


class ResolveFuncFunctionVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: Func.res

    Requires: RestrictModuleResource.used
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file = ast.File(Path("<unknown>"), [], [])

    def handle_file_start(self, node: ast.File):
        self._file = node

    def visit_func(self, _, node: ast.Func):
        e: RestrictError | None = None
        if len(node.prefix) < 2:
            prefix = node.prefix[0] if len(node.prefix) == 1 else ""
            imports = self._file.get_imports(prefix)
            paths = [i.path for i in imports]
            types = self._mods.get_functions(node.name, paths)
            if len(types) == 1:
                node.res = types[0].clone()
            elif len(types) == 0:
                e = UnknownFunctionError(node.name, self._path)
            else:
                e = AmbiguousFunctionError(node.name, paths, self._path)
        else:
            e = InvalidPrefixError(node.prefix, self._path)
        if e is not None:
            self._errors.append(e)


class ResolveGlobalNamesFromRootVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: Lit.res

    Requires: RestrictModuleResource.used
              Fields and DNC updated with base properties
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        file = self._asts[self._root]
        for res in file.resources:
            if res.used and res.base is not None:
                names = res.bridge.get_global_names()
                global_fields: dict[str, types.Datum] = {
                    k: v.res
                    for k, v in res.fields.items()
                    if k in names and v.res is not None
                }
                global_relations: dict[str, types.Resource] = {
                    k: v.bridge if isinstance(v, ast.Res) else v.res
                    for k, v in res.dnc.items()
                    if k in names
                }
                self._globals = self._globals | global_relations | global_fields
                for name in names:
                    if name not in self._globals:
                        e = UnknownPropertyError(
                            name,
                            "dnc",
                            res.base.name,
                            res.name,
                            file.path,
                        )
                        self._errors.append(e)

    @override
    def visit_file(
        self,
        ast: ast.File,
    ) -> tuple[ast.File, dict[str, types.Resource | types.Datum]]:
        return ast, self._globals


class ResolveInheritedEffectsVisitor(AstVisitor):
    """Sets: Res.effects

    Requires: RestrictModuleResource.base
    """

    def visit_res(self, _, node: ast.Res):
        if node.base is not None:
            new_effects = {sec: copy(v) for sec, v in node.base.get_effects().items()}
            old_effects = dict(node.effects)
            for sec in old_effects:
                if sec in new_effects:
                    old_effects[sec] = dict(new_effects[sec]) | dict(old_effects[sec])
            for sec in new_effects:
                sec = cast(ast.EffName, sec)
                if sec not in old_effects:
                    old_effects[sec] = new_effects[sec]
            node.effects = old_effects
        node.effects_updated = True


class ResolveInheritedFieldsVisitor(AstVisitor):
    """Sets: Res.fields

    Requires: RestrictModuleResource.base
    """

    def visit_res(self, _, node: ast.Res):
        if node.base is not None:
            new_fields = {k: copy(v) for k, v in node.base.get_fields().items()}
            node.fields = cast(ast.DataFields, new_fields | node.fields)
        node.fields_updated = True


class ResolveInheritedRelsVisitor(AstVisitor):
    """Sets: Res.dnc

    Requires: RestrictModuleResource.base
    """

    def visit_res(self, _, node: ast.Res):
        if node.base is not None:
            new_rels = {k: copy(v) for k, v in node.base.get_relations().items()}
            node.dnc = new_rels | dict(node.dnc)
        node.dnc_updated = True


class ResolveInheritedSecurityVisitor(AstVisitor):
    """Sets: Res.rules

    Requires: RestrictModuleResource.base
    """

    def visit_res(self, _, node: ast.Res):
        if node.base is not None:
            base_rules: ast.Rules = {
                sec: copy(v) for sec, v in node.base.get_rules().items()
            }
            old_rules = dict(node.rules)
            sec: ast.RuleName
            for sec in old_rules:
                if sec in base_rules:
                    new_rule = base_rules[sec]
                    old_rule = old_rules.get(sec, {})
                    if isinstance(new_rule, Mapping) and isinstance(old_rule, Mapping):
                        old_rules[sec] = dict(new_rule) | dict(old_rule)
            for sec in base_rules:
                if sec not in old_rules:
                    old_rules[sec] = base_rules[sec]
            node.rules = old_rules
        node.security_updated = True


class ResolveLitTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: Lit.res

    Requires: RestrictModuleResource.used
    """

    def visit_lit(self, _, node: ast.Lit):
        if node.res is None:
            if type(node.value) is list:
                node.res = types.Data(
                    list,
                    self._scalar(list(node.value)[0]),
                )
            elif type(node.value) is set:
                node.res = types.Data(
                    set,
                    self._scalar(list(node.value)[0]),
                )
            else:
                node.res = self._scalar(node.value)  # type: ignore

    def _scalar(self, value: bool | int | Decimal | str):
        t = type(value)
        if t is bool:
            return Boolean()
        if t is int:
            return Integer()
        if t is Decimal:
            return Decimal_()
        if t is str:
            return Text()
        raise ValueError("Invalid literal value")  # pragma: nocover


class ResolveModifyTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: Modify.res

    Requires: Rel.res, RestrictModuleResource.used
    """

    def handle_res_start(self, node: ast.Res):
        self._resource = node
        self._stack: list[types.Resource] = [node.bridge]

    def handle_res_end(self, _):
        self._resource = None
        self._stack = []

    def visit_modify(self, _, node: ast.Modify):
        if node.res is None:
            scope = self._stack[-1]
            rels = scope.get_singular_relations()
            try:
                target = rels[node.ref.path[0]].res
                if not isinstance(target, types.ResourceCollection):
                    if not isinstance(target, types.Resource):
                        e = InvalidModifyValueError(
                            node.ref.path[0],
                            self._resource.name,  # type: ignore
                            self._path,
                        )
                        self._errors.append(e)
                    else:
                        node.res = target
                        self._stack.append(target)
                        self.visit(node)
                        self._stack.pop()
                else:
                    raise KeyError()
            except KeyError:
                e = InvalidModifyCollectionError(
                    node.ref.path[0],
                    self._resource.name,  # type: ignore
                    self._path,
                )
                self._errors.append(e)


class ResolveRefTypeVisitor(AstVisitor):
    """Sets Ref.path_res

    Requires: globals
    """

    def handle_res_start(self, node: ast.Res):
        self._resource = node

    def handle_res_end(self, _):
        self._resource = None

    def visit_ref(self, _, node: ast.Ref):
        if node.path_res is None:
            res_name = ""
            if self._resource is not None:
                res_name = self._resource.name
            target = self._globals.get(node.path[0])
            if target is not None:
                res: list[types.Datum | types.Resource] = [target]
                e = None

                if len(node.path) > 1:
                    for part in node.path[1:-1]:
                        is_collection = isinstance(target, types.ResourceCollection)
                        is_not_resource = not isinstance(target, types.Resource)
                        if is_collection or is_not_resource:
                            e = InvalidRefCollectionError(
                                node.path,
                                res_name,
                                self._path,
                            )
                        elif isinstance(target, types.Resource):
                            rels = target.get_relations()
                            target = rels[part].res
                            res.append(target)

                    if (
                        e is None
                        and isinstance(target, types.Resource)
                        and not isinstance(target, types.ResourceCollection)
                    ):
                        part = node.path[-1]
                        rels = target.get_relations()
                        fields = target.get_fields()
                        if part in rels:
                            res.append(rels[part].res)
                        elif part in fields:
                            res.append(fields[part].res)
                    elif e is None:
                        e = InvalidRefCollectionError(node.path, res_name, self._path)

                if e is None:
                    node.path_res = res
                else:
                    self._errors.append(e)


class ResolveRelTypeVisitor(AbstractResourceResolutionVisitor):
    """Sets: DataConstrainedField.res

    Requires: N/A
    """

    def visit_rel(self, _, node: ast.Rel):
        self._resolve(True, node, node.type)

    @override
    def _set(self, node: ast.Rel, resource: types.Resource):
        value = resource
        node.res = (
            types.ResourceCollection(
                node.collection,
                value,
            )
            if node.collection is not None
            else value
        )

    @override
    def _unknown(self, node: ast.Rel):
        return UnknownTypeError(node.type, node.prefix, self._path)

    @override
    def _ambiguous(self, node: ast.Rel, paths: list[Path]) -> AmbiguousTypeError:
        return AmbiguousTypeError(node.type, paths, self._path)


class ResolveSelfPathTypesVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: Self.path_res

    Requires: RestrictModuleResource.used
              DataConstrainedField.res
              DataComputedField.func_res
              Rel.res
              Res.base
    """

    def handle_res_start(self, node: ast.Res):
        self._resource = node

    def handle_res_end(self, _):
        self._resource = None

    def visit_self(self, _, node: ast.Self):
        if self._resource is not None and node.path_res is None:
            try:
                node.path_res = self._resource.resolve_path(node.path)
                is_optional = False
                for i, p in enumerate(node.path_res[1:-1]):
                    if not is_optional and isinstance(p, types.OptionalResource):
                        is_optional = True
                    elif is_optional and isinstance(p, types.Resource):
                        node.path_res[i + 1] = types.OptionalResource.wrap(p)
                last = node.path_res[-1]
                if is_optional and isinstance(last, types.Datum):
                    node.path_res[-1] = types.OptionalDatum.wrap(last)
                elif is_optional and isinstance(last, types.Resource):
                    node.path_res[-1] = types.OptionalResource.wrap(last)
            except NotImplementedError:
                e = InvalidPathError("self", node.path, self._path)
                self._errors.append(e)
            except ValueError:
                node.path_res = None


class ResolveSelvesResourceCollectionTypeVisitor(
    AstVisitor,
    VisitUsedResourcesMixin,
):
    """Sets: Selves.res

    Requires: RestrictModuleResource.used
    """

    def handle_res_start(self, node: ast.Res):
        self._resource = node

    def handle_res_end(self, _):
        self._resource = None

    def visit_selves(self, _, node: ast.Selves):
        if self._resource is not None and node.res is None:
            coll = types.ResourceCollection(list, self._resource.bridge)
            node.res = coll


class ResolveTaggedLitTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: TaggedLit.res

    Requires: RestrictModuleResource.used
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file = ast.File(Path("<unknown>"), [], [])

    def handle_file_start(self, node: ast.File):
        self._file = node

    def visit_tagged_lit(self, _, node: ast.TaggedLit):
        e: RestrictError | None = None
        if len(node.prefix) < 2 and node.res is None:
            prefix = "" if len(node.prefix) == 0 else node.prefix[0]
            imports = self._file.get_imports(prefix)
            paths = [i.path for i in imports]
            types = [
                t for t in self._mods.get_types(paths) if t.can_handle_tag(node.tag)
            ]
            if len(types) == 1 and types[0].can_handle_value(node.value):
                node.res = types[0]
            elif len(types) == 1:
                e = InvalidTaggedValue(
                    node.tag,
                    node.value,
                    types[0].name,
                    self._path,
                )
            elif len(types) == 0:
                e = UnknownTagError(node.tag, prefix, self._path)
            else:
                e = AmbiguousTagError(node.tag, prefix, self._path)
        elif node.res is None:
            e = InvalidPrefixError(node.prefix, self._path)

        if e is not None:
            self._errors.append(e)


class ResolveUsedResourcesVisitor(AstVisitor):
    """Sets: RestrictModuleResource.used

    Requires: Rel.res, Res.base
    """

    @visit_after
    def visit_res(self, _, node: ast.Res):
        self._resource = node
        if self._path == self._root:
            node.used = True
            if node.base is not None:
                self._mark_targets(node.base)

    def visit_rel(self, _, node: ast.Rel):
        res = node.res
        if res is not None and not res.used:
            res.used = self._resource.used
            if res.used:
                if isinstance(node.res, types.Resource):
                    self._mark_targets(node.res)
                self.visit(node.res)

    def _mark_targets(self, mod: types.Resource):
        targets = list(r.res for r in mod.get_singular_relations().values())
        visited = set()
        while len(targets) > 0:
            target = targets.pop(0)
            if id(target) in visited:
                continue
            visited.add(id(target))
            target.used = True
            if isinstance(target, types.Resource):
                targets.extend(r.res for r in target.get_singular_relations().values())


class ResolveValueTypeVisitor(AstVisitor, VisitUsedResourcesMixin):
    """Sets: Value.res

    Requires: DataConstrainedField.res, RestrictModuleResource.used
    """

    def visit_data_constrained_field(self, _, node: ast.DataConstrainedField):
        self._field = node
        if self._field.res is not None:
            self.visit(node)
        self._field = None

    def visit_value(self, _, node: ast.Value):
        if self._field is not None:
            node.res = self._field.res
