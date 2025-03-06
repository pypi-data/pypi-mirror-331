from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, override

from ..compiler.ast import (
    DataConstrainedField,
    DataComputedField,
    EffectsComputedField,
    Rel,
    SecurityConstraintField,
)
from ..compiler.types import (
    Datum,
    Effect,
    EffName,
    Field,
    LayeredMapping,
    Relation,
    Resource,
    ResourceCollection,
    Rule,
    RuleName,
)


class SpecField(Field):
    def __init__(self, res, compiled, is_computed):
        self.__res = res
        self.__compiled = compiled
        self.__is_computed = is_computed

    @property
    def res(self) -> Datum:
        return self.__res

    @res.setter
    def res(self, value):
        raise NotImplementedError()

    @property
    def compiled(self) -> Callable[[LayeredMapping], Any]:
        return self.__compiled

    @property
    def is_computed(self) -> bool:
        return self.__is_computed


class SpecEffect(Effect):
    def __init__(self, compiled, res):
        self.__compiled = compiled
        self.__res = res

    @property
    def compiled(self) -> Callable[[LayeredMapping], Any]:
        return self.__compiled

    @property
    def res(self) -> Resource | Datum | None:
        return self.__res

    @res.setter
    def res(self, value):
        raise NotImplementedError()


class SpecRule(Rule):
    def __init__(self, compiled):
        self.__compiled = compiled

    @property
    def compiled(self) -> Callable[[LayeredMapping], Any]:
        return self.__compiled


class SpecResource(Resource):
    specs: dict[str, SpecField]
    spec_effects: dict[str, dict[EffName, Callable[[LayeredMapping], Any] | None]]
    spec_rules: dict[str, dict[RuleName, Callable[[LayeredMapping], Any] | None]]

    fields: dict[str, DataConstrainedField | DataComputedField | Rel]
    field_effects: dict[str, dict[EffName, EffectsComputedField]]
    field_rules: dict[str, dict[RuleName, SecurityConstraintField]]

    @property
    def name(self) -> str:
        return type(self).__name__

    @override
    def compiled_name(self) -> str:
        return f"<compiled>/{type(self).__name__}"

    @override
    def get_effects(self) -> Mapping[EffName, Mapping[str, Effect]]:
        sections: list[EffName] = ["create", "modify", "delete"]
        effects: dict[EffName, dict[str, Effect]] = {
            "create": {},
            "modify": {},
            "delete": {},
        }
        if hasattr(self, "spec_effects"):
            for name, effs in self.spec_effects.items():
                for section in sections:
                    s = effs[section]
                    if s is not None:
                        effects[section][name] = SpecEffect(s, self.specs[name].res)
        if hasattr(self, "field_effects"):
            for name, effs in self.field_effects.items():
                for action, field in effs.items():
                    effects[action][name] = field
        return effects

    @override
    def get_fields(self) -> Mapping[str, Field]:
        specs = {}
        if hasattr(self, "specs"):
            specs = self.specs
        fields = {}
        if hasattr(self, "fields"):
            fields = self.fields
        return {x: y for x, y in specs.items() if isinstance(y.res, Datum)} | {
            x: y for x, y in fields.items() if not isinstance(y, Rel)
        }

    @override
    def get_relations(self) -> Mapping[str, Relation]:
        specs = {}
        if hasattr(self, "specs"):
            specs = self.specs
        fields = {}
        if hasattr(self, "fields"):
            fields = self.fields
        return {
            x: Relation(x, y.res)
            for x, y in specs.items()
            if isinstance(y.res, Resource)
        } | {x: y for x, y in fields.items() if isinstance(y, Rel)}

    @override
    def get_rules(self) -> Mapping[RuleName, Mapping[str, Rule]]:
        sections: list[RuleName] = ["create", "modify", "delete", "list", "details"]
        rules: dict[RuleName, dict[str, Rule]] = {
            "create": {},
            "modify": {},
            "delete": {},
            "list": {},
            "details": {},
        }
        if hasattr(self, "spec_rules"):
            for name, effs in self.spec_rules.items():
                for section in sections:
                    s = effs[section]
                    if s is not None:
                        rules[section][name] = SpecRule(s)
        if hasattr(self, "field_rules"):
            for name, effs in self.field_rules.items():
                for action, field in effs.items():
                    rules[action][name] = field

        return rules

    @override
    def get_singular_relations(self) -> Mapping[str, Relation]:
        return {
            name: field
            for name, field in self.get_relations().items()
            if not isinstance(field.res, ResourceCollection)
        }

    @override
    def resolve_path(self, path: list[str]) -> list[Datum | Resource] | None:
        pass

    @override
    def to_schema(self, action: RuleName = "create") -> dict[str, Any]:
        return {}

    @staticmethod
    def _field_effects(
        effects: dict[EffName, Callable[[LayeredMapping], Any] | None],
    ) -> dict[EffName, Callable[[LayeredMapping], Any] | None]:
        actions: list[EffName] = ["create", "modify", "delete"]
        for action in actions:
            if action not in effects:
                effects[action] = None
        return effects

    @staticmethod
    def _field_security(
        rules: dict[RuleName, Callable[[LayeredMapping], Any] | None] | list[RuleName],
    ) -> dict[RuleName, Callable[[LayeredMapping], Any] | None]:
        if isinstance(rules, list):
            rules = {x: lambda _: True for x in rules}
        actions: list[RuleName] = ["create", "modify", "delete", "list", "details"]
        for action in actions:
            if action not in rules:
                rules[action] = None
        return rules
