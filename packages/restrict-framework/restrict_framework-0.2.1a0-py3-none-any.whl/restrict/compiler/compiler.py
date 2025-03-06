from collections.abc import Sequence
from pathlib import Path

from .compiled import AppResource, App
from .exceptions.compile import InvalidFilePathError

from .ast import File
from .parsers import PlyRestrictParser, RestrictParser
from .resolver import FileResolver, RestrictFileResolver
from .transformers import (
    AstTransformer,
    ReplaceRefsWithFuncParamRefsTransformer,
    ReplaceRefsWithSelfsTransformer,
)
from .types import Datum, LayeredMapping, ModuleDictionary, Resource
from .visitors import (
    AstVisitor,
    CheckDataConstraintTypeVisitor,
    CheckEffectTypeMatchesFieldType,
    CheckForCyclesVisitor,
    CheckForDuplicateFieldAndResourceNamesVisitor,
    CheckSecurityConstraintTypeVisitor,
    CompilePipedExpressionListsToPythonFunctionsVisitor,
    CompileResourceVisitor,
    LoadGlobalsIntoBaseLayeredMapping,
    RepeatAggregateVisitor,
    ResolveBaseResourceTypeVisitor,
    ResolveCreateTypeVisitor,
    ResolveDataComputedFieldTypeVisitor,
    ResolveDataConstrainedFieldTypeVisitor,
    ResolveEffectFieldTypeVisitor,
    ResolveFuncFunctionVisitor,
    ResolveGlobalNamesFromRootVisitor,
    ResolveInheritedEffectsVisitor,
    ResolveInheritedFieldsVisitor,
    ResolveInheritedRelsVisitor,
    ResolveInheritedSecurityVisitor,
    ResolveLitTypeVisitor,
    ResolveModifyTypeVisitor,
    ResolveRefTypeVisitor,
    ResolveRelTypeVisitor,
    ResolveSelfPathTypesVisitor,
    ResolveSelvesResourceCollectionTypeVisitor,
    ResolveTaggedLitTypeVisitor,
    ResolveUsedResourcesVisitor,
    ResolveValueTypeVisitor,
    RestrictError,
)

__all__ = ["CompilationErrors", "RestrictCompiler"]


class CompilationErrors(ExceptionGroup):
    def __init__(self, message: str, exceptions: Sequence[RestrictError]):
        super().__init__(message, exceptions)


class RestrictCompiler:
    visitor_types: list[
        type[AstVisitor] | type[AstTransformer] | RepeatAggregateVisitor
    ] = [
        CheckForDuplicateFieldAndResourceNamesVisitor,
        ReplaceRefsWithFuncParamRefsTransformer,
        ReplaceRefsWithSelfsTransformer,
        ResolveDataConstrainedFieldTypeVisitor,
        ResolveRelTypeVisitor,
        ResolveCreateTypeVisitor,
        ResolveBaseResourceTypeVisitor,
        ResolveInheritedFieldsVisitor,
        ResolveInheritedRelsVisitor,
        ResolveInheritedEffectsVisitor,
        ResolveInheritedSecurityVisitor,
        ResolveUsedResourcesVisitor,
        # Following only visit used resources
        ResolveFuncFunctionVisitor,
        ResolveEffectFieldTypeVisitor,
        ResolveValueTypeVisitor,
        ResolveSelvesResourceCollectionTypeVisitor,
        RepeatAggregateVisitor(
            [
                ResolveSelfPathTypesVisitor,
                ResolveLitTypeVisitor,
                ResolveTaggedLitTypeVisitor,
                ResolveModifyTypeVisitor,
                ResolveGlobalNamesFromRootVisitor,
                ResolveRefTypeVisitor,
                CheckForCyclesVisitor,
                ResolveDataComputedFieldTypeVisitor,
            ],
            3,
        ),
        CheckDataConstraintTypeVisitor,
        CheckSecurityConstraintTypeVisitor,
        CheckEffectTypeMatchesFieldType,
        #
        CompilePipedExpressionListsToPythonFunctionsVisitor,
        CompileResourceVisitor,
        LoadGlobalsIntoBaseLayeredMapping,
    ]

    def __init__(
        self,
        *,
        resolver: FileResolver = RestrictFileResolver(),
        parser: RestrictParser = PlyRestrictParser().build(),
    ):
        self._resolver = resolver
        self._parser = parser

    def compile(self, root: Path, base_path: Path) -> App:
        if not root.is_relative_to(base_path):
            raise InvalidFilePathError(root, base_path)

        CompileResourceVisitor.context = LayeredMapping()

        asts, mod_paths, errors, source_order = self._parse_file_tree(root, base_path)
        mods = self._load_extensions(mod_paths)
        globals_ = {}

        root_app_path = self._as_app_path(root, base_path)
        self._run_steps(root_app_path, asts, mods, globals_, errors, source_order)

        if len(errors) > 0:
            raise CompilationErrors("cannot compile", errors)

        return App(CompileResourceVisitor.context, self._compile(asts))

    def _compile(self, asts: dict[Path, File]) -> dict[str, type[AppResource]]:
        resources = {}
        for file in asts.values():
            for resource in file.resources:
                if resource.compiled is not None:
                    resources[resource.compiled.__qualname__] = resource.compiled
        return resources

    def _run_steps(
        self,
        root: Path,
        asts: dict[Path, File],
        mods: ModuleDictionary,
        globals_: dict[str, Resource | Datum],
        errors: list[RestrictError],
        source_order: list[Path],
    ):
        for p in source_order:
            ast = asts[p]
            for visitor_type in self.visitor_types:
                visitor = visitor_type(asts, mods, globals_, root)
                ast, globals_ = visitor.visit_file(ast)
                asts[p] = ast
                errors.extend(visitor.errors)
                if len(errors) > 0:
                    return

    def _load_extensions(
        self,
        mod_paths: list[Path],
    ) -> ModuleDictionary:
        mods = ModuleDictionary()
        for mod_path in mod_paths:
            if mod_path in mods:
                continue
            mods[mod_path] = self._resolver.resolve_module(mod_path)
        return mods

    def _parse_file_tree(
        self,
        root: Path,
        base_path: Path,
    ) -> tuple[dict[Path, File], list[Path], list[RestrictError], list[Path]]:
        asts = {}
        mod_paths = []
        errors = []
        sources = [root.relative_to(base_path)]
        visited = []
        while len(sources):
            source = base_path / sources.pop(0)
            app_path = self._as_app_path(source, base_path)
            visited.append(app_path)
            if app_path in asts:
                continue
            content = self._resolver.resolve_file(source)
            file = self._parser.parse(content, app_path)
            errors.extend(self._parser.errors)
            if file is None:
                raise CompilationErrors(str(root), self._parser.errors)
            asts[app_path] = file
            sources.extend(
                [i for i, absolute in file.resolved_imports() if not absolute]
            )
            mod_paths.extend([i for i, absolute in file.resolved_imports() if absolute])
        return asts, mod_paths, errors, visited

    @staticmethod
    def _as_app_path(path: Path, base_path: Path):
        return Path("/" + path.relative_to(base_path).as_posix())
