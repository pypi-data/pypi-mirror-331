from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Literal, cast, overload, override

from .exceptions.runtime import (
    ComputedFieldAssignmentError,
    InvalidPropertyValueError,
    PropertyValueFailsContraintError,
    RestrictRuntimeError,
    RestrictRuntimeErrorGroup,
    SecurityPreventedFieldAssignmentError,
    UnboundPropertyError,
)
from .types import (
    Datum,
    EffName,
    LayeredMapping,
    OptionalDatum,
    RuleName,
)


class _Empty:
    pass


EMPTY_SENTINEL = _Empty()


class App:
    def __init__(
        self,
        root_context: LayeredMapping,
        resources: dict[str, type[AppResource]],
    ):
        self._root_context = root_context
        self._resources = resources

    @property
    def paths(self):
        return self._resources.keys()

    def get_resource(self, name: str):
        return self._resources[name]

    def get_repository(self, name: str):
        Res = self._resources[name]
        if Res._repository is None:
            instance = Res()
            specs = [getattr(instance, name) for name in Res._eval_order]
            for spec in specs:
                if isinstance(spec, RelSpec):
                    t = spec.field_func(self._root_context)
                    if issubclass(t, Repository):
                        Res._repository = t
                        break
        if Res._repository is None:
            Res._repository = TransientRepository
        return Res._repository


class Repository(ABC):
    def __init__(self, app_resource_type: type[AppResource]):
        self.app_resource_type = app_resource_type

    @abstractmethod
    async def create_object(
        self, scope, data: dict[str, Any]
    ) -> AppResource | None: ...

    @abstractmethod
    async def get_object(self, scope, id: Any) -> AppResource | None: ...

    @abstractmethod
    async def save_object(self, scope, id: Any | None, o) -> None: ...


class TransientRepository(Repository):
    @override
    async def create_object(self, scope, data: dict[str, Any]) -> AppResource | None:
        return self.app_resource_type._create(data)

    @override
    async def get_object(self, scope, id: Any) -> AppResource | None:
        return None

    @override
    async def save_object(self, scope, id: Any | None, o) -> None:
        pass


