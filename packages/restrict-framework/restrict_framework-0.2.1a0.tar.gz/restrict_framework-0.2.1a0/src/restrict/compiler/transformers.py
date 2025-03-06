from __future__ import annotations

import re
from copy import copy
from itertools import chain
from pathlib import Path

import restrict.compiler.ast as ast

from .types import Datum, ModuleDictionary, Resource
from .walker_utils import EventMixin


class AstTransformer(EventMixin):
    snakifier = re.compile(r"(?<!^)(?=[A-Z])")
    errors = []

    def __init__(
        self,
        asts: dict[Path, ast.File],
        mods: ModuleDictionary,
        globals_: dict[str, Resource | Datum],
        root: Path,
    ):
        super().__init__()
        self._asts = asts
        self._mods = mods
        self._globals = globals_
        self._root = root

    def visit_file(
        self,
        file: ast.File,
    ) -> tuple[ast.File, dict[str, Resource | Datum]]:
        self.path = file.path
        return self.visit(file), self._globals

    def visit(self, node):
        res = node
        match type(node):
            case ast.Create:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("create", node):
                        values = {k: self._dispatch(v) for k, v in node.values.items()}
                    res = copy(node)
                    res.values = values
            case ast.DataComputedField:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("data_computed_field", node):
                        func = ast.PipedExprList([self._dispatch(x) for x in node.func])
                    res = copy(node)
                    res.func = func
            case ast.DataConstrainedField:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("data_constrained_field", node):
                        func = ast.PipedExprList([self._dispatch(x) for x in node.func])
                    res = copy(node)
                    res.func = func
            case ast.EffectsComputedField:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("effects_computed_field", node):
                        func = ast.PipedExprList([self._dispatch(x) for x in node.func])
                    res = copy(node)
                    res.func = func
            case ast.File:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("file", node):
                        with self.em("imports", node.imports):
                            imps = [self._dispatch(x) for x in node.imports]
                        with self.em("resources", node.resources):
                            ress = [self._dispatch(x) for x in node.resources]
                    res = ast.File(node.path, imps, ress)
                    for r in res.resources:
                        r.file = res
            case ast.Func:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("func", node):
                        args = [
                            ast.PipedExprList([self._dispatch(x) for x in arg])
                            for arg in node.args
                        ]
                    res = copy(node)
                    res.args = args
            case ast.Lit:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("lit", node):
                        res = self._node_dispatch(node)
            case ast.Modify:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("modify", node):
                        values = {k: self._dispatch(v) for k, v in node.values.items()}
                    res = copy(node)
                    res.values = values
            case ast.Ref:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("ref", node):
                        res = self._node_dispatch(node)
            case ast.Rel:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("rel", node):
                        res = self._node_dispatch(node)
            case ast.Res:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("resource", node):
                        with self.em("data", node.fields):
                            fields = {
                                k: self._dispatch(v) for k, v in node.fields.items()
                            }
                        with self.em("dnc", node.fields):
                            dnc = {k: self._dispatch(v) for k, v in node.dnc.items()}
                        with self.em("effects", node.fields):
                            effects = {
                                method: {k: self._dispatch(v) for k, v in sec.items()}
                                for method, sec in node.effects.items()
                            }
                        with self.em("security", node.fields):
                            rules = {
                                k: (
                                    self._dispatch(v)
                                    if not isinstance(v, dict)
                                    else {
                                        ik: self._dispatch(iv) for ik, iv in v.items()
                                    }
                                )
                                for k, v in node.rules.items()
                            }
                        with self.em("workflow", node.fields):
                            workflow = {
                                k: self._dispatch(v) for k, v in node.workflow.items()
                            }
                    res = copy(node)
                    res.fields = fields
                    res.dnc = dnc
                    res.effects = effects
                    res.rules = rules
                    res.workflow = workflow
            case ast.SecurityConstraintField:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("security_constrained_field", node):
                        func = ast.PipedExprList([self._dispatch(x) for x in node.func])
                    res = copy(node)
                    res.func = func
            case ast.Self:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("self", node):
                        res = self._node_dispatch(node)
            case ast.Selves:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("selves", node):
                        res = self._node_dispatch(node)
            case ast.TaggedLit:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("tagged_lit", node):
                        res = self._node_dispatch(node)
            case ast.Transition:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("transition", node):
                        mappings = {
                            k: self._dispatch(v) for k, v in node.mappings.items()
                        }
                    res = copy(node)
                    res.mappings = mappings
            case ast.TransitionComputedField:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("transition_computed_field", node):
                        func = ast.PipedExprList([self._dispatch(x) for x in node.func])
                    res = copy(node)
                    res.func = func
            case ast.Value:
                res = self._node_dispatch(node)
                if res == node:
                    with self.em("value", node):
                        res = self._node_dispatch(node)
        return res

    def _node_dispatch(self, node):
        node_name = self._snakify(node)
        if node_name != "file" and hasattr(self, f"visit_{node_name}"):
            return getattr(self, f"visit_{node_name}")(node)
        return node

    def _dispatch(self, node):
        node_name = self._snakify(node)
        if node_name != "file" and hasattr(self, f"visit_{node_name}"):
            return getattr(self, f"visit_{node_name}")(node)
        elif not node.is_leaf:
            return self.visit(node)
        else:
            return node

    def _snakify(self, node):
        name = type(node).__name__
        return self.snakifier.sub("_", name).lower()


class ReplaceRefsWithFuncParamRefsTransformer(AstTransformer):
    """Replaces Refs in Funcs to the specified FuncParam by checking the closures
    of the nested Func stack

    Requires: N/A
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._funcs = []

    def handle_func_start(self, node: ast.Func):
        self._funcs.append(node)

    def handle_func_end(self, _):
        self._funcs.pop()

    def visit_ref(self, node: ast.Ref):
        name = node.path[0]
        param: ast.FuncParam | None = None
        for func in reversed(self._funcs):
            for p in func.params:
                if p.name == name:
                    param = p
                    break
            if param is not None:
                return param.create_ref(node.path[1:])
        return node


class ReplaceRefsWithSelfsTransformer(AstTransformer):
    """Replaces Refs With Selfs if the beginning of the Ref refers
    to a key in the data or dnc sections

    Requires: N/A
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._names = set()

    def handle_resource_start(self, resource: ast.Res):
        self._names = set(chain(resource.fields, resource.dnc))

    def visit_ref(self, ref: ast.Ref):
        if ref.path[0] in self._names:
            return ast.Self(ref.path)
        return ref
