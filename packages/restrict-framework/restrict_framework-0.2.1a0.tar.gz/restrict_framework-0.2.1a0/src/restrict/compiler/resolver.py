from abc import ABC, abstractmethod
from importlib import import_module
from pathlib import Path

from .exceptions.compile import FileResolutionError, ModuleResolutionError
from .types import Module


class FileResolver(ABC):  # pragma: nocover
    @abstractmethod
    def resolve_file(self, path: Path) -> str:
        pass

    @abstractmethod
    def resolve_module(self, path: Path) -> Module:
        pass


class RestrictFileResolver(FileResolver):
    def resolve_file(self, path: Path) -> str:
        if not path.is_absolute():
            raise FileResolutionError(path, "not an absolute path")
        try:
            with path.open("r", encoding="utf8") as f:
                return f.read()
        except FileNotFoundError as fnfe:
            raise FileResolutionError(path, "does not exist", fnfe)
        except OSError as oe:
            raise FileResolutionError(path, "could not access", oe)

    def resolve_module(self, path: Path) -> Module:
        posix_path = path.as_posix()
        mod_path = posix_path[1:].replace("/", ".")
        e = None
        if not posix_path.startswith("/"):
            message = "not an absolute POSIX path"
            mod_path = ""
        else:
            try:
                mod = import_module(mod_path)
                if isinstance(mod.restrict_module, Module):
                    return mod.restrict_module
                message = "not a restrict.compiler.types.Module"
            except AttributeError as ae:
                e = ae
                message = "no restrict_module property"
            except ModuleNotFoundError as mnfe:
                e = mnfe
                message = "module cannot be loaded"
        raise ModuleResolutionError(path, mod_path, message, e)