class AppResource(ABC):
    _eval_order: list[str]
    _repository: type[Repository] | None = None
    _is_singleton: bool = False
    __serilazing: bool = False

    def _get_underlying_spec(self, name: str) -> Spec:
        field_name = f"_spec_{name}"
        if hasattr(self, field_name):
            return getattr(self, field_name)
        raise KeyError(name)

    @classmethod
    def _create(cls, values: dict[str, Any]) -> AppResource:
        values = values.copy()
        errors = []
        skip_cx = []
        result = (
            cls()
            ._apply_incoming_security("create", values, errors)
            ._set_property_values("create", values, {}, errors, skip_cx)
            ._run_effects("create", values)
            ._run_constraints(errors, skip_cx)
        )
        if len(errors) > 0:
            raise RestrictRuntimeErrorGroup(errors)
        return result

    @classmethod
    def _modify(cls, old: dict[str, Any], new: dict[str, Any]) -> AppResource:
        errors = []
        skip_cx = []
        old = old.copy()
        new = new.copy()
        result = (
            cls()
            ._set_property_values("create", old, {}, errors, [])
            ._apply_incoming_security("modify", new, errors)
            ._set_property_values("modify", new, old, errors, skip_cx)
            ._run_effects("modify", new)
            ._run_constraints(errors, skip_cx)
        )
        if len(errors) > 0:
            raise RestrictRuntimeErrorGroup(errors)
        return result

    @classmethod
    def _hydrate(cls, data: dict[str, Any]) -> AppResource:
        errors = []
        skip_cx = []
        result = cls()._set_property_values(
            "hydrate",
            data.copy(),
            {},
            errors,
            skip_cx,
        )
        return result

    def _alter_field(self, field_name: str = "$", value: Any = EMPTY_SENTINEL):
        if value == EMPTY_SENTINEL or field_name == "$":
            new = {}
        else:
            new = {field_name: value}
        return self._alter(new)

    def _alter(self, new: dict[str, Any] | None):
        errors = []
        skip_cx = []
        if new is None:
            new = {}
        _ = (
            self._apply_incoming_security("modify", new, errors)
            ._set_property_values("modify", new, {}, errors, skip_cx)
            ._run_effects("modify", new)
            ._run_constraints(errors, skip_cx)
        )
        if len(errors) > 0:
            raise RestrictRuntimeErrorGroup(errors)
        return self

    def _apply_incoming_security(
        self,
        action: RuleName,
        values: dict[str, Any],
        errors: list[RestrictRuntimeError],
    ) -> AppResource:
        specs = [getattr(self, x) for x in self._eval_order]
        for spec in specs:
            if not spec.apply_rule(action) and spec.name in values:
                e = SecurityPreventedFieldAssignmentError(
                    spec.name, values[spec.name], type(self).__qualname__
                )
                errors.append(e)
                del values[spec.name]
        return self

    def _run_constraints(
        self,
        errors: list[RestrictRuntimeError],
        skip_cx: list[str],
    ) -> AppResource:
        specs = [getattr(self, x) for x in self._eval_order]
        for field in specs:
            if field.name in skip_cx:
                continue
            try:
                field.run_constraint()
                if field.is_required:
                    field.get()
            except RestrictRuntimeErrorGroup as rreg:
                errors.extend(rreg.errors)
            except RestrictRuntimeError as rre:
                errors.append(rre)
        return self

    def _run_effects(self, action: EffName, values: dict[str, Any]) -> AppResource:
        specs = [getattr(self, x) for x in self._eval_order]
        for spec in specs:
            if spec.name not in values:
                spec.run_effect(action)
            elif isinstance(spec, RelSpec):
                try:
                    ar = cast(AppResource, spec.get())
                    if ar is not None:
                        ar._run_effects(action, values[spec.name])
                except UnboundPropertyError:
                    pass
        return self

    def _set_property_values(
        self,
        action: EffName | Literal["hydrate"],
        new: dict[str, Any],
        old: dict[str, Any],
        errors: list[RestrictRuntimeError],
        skip_cx: list[str],
    ) -> AppResource:
        for key, value in new.items():
            try:
                spec = self._get_underlying_spec(key)
                spec.set(action, value, old.get(key, None))
            except RestrictRuntimeErrorGroup as rreg:
                errors.extend(rreg.errors)
                skip_cx.append(key)
            except RestrictRuntimeError as rre:
                errors.append(rre)
                skip_cx.append(key)
            except KeyError:
                skip_cx.append(key)
        return self

    def _to_schema(self, action: RuleName) -> dict[str, Any]:
        specs = [getattr(self, x) for x in self._eval_order]
        properties = {
            field.name: field.to_schema(action)
            for field in specs
            if isinstance(field, Spec) and field.apply_rule(action)
        }

        defs = {}
        def_names = {}
        for name, prop in properties.items():
            if "$defs" in prop:
                d = defs.setdefault("$defs", {})
                self.__merge_dicts(prop["$defs"], d)
            if "$schema" in prop:
                id = prop["$id"]
                def_names[name] = id
                d = defs.setdefault("$defs", {})
                for part in id[1:].split("/"):
                    d = d.setdefault(part, {})
                for key, value in prop.items():
                    if key in ["properties", "required", "type"]:
                        d[key] = value
        for name, id in def_names.items():
            new_prop = {"$ref": f"#/$defs{id}"}
            for key, value in properties[name].items():
                if not key.startswith("$") and key not in [
                    "properties",
                    "required",
                    "type",
                ]:
                    new_prop[key] = value
            properties[name] = new_prop

        required = [
            field.name
            for field in specs
            if isinstance(field, Spec)
            and field.is_required
            and field.apply_rule(action)
        ]
        result = defs | {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": type(self).__qualname__,
            "type": "object",
            "properties": properties,
            "required": required,
        }

        return result

    def _to_json(self, action: RuleName | Literal["all"]) -> dict[str, Any]:
        if self.__serilazing:
            return {"$ref": "self"}

        self.__serilazing = True
        specs = [getattr(self, x) for x in self._eval_order]
        result = {
            v.name: v.to_json(action)
            for v in specs
            if isinstance(v, Spec)
            and (v.is_required or v.to_json(action) is not None)
            and (action == "all" or v.apply_rule(action))
        }
        self.__serilazing = False
        return result

    def __merge_dicts(self, source, target):
        for key, value in source.items():
            if key not in target or not isinstance(source[key], dict):
                target[key] = value
            else:
                raise NotImplementedError()  # pragma: nocover (should not happen)


