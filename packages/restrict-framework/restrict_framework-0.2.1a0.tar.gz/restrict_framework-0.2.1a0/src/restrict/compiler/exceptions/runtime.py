from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, override


class RestrictRuntimeError(RuntimeError, ABC):
    @property
    @abstractmethod
    def is_fatal(self) -> bool: ...

    def to_json(self):
        return {"type": type(self).__name__} | {
            key: getattr(self, key)
            if type(getattr(self, key)) is not list
            else [i.to_json() for i in getattr(self, key)]
            for key, value in type(self).__dict__.items()
            if isinstance(value, property)
        }


class RestrictRuntimeErrorGroup(RestrictRuntimeError):
    def __init__(self, errors: Sequence[RestrictRuntimeError]):
        super().__init__(errors)

    @property
    @override
    def is_fatal(self) -> bool:
        return any(e.is_fatal for e in self.errors)

    @property
    def errors(self) -> Sequence[RestrictRuntimeError]:
        return self.args[0]


class ComputedFieldAssignmentError(RestrictRuntimeError):
    def __init__(self, name: str, res: str):
        super().__init__(name, res)

    @property
    def is_fatal(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def res(self) -> str:
        return self.args[1]


class InvalidPropertyValueError(RestrictRuntimeError):
    def __init__(self, msg: str, name: str, value: Any, res: str):
        super().__init__(msg, name, value, res)

    @property
    def is_fatal(self) -> bool:
        return True

    @property
    def msg(self) -> str:
        return self.args[0]

    @property
    def name(self) -> str:
        return self.args[1]

    @property
    def value(self) -> Any:
        return self.args[2]

    @property
    def res(self) -> str:
        return self.args[3]


class PropertyValueFailsContraintError(RestrictRuntimeError):
    def __init__(self, name: str, value: Any, res: str):
        super().__init__(name, value, res)

    @property
    def is_fatal(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def value(self) -> Any:
        return self.args[1]

    @property
    def res(self) -> str:
        return self.args[2]


class SecurityPreventedFieldAssignmentError(RestrictRuntimeError):
    def __init__(self, name: str, value: Any, res: str):
        super().__init__(name, value, res)

    @property
    def is_fatal(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def value(self) -> Any:
        return self.args[1]

    @property
    def res(self) -> str:
        return self.args[2]


class UnboundPropertyError(RestrictRuntimeError):
    def __init__(self, name: str, res: str):
        super().__init__(name, res)

    @property
    def is_fatal(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self.args[0]

    @property
    def res(self) -> str:
        return self.args[1]
