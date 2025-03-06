from collections.abc import Sequence
from pathlib import Path

from ..ply.lex import LexToken


class RestrictError(Exception):
    pass


class AmbiguousFunctionError(RestrictError):
    def __init__(self, name: str, sources: Sequence[Path], source: Path):
        super().__init__(name, sources, source)

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def sources(self) -> list[Path]:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class AmbiguousTagError(RestrictError):
    def __init__(self, tag: str, prefix: str, source: Path):
        super().__init__(tag, prefix, source)

    @property
    def tag(self) -> str:
        return self.args[0]

    @property
    def prefix(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class AmbiguousTypeError(RestrictError):
    def __init__(self, name: str, sources: list[Path], source: Path):
        super().__init__(name, sources, source)

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def sources(self) -> list[Path]:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class CompileError(RestrictError):
    def __init__(self, message: str):
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0]


class DuplicateGlobalNameError(RestrictError):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def name(self) -> str:
        return self.args[0]


class DuplicatePropertyError(RestrictError):
    def __init__(self, name: str, source: Path):
        super().__init__(name, source)

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def source(self) -> Path:
        return self.args[1]


class DuplicateResourceError(RestrictError):
    def __init__(self, name: str, source: Path):
        super().__init__(name, source)

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def source(self) -> Path:
        return self.args[1]


class FileResolutionError(RestrictError):
    def __init__(self, path: Path, reason: str, cause: Exception | None = None):
        super().__init__(path, reason, cause)

    @property
    def path(self) -> Path:
        return self.args[0]

    @property
    def reason(self) -> str:
        return self.args[1]

    @property
    def cause(self) -> str:
        return self.args[2]


class InvalidFuncCallError(RestrictError):
    def __init__(
        self,
        name: str,
        expected_num_args: int,
        received_num_args: int,
        resource: str | None,
        source: Path | None,
    ):
        super().__init__(
            name,
            expected_num_args,
            received_num_args,
            resource,
            source,
        )

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def expected_num_args(self) -> int:
        return self.args[1]

    @property
    def received_num_args(self) -> int:
        return self.args[2]

    @property
    def resource(self) -> str | None:
        return self.args[3]

    @property
    def source(self) -> Path | None:
        return self.args[4]


class InvalidRefCollectionError(RestrictError):
    def __init__(self, path: list[str], resource: str, source: Path):
        super().__init__(".".join(path), resource, source)

    @property
    def path(self) -> str:
        return self.args[0]

    @property
    def resource(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class InvalidModifyCollectionError(RestrictError):
    def __init__(self, prop: str, resource: str, source: Path):
        super().__init__(prop, resource, source)

    @property
    def prop(self) -> str:
        return self.args[0]

    @property
    def resource(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class InvalidModifyValueError(RestrictError):
    def __init__(self, prop: str, resource: str, source: Path):
        super().__init__(prop, resource, source)

    @property
    def prop(self) -> str:
        return self.args[0]

    @property
    def resource(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class InvalidExpressionError(RestrictError):
    pass


class InvalidPrefixError(RestrictError):
    def __init__(self, prefix: list[str], source: Path):
        super().__init__(".".join(prefix), source)

    @property
    def prefix(self) -> str:
        return self.args[0]

    @property
    def source(self) -> Path:
        return self.args[1]


class InvalidFilePathError(RestrictError):
    def __init__(self, path: Path, base_path: Path):
        super().__init__(path, base_path)

    @property
    def path(self) -> Path:
        return self.args[0]

    @property
    def base_path(self) -> Path:
        return self.args[1]


class InvalidPathError(RestrictError):
    def __init__(self, root: str, path: list[str], source: Path):
        super().__init__(root + "." + ".".join(path), source)

    @property
    def reference(self) -> str:
        return self.args[0]

    @property
    def source(self) -> Path:
        return self.args[1]


class InvalidConstraintError(RestrictError):
    def __init__(self, path: list[str], type: str, source: Path):
        super().__init__(".".join(path), type, source)

    @property
    def path(self) -> str:
        return self.args[0]

    @property
    def type(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class InvalidEffectError(RestrictError):
    def __init__(
        self,
        path: list[str],
        expected_type: str,
        received_type: str,
        source: Path,
    ):
        super().__init__(".".join(path), expected_type, received_type, source)

    @property
    def path(self) -> str:
        return self.args[0]

    @property
    def expected_type(self) -> str:
        return self.args[1]

    @property
    def received_type(self) -> str:
        return self.args[2]

    @property
    def source(self) -> Path:
        return self.args[3]


class InvalidTaggedValue(RestrictError):
    def __init__(self, tag: str, value: str, type: str, source: Path):
        super().__init__(tag, value, type, source)

    @property
    def tag(self) -> str:
        return self.args[0]

    @property
    def value(self) -> str:
        return self.args[1]

    @property
    def type(self) -> str:
        return self.args[2]

    @property
    def source(self) -> Path:
        return self.args[3]


class ModuleResolutionError(RestrictError):
    def __init__(
        self,
        path: Path,
        mod_path: str,
        reason: str,
        cause: Exception | None = None,
    ):
        super().__init__(path, reason, cause, mod_path)

    @property
    def path(self) -> Path:
        return self.args[0]

    @property
    def reason(self) -> str:
        return self.args[1]

    @property
    def cause(self) -> str:
        return self.args[2]

    @property
    def mod_path(self) -> str:
        return self.args[3]


class ParsingError(RestrictError):
    def __init__(self, token: LexToken):
        super().__init__(token)

    @property
    def token(self) -> LexToken:
        return self.args[0]


class ReferenceCycleError(RestrictError):
    def __init__(self, path: list[str], res: str, source: Path):
        super().__init__("->".join(path), res, source)

    @property
    def path(self) -> str:
        return self.args[0]

    @property
    def resource(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class UnknownFunctionError(RestrictError):
    def __init__(self, name: str, source: Path):
        super().__init__(name, source)

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def source(self) -> Path:
        return self.args[1]


class UnknownPropertyError(RestrictError):
    def __init__(
        self,
        prop_name: str,
        section: str,
        src_res_name: str,
        ref_res_name: str,
        source: Path,
    ):
        super().__init__(prop_name, section, src_res_name, ref_res_name, source)

    @property
    def prop_name(self) -> str:
        return self.args[0]

    @property
    def section(self) -> str:
        return self.args[1]

    @property
    def src_res_name(self) -> str:
        return self.args[2]

    @property
    def ref_res_name(self) -> str:
        return self.args[3]

    @property
    def source(self) -> Path:
        return self.args[4]


class UnknownTagError(RestrictError):
    def __init__(self, tag: str, prefix: str, source: Path):
        super().__init__(tag, prefix, source)

    @property
    def tag(self) -> str:
        return self.args[0]

    @property
    def prefix(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]


class UnknownTypeError(RestrictError):
    def __init__(self, type: str, prefix: str, source: Path):
        super().__init__(type, prefix, source)

    @property
    def type(self) -> str:
        return self.args[0]

    @property
    def prefix(self) -> str:
        return self.args[1]

    @property
    def source(self) -> Path:
        return self.args[2]