class Spec(ABC):
    def __init__(
        self,
        context: LayeredMapping,
        resource_name: str,
        name: str,
        field_func: Callable[[LayeredMapping], Any],
        effects: dict[EffName, Callable[[LayeredMapping], Any] | None],
        security: dict[RuleName, Callable[[LayeredMapping], Any] | None],
        meta: Mapping[str, str] = {},
    ):
        self.context = context
        self.resource_name = resource_name
        self.name = name
        self.type = type
        self.field_func = field_func
        self.effects = effects
        self.security = security
        self.meta = meta

    @property
    @abstractmethod
    def is_required(self) -> bool: ...

    @abstractmethod
    def to_schema(self, action: RuleName) -> dict[str, Any]: ...

    @abstractmethod
    def get(self) -> Any | None: ...

    @abstractmethod
    def set(self, action: EffName | Literal["hydrate"], new, old) -> Any: ...

    @abstractmethod
    def to_json(
        self,
        action: RuleName | Literal["all"],
    ) -> (
        bool | int | Decimal | datetime | timedelta | str | list | set | dict | None
    ): ...

    @abstractmethod
    def run_constraint(self): ...

    @abstractmethod
    def run_effect(self, action: EffName): ...

    def apply_rule(self, action: RuleName):
        rule = self.security.get(action)
        if rule is not None:
            return rule(self.context)
        return False


class CompSpec(Spec):
    def __init__(
        self,
        context: LayeredMapping,
        resource_name: str,
        name: str,
        type: Datum | AppResource,
        field_func: Callable[[LayeredMapping], Any],
        effects: dict[EffName, Callable[[LayeredMapping], Any] | None],
        security: dict[RuleName, Callable[[LayeredMapping], Any] | None],
        meta: Mapping[str, str] = {},
    ):
        super().__init__(
            context, resource_name, name, field_func, effects, security, meta
        )
        self.type = type

    @override
    def get(self):
        return self.field_func(self.context)

    @override
    def to_schema(self, action: RuleName):
        t = self.type
        if isinstance(t, AppResource):
            return t._to_schema(action) | {"readOnly": True}
        else:
            return t.to_schema() | {"readOnly": True}

    @override
    def to_json(
        self,
        action: RuleName | Literal["all"],
    ) -> bool | int | Decimal | datetime | timedelta | str | list | set | dict | None:
        value = self.get()
        if isinstance(value, AppResource):
            return value._to_json(action)
        elif isinstance(self.type, Datum):
            return self.type.to_json(value)
        raise ValueError()

    @property
    @override
    def is_required(self) -> bool:
        return not isinstance(self.type, OptionalDatum)

    def run_constraint(self):
        pass

    @override
    def set(self, action, new, old) -> Any:
        raise ComputedFieldAssignmentError(self.name, self.resource_name)

    @override
    def run_effect(self, action: EffName):
        pass


class FieldSpec(Spec):
    def __init__(
        self,
        context: LayeredMapping,
        resource_name: str,
        name: str,
        type: Datum,
        field_func: Callable[[LayeredMapping], Any],
        effects: dict[EffName, Callable[[LayeredMapping], Any] | None],
        security: dict[RuleName, Callable[[LayeredMapping], Any] | None],
        meta: Mapping[str, str] = {},
    ):
        super().__init__(
            context, resource_name, name, field_func, effects, security, meta
        )
        self.type = type
        self.value: (
            bool | int | Decimal | datetime | timedelta | str | list | set | _Empty
        ) = EMPTY_SENTINEL

    @property
    @override
    def is_required(self) -> bool:
        return not isinstance(self.type, OptionalDatum)

    @property
    def bound(self) -> bool:
        return self.value != EMPTY_SENTINEL

    @override
    def to_schema(self, action: RuleName):
        return self.type.to_schema() | {"readOnly": False}

    @override
    def to_json(
        self,
        action: RuleName | Literal["all"],
    ) -> bool | int | Decimal | datetime | timedelta | str | list | set | None:
        return self.type.to_json(self.get())

    @override
    def get(
        self,
    ) -> bool | int | Decimal | datetime | timedelta | str | list | set | None:
        if self.value == EMPTY_SENTINEL and not self.is_required:
            return None
        elif not isinstance(self.value, _Empty):
            return self.value
        raise UnboundPropertyError(self.name, self.resource_name)

    def run_constraint(self):
        try:
            value = self.get()
            self.context["value"] = value
            if self.field_func(self.context) is False:
                raise PropertyValueFailsContraintError(
                    self.name,
                    value,
                    self.resource_name,
                )
        except UnboundPropertyError:
            pass

    def set(self, action, new, old):
        try:
            self.value = self.type.parse(new)
        except ValueError as e:
            raise InvalidPropertyValueError(
                e.args[0],
                self.name,
                new,
                self.resource_name,
            )
        return self

    @override
    def run_effect(self, action: EffName):
        effect = self.effects[action]
        if effect is not None:
            self.value = effect(self.context)


class RelSpec(Spec):
    def __init__(
        self,
        context: LayeredMapping,
        resource_name: str,
        name: str,
        is_optional: bool,
        compiled_res_name: str,
        effects: dict[EffName, Callable[[LayeredMapping], Any] | None],
        security: dict[RuleName, Callable[[LayeredMapping], Any] | None],
        meta: Mapping[str, str] = {},
    ):
        super().__init__(
            context,
            resource_name,
            name,
            lambda _: context[compiled_res_name],
            effects,
            security,
            meta,
        )
        self.is_optional = is_optional
        self.value: AppResource | object = EMPTY_SENTINEL

    @overload
    def res(self, action: Literal["_create"]) -> Callable[[dict], AppResource]: ...

    @overload
    def res(
        self, action: Literal["_modify"]
    ) -> Callable[[dict, dict], AppResource]: ...

    @overload
    def res(self, action: Literal["_hydrate"]) -> Callable[[dict], AppResource]: ...

    def res(self, action):
        return getattr(self.field_func(self.context), action)

    @property
    def bound(self) -> bool:
        return self.value != EMPTY_SENTINEL

    @override
    def to_schema(self, action: RuleName) -> dict[str, Any]:
        return self.field_func(self.context)()._to_schema(action)

    @override
    def get(self) -> AppResource | None:
        if isinstance(self.value, AppResource):
            return self.value
        elif self.value == EMPTY_SENTINEL and not self.is_required:
            return None
        raise UnboundPropertyError(self.name, self.resource_name)

    @override
    def to_json(self, action: RuleName | Literal["all"]) -> dict[str, Any] | None:
        value = self.get()
        if value is not None:
            return value._to_json(action)
        return None

    def set(self, action, new, old):
        if action == "create":
            self.value = self.res("_create")(new)
        elif action == "modify":
            self.value = self.res("_modify")(old or {}, new)
        elif action == "hydrate":
            self.value = self.res("_hydrate")(new)

    @property
    @override
    def is_required(self) -> bool:
        return not self.is_optional

    def run_constraint(self):
        value = self.get()
        if isinstance(value, AppResource):
            errors = []
            skip_cx = []
            value._run_constraints(errors, skip_cx)  # type: ignore
            if len(errors) > 0:
                raise RestrictRuntimeErrorGroup(
                    errors
                )  # pragma: nocover (should not happen)

    @override
    def run_effect(self, action: EffName):
        effect = self.effects[action]
        if effect is not None:
            result = effect(self.context)
            self.value = result
