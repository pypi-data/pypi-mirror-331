from __future__ import annotations

import functools
import inspect
import re
from abc import ABC, abstractmethod
from collections.abc import Generator, Mapping, MutableMapping, Sequence
from decimal import Decimal
from itertools import permutations
from pathlib import Path
from typing import Literal

from .ast import (
    CollectionType,
    Create,
    DataComputedExpr,
    DataComputedField,
    DataConstrainedField,
    DataConstraintExpr,
    DataField,
    DataFields,
    Dir,
    Effects,
    EffectsComputedExpr,
    EffectsComputedField,
    EffEntries,
    EffName,
    File,
    Func,
    FuncParam,
    Import,
    Lit,
    Modify,
    PipedExprList,
    Ref,
    Rel,
    Rels,
    Res,
    RuleName,
    Rules,
    SecurityConstraintExpr,
    SecurityConstraintField,
    Self,
    Selves,
    TaggedLit,
    Transition,
    TransitionComputedExpr,
    TransitionComputedField,
    TransitionEntries,
    Transitions,
    TxDec,
    Value,
)
from .exceptions.compile import (
    DuplicatePropertyError,
    LexToken,
    ParsingError,
    RestrictError,
)
from .lexers import RestrictLexer
from .ply.yacc import LRParser, YaccProduction, yacc

type ResourceSections = tuple[DataFields, Rels, Effects, Rules, Transitions]


class RestrictParser(ABC):
    @abstractmethod
    def parse(self, content: str, source: Path) -> File | None: ...

    @property
    @abstractmethod
    def errors(self) -> Sequence[RestrictError]: ...


class ShiftedYaccProduction:
    def __init__(self, p: YaccProduction):
        self._p = p

    def __getitem__(self, n):
        if isinstance(n, int):
            return self._p[n + 1]
        return self._p[n]

    def __len__(self):
        return len(self._p) - 1


def RULE(
    first_line_or_gen: str | Generator[str, None, None] | list[str] | None,
    *args: str,
):
    if first_line_or_gen is None:
        raise SyntaxError("Cannot create a RULE with no specification")

    def set_doc(func):
        @functools.wraps(func)
        def wrapper(self, p: YaccProduction):
            p[0] = func(self, ShiftedYaccProduction(p))

        lines: list[str] = []
        if isinstance(first_line_or_gen, list):
            lines = first_line_or_gen
        elif inspect.isgenerator(first_line_or_gen):
            lines = list(first_line_or_gen) + list(args)
        elif isinstance(first_line_or_gen, str):
            lines = [first_line_or_gen] + list(args)
        rule_name = func.__name__[2:]
        wrapper.__doc__ = (
            rule_name + " : " + ("\n" + " " * len(rule_name) + " | ").join(lines)
        )
        return wrapper

    return set_doc


MAIN_SECTIONS = ["data", "dnc", "effects", "security", "workflow"]
MAIN_SECTION_PERMUTATIONS = [
    list(permutations(MAIN_SECTIONS, n)) for n in range(1, len(MAIN_SECTIONS) + 1)
]

EFFECTS_SECTIONS = ["eff_create", "eff_modify", "eff_delete"]
EFFECTS_SECTION_PERMUTATIONS = [
    list(permutations(EFFECTS_SECTIONS, n)) for n in range(1, len(EFFECTS_SECTIONS) + 1)
]


SECURITY_SECTIONS = [
    "sec_create",
    "sec_modify",
    "sec_delete",
    "sec_list",
    "sec_details",
]
SECURITY_SECTION_PERMUTATIONS = [
    list(permutations(SECURITY_SECTIONS, n))
    for n in range(1, len(SECURITY_SECTIONS) + 1)
]


class DataSectionMixin:
    _errors: list[RestrictError]
    _source: Path

    @RULE("DATA '{' data_fields '}'")
    def p_data(
        self,
        p: tuple[str, str, DataFields, DataFields, str],
    ) -> tuple[Literal["data"], DataFields]:
        return "data", p[2]

    @RULE(
        "data_fields data_field",
        "data_field",
    )
    def p_data_fields(
        self,
        p: tuple[DataFields, DataFields] | tuple[DataFields],
    ) -> Mapping[str, DataField]:
        if len(p) == 2:
            for name in p[1]:
                if name in p[0]:
                    e = DuplicatePropertyError(name, self._source)
                    self._errors.append(e)
        return p[0] if len(p) == 1 else p[0] | p[1]

    @RULE(
        "ID ':' field_mods ID '.' ID ';'",
        "ID ':' field_mods ID '.' ID ':' data_expr ';'",
        "ID ':' field_mods ID ';'",
        "ID ':' field_mods ID ':' data_expr ';'",
        "data_computed_field",
    )
    def p_data_field(
        self,
        p: (
            tuple[
                str,
                Literal[":"],
                tuple[bool, bool, CollectionType],
                str,
                Literal["."],
                str,
                Literal[";"],
            ]
            | tuple[
                str,
                Literal[":"],
                tuple[bool, bool, CollectionType],
                str,
                Literal["."],
                str,
                Literal[":"],
                list[DataConstraintExpr | None],
                Literal[";"],
            ]
            | tuple[
                str,
                Literal[":"],
                tuple[bool, bool, CollectionType],
                str,
                Literal[";"],
            ]
            | tuple[
                str,
                Literal[":"],
                tuple[bool, bool, CollectionType],
                str,
                Literal[":"],
                list[DataConstraintExpr | None],
                Literal[";"],
            ]
            | tuple[dict[str, DataComputedField]]
        ),
    ) -> Mapping[str, DataField]:
        if len(p) == 1:
            return p[0]

        name = p[0]
        is_optional, is_unique, collection_type = p[2]
        if p[1] == ":" and len(p) == 5:
            field = DataConstrainedField(
                p[3],
                "",
                is_optional,
                is_unique,
                collection_type,
                PipedExprList([Lit(True)]),
            )
        elif p[4] == ":" and len(p) == 7:
            field = DataConstrainedField(
                p[3],
                "",
                is_optional,
                is_unique,
                collection_type,
                PipedExprList([x for x in p[5] if x is not None]),
            )
        elif p[4] == "." and len(p) == 7:
            field = DataConstrainedField(
                p[5],
                p[3],
                is_optional,
                is_unique,
                collection_type,
                PipedExprList([Lit(True)]),
            )
        else:
            field = DataConstrainedField(
                p[5],
                p[3],
                is_optional,
                is_unique,
                collection_type,
                PipedExprList([x for x in p[7] if x is not None]),
            )
        return {name: field}

    @RULE("ID '=' data_comp_expr ';'")
    def p_data_computed_field(
        self,
        p: tuple[str, Literal["="], list[DataComputedExpr | None], str],
    ) -> dict[str, DataComputedField]:
        return {
            p[0]: DataComputedField(PipedExprList([x for x in p[2] if x is not None]))
        }

    @RULE(
        "data_comp_expr PIPEOP data_comp_term",
        "data_comp_term",
    )
    def p_data_comp_expr(
        self,
        p: (
            tuple[DataComputedExpr]
            | tuple[PipedExprList[DataComputedExpr], str, DataComputedExpr]
        ),
    ) -> PipedExprList:
        return (
            PipedExprList([p[0]])
            if len(p) == 1
            else PipedExprList([x for x in p[0] if x is not None] + [p[2]])
        )

    @RULE(
        # Lit
        "DECIMAL",
        "FALSE",
        "INT",
        "STRING",
        "TRUE",
        # Self
        "SELF opt_props",
        # Selves
        "SELVES",
        # Ref, Func
        "data_comp_func",
    )
    def p_data_comp_term(
        self,
        p: (
            tuple[Literal["self"], list[str]]
            | tuple[str, str]
            | tuple[int | str | Decimal | bool | Func | Ref | Self | TaggedLit]
        ),
    ) -> DataComputedExpr | None:
        if (
            isinstance(p[0], Func)
            or isinstance(p[0], Self)
            or isinstance(p[0], Ref)
            or isinstance(p[0], TaggedLit)
        ):
            return p[0]

        if p[0] == "selves":
            return Selves()
        elif len(p) == 2 and isinstance(p[1], list):
            return Self(p[1])

        return Lit(p[0])

    @RULE(
        "prop",
        "prop '(' ')'",
        "prop '(' data_comp_args ')'",
        "prop '[' params ']' '(' data_comp_args ')'",
    )
    def p_data_comp_func(
        self,
        p: (
            tuple[list[str] | TaggedLit]
            | tuple[list[str], str, str]
            | tuple[list[str], str, list[PipedExprList], str]
            | tuple[
                list[str],
                str,
                list[FuncParam],
                str,
                str,
                list[PipedExprList],
                str,
            ]
        ),
    ) -> Ref | Func | TaggedLit:
        if isinstance(p[0], TaggedLit):
            return p[0]
        if isinstance(p[0], list) and len(p) == 1:
            return Ref(p[0])

        params = []
        args = []
        name = p[0][-1]
        prefix = p[0][: len(p[0]) - 1]
        if len(p) > 3:
            params = p[2] if len(p) == 7 else []
            args = p[2] if len(p) == 4 else p[5]
        return Func(name, prefix, params, args)

    @RULE(
        "data_comp_args ',' data_comp_expr",
        "data_comp_expr",
    )
    def p_data_comp_args(
        self,
        p: (tuple[PipedExprList] | tuple[list[PipedExprList], str, PipedExprList]),
    ) -> list[PipedExprList]:
        return [p[0]] if len(p) == 1 else p[0] + [p[2]]

    @RULE(
        "data_expr PIPEOP data_term",
        "data_term",
    )
    def p_data_expr(
        self,
        p: (
            tuple[DataConstraintExpr]
            | tuple[PipedExprList[DataConstraintExpr], str, DataConstraintExpr]
        ),
    ) -> PipedExprList:
        return (
            PipedExprList([p[0]])
            if len(p) == 1
            else PipedExprList([x for x in p[0] if x is not None] + [p[2]])
        )

    @RULE(
        # Lit
        "DECIMAL",
        "FALSE",
        "INT",
        "STRING",
        "TRUE",
        # Self
        "SELF opt_props",
        # Selves
        "SELVES",
        # Value
        "VALUE",
        # Ref, Func
        "data_func",
    )
    def p_data_term(
        self,
        p: (
            tuple[Literal["self"], list[str]]
            | tuple[str, str]
            | tuple[int | str | Decimal | bool | Func | Self | TaggedLit]
        ),
    ) -> DataConstraintExpr | None:
        if (
            isinstance(p[0], Func)
            or isinstance(p[0], Self)
            or isinstance(p[0], TaggedLit)
        ):
            return p[0]

        if p[0] == "selves":
            return Selves()
        elif p[0] == "value":
            return Value()
        elif len(p) == 2 and isinstance(p[1], list):
            return Self(p[1])

        return Lit(p[0])

    @RULE(
        "prop",
        "prop '(' ')'",
        "prop '(' data_args ')'",
        "prop '[' params ']' '(' data_args ')'",
    )
    def p_data_func(
        self,
        p: (
            tuple[list[str]]
            | tuple[list[str], str, str]
            | tuple[list[str], str, list[PipedExprList], str]
            | tuple[
                list[str],
                str,
                list[FuncParam],
                str,
                str,
                list[PipedExprList],
                str,
            ]
        ),
    ) -> Self | Func:
        if len(p) == 1:
            return Self(p[0])

        params = []
        args = []
        name = p[0][-1]
        prefix = p[0][: len(p[0]) - 1]
        if len(p) > 3:
            params = p[2] if len(p) == 7 else []
            args = p[2] if len(p) == 4 else p[5]
        return Func(name, prefix, params, args)

    @RULE(
        "data_args ',' data_expr",
        "data_expr",
    )
    def p_data_args(
        self,
        p: (tuple[PipedExprList] | tuple[list[PipedExprList], str, PipedExprList]),
    ) -> list[PipedExprList]:
        return [p[0]] if len(p) == 1 else p[0] + [p[2]]


class DncSectionMixin:
    _errors: list[RestrictError]
    _source: Path

    @RULE("DNC '{' dnc_rels '}'")
    def p_dnc(
        self,
        p: tuple[str, str, Rels, Rels, str],
    ) -> tuple[Literal["dnc"], Rels]:
        return "dnc", p[2]

    @RULE(
        "dnc_rels dnc_rel",
        "dnc_rel",
    )
    def p_dnc_rels(self, p: tuple[Rels, Rels] | tuple[Rels]) -> Rels:
        if len(p) == 2:
            for name in p[1]:
                if name in p[0]:
                    e = DuplicatePropertyError(name, self._source)
                    self._errors.append(e)
        return p[0] if len(p) == 1 else dict(p[0]) | dict(p[1])

    @RULE("opt_dnc_dec ID opt_dnc_card ':' field_mods name ';'")
    def p_dnc_rel(
        self,
        p: tuple[
            Dir,
            str,
            tuple[int, int | Literal["*"]] | None,
            str,
            tuple[bool, bool, CollectionType],
            tuple[str, str],
            str,
        ],
    ) -> Rels:
        is_optional, is_unique, collection_type = p[4]
        cardinality = (0, "*") if collection_type is not None and p[2] is None else p[2]
        name, prefix = p[5]
        return {
            p[1]: Rel(
                name,
                prefix,
                is_optional,
                is_unique,
                collection_type,
                cardinality,
                p[0],
            )
        }

    @RULE(
        "'<' REL '>'",
        "empty",
    )
    def p_opt_dnc_dec(self, p: tuple[None] | tuple[str, Dir, str]) -> Dir:
        return "" if len(p) == 1 else p[1]

    @RULE(
        "'[' INT ',' INT ']'",
        "'[' INT ',' '*' ']'",
        "empty",
    )
    def p_opt_dnc_card(
        self,
        p: (
            tuple[None]
            | tuple[str, int, str, int, str]
            | tuple[str, int, str, Literal["*"], str]
        ),
    ) -> tuple[int, int | Literal["*"]] | None:
        if len(p) == 5:
            return p[1], p[3]


class EffectsSectionMixin:
    _errors: list[RestrictError]
    _source: Path

    @RULE("EFFECTS '{' eff_body '}'")
    def p_effects(
        self,
        p: tuple[Literal["effects"], str, Effects, str],
    ) -> tuple[Literal["effects"], Effects]:
        return p[0], p[2]

    @RULE(" ".join(y) for x in EFFECTS_SECTION_PERMUTATIONS for y in x)
    def p_eff_body(self, p: list[tuple[EffName, EffEntries]]) -> Effects:
        result: MutableMapping[EffName, EffEntries] = {
            "create": {},
            "modify": {},
            "delete": {},
        }
        for key, entries in p:
            result[key] = entries
        return result

    @RULE("CREATE '{' eff_action_body '}'")
    def p_eff_create(
        self,
        p: tuple[Literal["create"], str, dict[str, EffectsComputedField], str],
    ) -> tuple[Literal["create"], dict[str, EffectsComputedField]]:
        return p[0], p[2]

    @RULE("MODIFY '{' eff_action_body '}'")
    def p_eff_modify(
        self,
        p: tuple[Literal["modify"], str, dict[str, EffectsComputedField], str],
    ) -> tuple[Literal["modify"], dict[str, EffectsComputedField]]:
        return p[0], p[2]

    @RULE("DELETE '{' eff_action_body '}'")
    def p_eff_delete(
        self,
        p: tuple[Literal["delete"], str, dict[str, EffectsComputedField], str],
    ) -> tuple[Literal["delete"], dict[str, EffectsComputedField]]:
        return p[0], p[2]

    @RULE(
        "eff_action_body eff_field",
        "eff_field",
    )
    def p_eff_action_body(
        self,
        p: (
            tuple[dict[str, EffectsComputedField]]
            | tuple[dict[str, EffectsComputedField], dict[str, EffectsComputedField]]
        ),
    ) -> EffEntries:
        return p[0] if len(p) == 1 else p[0] | p[1]

    @RULE("ID '=' eff_expr ';'")
    def p_eff_field(
        self,
        p: tuple[str, Literal["="], list[EffectsComputedExpr | None], str],
    ) -> dict[str, EffectsComputedField]:
        return {
            p[0]: EffectsComputedField(
                PipedExprList([x for x in p[2] if x is not None])
            )
        }

    @RULE(
        "eff_expr PIPEOP eff_term",
        "eff_term",
    )
    def p_eff_expr(
        self,
        p: (
            tuple[EffectsComputedExpr]
            | tuple[PipedExprList[EffectsComputedExpr], str, EffectsComputedExpr]
        ),
    ) -> PipedExprList[EffectsComputedExpr]:
        return (
            PipedExprList([p[0]])
            if len(p) == 1
            else PipedExprList([x for x in p[0] if x is not None] + [p[2]])
        )

    @RULE(
        # Lit
        "FALSE",
        "DECIMAL",
        "INT",
        "STRING",
        "TRUE",
        # Self
        "SELF opt_props",
        # Selves
        "SELVES",
        # Ref, Func
        "eff_func",
        # Create, Modify
        "CREATE name",
        "MODIFY ID",
        "CREATE name '{' eff_action_body '}'",
        "MODIFY ID '{' eff_action_body '}'",
    )
    def p_eff_term(
        self,
        p: (
            tuple[int | str | Decimal | bool | Func | Ref | TaggedLit]
            | tuple[str, str]
            | tuple[Literal["self"], list[str]]
            | tuple[Literal["create"], str]
            | tuple[Literal["modify"], str]
            | tuple[
                Literal["create"],
                tuple[str, str],
                str,
                dict[str, EffectsComputedField],
                str,
            ]
            | tuple[
                Literal["modify"],
                str,
                str,
                dict[str, EffectsComputedField],
                str,
            ]
        ),
    ) -> EffectsComputedExpr | None:
        if len(p) == 5 and p[0] == "create":
            name, prefix = p[1]
            return Create(name, prefix, p[3])
        if len(p) == 5:
            return Modify(Self([p[1]]), p[3])
        if (
            isinstance(p[0], Func)
            or isinstance(p[0], Ref)
            or isinstance(p[0], TaggedLit)
        ):
            if p[0] == Ref(["delete"]):
                return None
            return p[0]

        if p[0] == "selves":
            return Selves()
        elif len(p) == 2 and p[0] == "create":
            name, prefix = p[1]
            return Create(name, prefix, {})
        elif len(p) == 2 and p[0] == "modify" and isinstance(p[1], str):
            return Modify(Self([p[1]]), {})
        elif len(p) == 2 and isinstance(p[1], list):
            return Self(p[1])

        return Lit(p[0])

    @RULE(
        "prop",
        "prop '(' ')'",
        "prop '(' eff_args ')'",
        "prop '[' params ']' '(' eff_args ')'",
    )
    def p_eff_func(
        self,
        p: (
            tuple[list[str] | TaggedLit]
            | tuple[list[str], str, str]
            | tuple[list[str], str, list[PipedExprList[EffectsComputedExpr]], str]
            | tuple[
                list[str],
                str,
                list[FuncParam],
                str,
                str,
                list[PipedExprList[EffectsComputedExpr]],
                str,
            ]
        ),
    ) -> Ref | Func[EffectsComputedExpr] | TaggedLit:
        if isinstance(p[0], TaggedLit):
            return p[0]
        if len(p) == 1:
            return Ref(p[0])

        params = []
        args = []
        name = p[0][-1]
        prefix = p[0][: len(p[0]) - 1]
        if len(p) > 3:
            params = p[2] if len(p) == 7 else []
            args = p[2] if len(p) == 4 else p[5]
        return Func(name, prefix, params, args)

    @RULE(
        "eff_args ',' eff_expr",
        "eff_expr",
    )
    def p_eff_args(
        self,
        p: (
            tuple[PipedExprList[EffectsComputedExpr]]
            | tuple[
                list[PipedExprList[EffectsComputedExpr]],
                str,
                PipedExprList[EffectsComputedExpr],
            ]
        ),
    ) -> list[PipedExprList[EffectsComputedExpr]]:
        return [p[0]] if len(p) == 1 else p[0] + [p[2]]


class SecuritySectionMixin:
    _errors: list[RestrictError]
    _source: Path

    @RULE("SECURITY '{' sec_body '}'")
    def p_security(
        self,
        p: tuple[Literal["security"], str, Rules, str],
    ) -> tuple[Literal["security"], Rules]:
        return p[0], p[2]

    @RULE(" ".join(y) for x in SECURITY_SECTION_PERMUTATIONS for y in x)
    def p_sec_body(
        self,
        p: list[
            tuple[
                RuleName,
                SecurityConstraintField | dict[str, SecurityConstraintField],
            ]
        ],
    ) -> Rules:
        result: Rules = {}
        for name, section in p:
            result[name] = section
        return result

    @RULE(
        "LIST ':' sec_expr ';'",
        "LIST '{' sec_attrs '}'",
    )
    def p_sec_list(
        self,
        p: tuple[
            Literal["list"],
            str,
            PipedExprList | dict[str, SecurityConstraintField],
            str,
        ],
    ) -> tuple[
        Literal["list"],
        SecurityConstraintField | dict[str, SecurityConstraintField],
    ]:
        return p[0], (p[2] if isinstance(p[2], dict) else SecurityConstraintField(p[2]))

    @RULE(
        "DETAILS ':' sec_expr ';'",
        "DETAILS '{' sec_attrs '}'",
    )
    def p_sec_details(
        self,
        p: tuple[
            Literal["details"],
            str,
            PipedExprList | dict[str, SecurityConstraintField],
            str,
        ],
    ) -> tuple[
        Literal["details"],
        SecurityConstraintField | dict[str, SecurityConstraintField],
    ]:
        return p[0], (p[2] if isinstance(p[2], dict) else SecurityConstraintField(p[2]))

    @RULE(
        "CREATE ':' sec_expr ';'",
        "CREATE '{' sec_attrs '}'",
    )
    def p_sec_create(
        self,
        p: tuple[
            Literal["create"],
            str,
            PipedExprList | dict[str, SecurityConstraintField],
            str,
        ],
    ) -> tuple[
        Literal["create"],
        SecurityConstraintField | dict[str, SecurityConstraintField],
    ]:
        return p[0], (p[2] if isinstance(p[2], dict) else SecurityConstraintField(p[2]))

    @RULE(
        "MODIFY ':' sec_expr ';'",
        "MODIFY '{' sec_attrs '}'",
    )
    def p_sec_modify(
        self,
        p: tuple[
            Literal["modify"],
            str,
            PipedExprList | dict[str, SecurityConstraintField],
            str,
        ],
    ) -> tuple[
        Literal["modify"],
        SecurityConstraintField | dict[str, SecurityConstraintField],
    ]:
        return p[0], (p[2] if isinstance(p[2], dict) else SecurityConstraintField(p[2]))

    @RULE(
        "DELETE ':' sec_expr ';'",
        "DELETE '{' sec_attrs '}'",
    )
    def p_sec_delete(
        self,
        p: tuple[
            Literal["delete"],
            str,
            PipedExprList | dict[str, SecurityConstraintField],
            str,
        ],
    ) -> tuple[
        Literal["delete"],
        SecurityConstraintField | dict[str, SecurityConstraintField],
    ]:
        return p[0], (p[2] if isinstance(p[2], dict) else SecurityConstraintField(p[2]))

    @RULE(
        "sec_attrs ID ':' sec_expr ';'",
        "ID ':' sec_expr ';'",
    )
    def p_sec_attrs(
        self,
        p: (
            tuple[str, str, PipedExprList, str]
            | tuple[dict[str, SecurityConstraintField], str, str, PipedExprList, str]
        ),
    ) -> dict[str, SecurityConstraintField]:
        if len(p) == 4:
            return {p[0]: SecurityConstraintField(p[2])}
        return p[0] | {p[1]: SecurityConstraintField(p[3])}

    @RULE(
        "sec_expr PIPEOP sec_term",
        "sec_term",
    )
    def p_sec_expr(
        self,
        p: (
            tuple[SecurityConstraintExpr]
            | tuple[PipedExprList, str, SecurityConstraintExpr]
        ),
    ) -> PipedExprList:
        return (
            PipedExprList([p[0]])
            if len(p) == 1
            else PipedExprList([x for x in p[0] if x is not None] + [p[2]])
        )

    @RULE(
        # Lit
        "FALSE",
        "DECIMAL",
        "INT",
        "STRING",
        "TRUE",
        # Self
        "SELF opt_props",
        # Ref, Func
        "sec_func",
    )
    def p_sec_term(
        self,
        p: (
            tuple[Literal["self"], list[str]]
            | tuple[str, str]
            | tuple[int | str | Decimal | bool | Func | Ref | TaggedLit]
        ),
    ) -> SecurityConstraintExpr | None:
        if (
            isinstance(p[0], Func)
            or isinstance(p[0], Ref)
            or isinstance(p[0], TaggedLit)
        ):
            return p[0]
        elif len(p) == 2 and isinstance(p[1], list):
            return Self(p[1])

        return Lit(p[0])

    @RULE(
        "prop",
        "prop '(' ')'",
        "prop '(' sec_args ')'",
        "prop '[' params ']' '(' sec_args ')'",
    )
    def p_sec_func(
        self,
        p: (
            tuple[list[str] | TaggedLit]
            | tuple[list[str], str, str]
            | tuple[list[str], str, list[PipedExprList[SecurityConstraintExpr]], str]
            | tuple[
                list[str],
                str,
                list[FuncParam],
                str,
                str,
                list[PipedExprList[SecurityConstraintExpr]],
                str,
            ]
        ),
    ) -> Ref | Func | TaggedLit:
        if isinstance(p[0], TaggedLit):
            return p[0]
        if len(p) == 1:
            return Ref(p[0])

        params = []
        args = []
        name = p[0][-1]
        prefix = p[0][: len(p[0]) - 1]
        if len(p) > 3:
            params = p[2] if len(p) == 7 else []
            args = p[2] if len(p) == 4 else p[5]
        return Func(name, prefix, params, args)

    @RULE(
        "sec_args ',' sec_expr",
        "sec_expr",
    )
    def p_sec_args(
        self,
        p: (
            tuple[PipedExprList[SecurityConstraintExpr]]
            | tuple[
                list[PipedExprList[SecurityConstraintExpr]],
                str,
                PipedExprList[SecurityConstraintExpr],
            ]
        ),
    ) -> list[PipedExprList[SecurityConstraintExpr]]:
        return [p[0]] if len(p) == 1 else p[0] + [p[2]]


class WorkflowSectionMixin:
    _errors: list[RestrictError]
    _source: Path

    @RULE("WORKFLOW '{' wf_transitions '}'")
    def p_workflow(
        self,
        p: tuple[Literal["workflow"], str, Transitions, str],
    ) -> tuple[Literal["workflow"], Transitions]:
        return p[0], p[2]

    @RULE(
        "wf_transitions wf_transition",
        "wf_transition",
    )
    def p_wf_transitions(
        self,
        p: tuple[Transitions] | tuple[Transitions, Transitions],
    ) -> Transitions:
        return p[0] if len(p) == 1 else p[0] | p[1]

    @RULE(
        "opt_wf_dec wf_method ';'",
        "opt_wf_dec wf_method TRANSITION name '#' wf_method ';'",
        "opt_wf_dec wf_method TRANSITION name '#' wf_method '{' wf_fields '}'",
    )
    def p_wf_transition(
        self,
        p: (
            tuple[TxDec, RuleName, str]
            | tuple[TxDec, RuleName, str, tuple[str, str], str, RuleName, str]
            | tuple[
                TxDec,
                RuleName,
                str,
                tuple[str, str],
                str,
                RuleName,
                str,
                TransitionEntries,
                str,
            ]
        ),
    ) -> Transitions:
        typ, prefix = p[3] if len(p) > 3 else ("", "")
        m = p[5] if len(p) > 3 else ""
        entries = p[7] if len(p) == 9 else {}
        return {p[1]: Transition(typ, prefix, p[0], m, entries)}

    @RULE(
        "LIST",
        "DETAILS",
        "CREATE",
        "MODIFY",
        "DELETE",
    )
    def p_wf_method(self, p: tuple[EffName]) -> EffName:
        return p[0]

    @RULE(
        "'<' ENTRYPOINT '>'",
        "'<' ALIAS '>'",
        "empty",
    )
    def p_opt_wf_dec(
        self,
        p: tuple[None] | tuple[str, Literal["entrypoint", "alias"], str],
    ) -> TxDec:
        return "" if len(p) == 1 else p[1]

    @RULE(
        "wf_fields wf_field",
        "wf_field",
    )
    def p_wf_fields(
        self,
        p: (tuple[TransitionEntries] | tuple[TransitionEntries, TransitionEntries]),
    ) -> TransitionEntries:
        return p[0] if len(p) == 1 else p[0] | p[1]

    @RULE("ID '=' wf_expr ';'")
    def p_wf_field(
        self,
        p: tuple[str, Literal["="], list[TransitionComputedExpr | None], str],
    ) -> dict[str, TransitionComputedField]:
        return {
            p[0]: TransitionComputedField(
                PipedExprList([x for x in p[2] if x is not None])
            )
        }

    @RULE(
        "wf_expr PIPEOP wf_term",
        "wf_term",
    )
    def p_wf_expr(
        self,
        p: (
            tuple[TransitionComputedExpr]
            | tuple[
                PipedExprList[TransitionComputedExpr],
                str,
                TransitionComputedExpr,
            ]
        ),
    ) -> PipedExprList[TransitionComputedExpr]:
        return (
            PipedExprList([p[0]])
            if len(p) == 1
            else PipedExprList([x for x in p[0] if x is not None] + [p[2]])
        )

    @RULE(
        # Lit
        "FALSE",
        "DECIMAL",
        "INT",
        "STRING",
        "TRUE",
        # Self
        "SELF opt_props",
        # Selves
        "SELVES",
        # Ref, Func
        "wf_func",
    )
    def p_wf_term(
        self,
        p: (
            tuple[Literal["self"], list[str]]
            | tuple[str, str]
            | tuple[int | str | Decimal | bool | Func | Ref | TaggedLit]
        ),
    ) -> TransitionComputedExpr | None:
        if (
            isinstance(p[0], Func)
            or isinstance(p[0], Ref)
            or isinstance(p[0], TaggedLit)
        ):
            return p[0]

        if p[0] == "selves":
            return Selves()
        elif len(p) == 2 and isinstance(p[1], list):
            return Self(p[1])

        return Lit(p[0])

    @RULE(
        "wf_args ',' wf_expr",
        "wf_expr",
    )
    def p_wf_args(
        self,
        p: (
            tuple[PipedExprList[TransitionComputedExpr]]
            | tuple[
                list[PipedExprList[TransitionComputedExpr]],
                str,
                PipedExprList[TransitionComputedExpr],
            ]
        ),
    ) -> list[PipedExprList[TransitionComputedExpr]]:
        return [p[0]] if len(p) == 1 else p[0] + [p[2]]

    @RULE(
        "prop",
        "prop '(' ')'",
        "prop '(' wf_args ')'",
        "prop '[' params ']' '(' wf_args ')'",
    )
    def p_wf_func(
        self,
        p: (
            tuple[list[str] | TaggedLit]
            | tuple[list[str], str, str]
            | tuple[list[str], str, list[PipedExprList[TransitionComputedExpr]], str]
            | tuple[
                list[str],
                str,
                list[FuncParam],
                str,
                str,
                list[PipedExprList[TransitionComputedExpr]],
                str,
            ]
        ),
    ) -> Ref | Func[TransitionComputedExpr] | TaggedLit:
        if isinstance(p[0], TaggedLit):
            return p[0]
        if len(p) == 1:
            return Ref(p[0])

        params = []
        args = []
        name = p[0][-1]
        prefix = p[0][: len(p[0]) - 1]
        if len(p) > 3:
            params = p[2] if len(p) == 7 else []
            args = p[2] if len(p) == 4 else p[5]
        return Func(name, prefix, params, args)


class PlyRestrictParser(
    DataSectionMixin,
    DncSectionMixin,
    EffectsSectionMixin,
    SecuritySectionMixin,
    WorkflowSectionMixin,
    RestrictParser,
):
    _parser: LRParser | None = None
    _lexer: RestrictLexer | None = None
    _debug: bool = False

    start = "file"

    @classmethod
    def dump_rules(cls, file_name: str = "rules.out"):  # pragma: nocover
        prod_rule = re.compile(r"( |^)([a-z_]+)")
        with open(file_name, "w") as f:
            for attr_name in dir(cls):
                if not attr_name.startswith("p_"):
                    continue
                attr = getattr(cls, attr_name)
                if attr.__doc__ is None:
                    continue
                rule = (
                    prod_rule.sub(r"\1<\2>", attr.__doc__)
                    .replace("|", "  |")
                    .replace("<empty>", "''")
                )
                print(rule, "\n", file=f)

    def __init__(self):
        self._errors: list[RestrictError] = []

    @property
    def errors(self) -> Sequence[RestrictError]:
        return [x for x in self._errors]

    @property
    def tokens(self) -> list[str]:
        if self._lexer is None:
            return []
        return self._lexer.tokens

    def build(
        self,
        debug=False,
        tracking=False,
        out_file="parser.out",
    ) -> PlyRestrictParser:
        self._debug = debug
        self._tracking = tracking
        self._lexer = RestrictLexer().build(debug=debug)
        self._parser = yacc(module=self, debug=debug, debugfile=out_file)
        return self

    def parse(self, content: str, source: Path) -> File | None:
        if self._parser is None:
            raise NameError("You must build the parser first")
        if len(content.strip()) == 0:
            return File(source, [], [])
        self._errors = []
        self._source = source
        result = self._parser.parse(
            content,
            lexer=self._lexer,
            tracking=self._tracking,
        )
        if result is not None:
            imports, resources = result
            result = File(source, imports, resources)
            for r in resources:
                r.file = result
        return result

    def p_error(self, t: LexToken):
        print("Syntax error in input", t)
        self._errors.append(ParsingError(t))
        if self._debug:
            raise SyntaxError(t)

    @RULE("")
    def p_empty(self, _):
        pass

    @RULE("opt_imports opt_resources")
    def p_file(self, p) -> tuple[list[Import], list[Res]]:
        return p[0], p[1]

    @RULE(
        "use opt_imports",
        "refer_to opt_imports",
        "empty",
    )
    def p_opt_imports(
        self, p: tuple[Import, list[Import]] | tuple[None]
    ) -> list[Import]:
        return [] if p[0] is None else [p[0]] + p[1]

    @RULE("REFER TO '<' PATH '>' AS ID")
    def p_refer_to(self, p: tuple[str, str, str, str, str, str, str]) -> Import:
        result = Import(Path(p[3]), p[6])
        return result

    @RULE("USE '<' PATH '>'")
    def p_use(self, p: tuple[str, str, str, str]) -> Import:
        result = Import(Path(p[2]), "")
        return result

    @RULE(
        "resource opt_resources",
        "empty",
    )
    def p_opt_resources(
        self,
        p: tuple[Res, list[Res]] | tuple[None],
    ) -> list[Res]:
        return [] if p[0] is None else [p[0]] + p[1]

    @RULE(
        "OVERRIDE TYPE ID '.' NAME '{' body '}'",
        "OVERRIDE TYPE NAME '{' body '}'",
        "TYPE NAME '{' body '}'",
    )
    def p_resource(
        self,
        p: (
            tuple[
                Literal["override"],
                str,
                str,
                Literal["."],
                str,
                Literal["{"],
                ResourceSections,
                Literal["}"],
            ]
            | tuple[
                Literal["override"],
                str,
                str,
                Literal["{"],
                ResourceSections,
                Literal["}"],
            ]
            | tuple[str, str, Literal["{"], ResourceSections, Literal["}"]]
        ),
    ) -> Res:
        override = False
        prefix = ""
        rtype = ""
        name = ""
        body = ({}, {}, {}, {}, {})
        if len(p) == 5:
            name = p[1]
            rtype = p[0]
            body = p[3]
        if len(p) == 6:
            override = True
            name = p[2]
            rtype = p[1]
            body = p[4]
        if len(p) == 8:
            override = True
            name = p[4]
            rtype = p[1]
            prefix = p[2]
            body = p[6]
        return Res(rtype, name, prefix, override, *body)

    @RULE(
        "ID '.' NAME",
        "NAME",
    )
    def p_name(self, p: tuple[str] | tuple[str, str, str]) -> tuple[str, str]:
        return (p[0], "") if len(p) == 1 else (p[2], p[0])

    @RULE(" ".join(y) for x in MAIN_SECTION_PERMUTATIONS for y in x)
    def p_body(self, p) -> ResourceSections:
        result: ResourceSections = ({}, {}, {}, {}, {})
        for name, section_def in p:
            match name:
                case "data":
                    result = (
                        section_def,
                        result[1],
                        result[2],
                        result[3],
                        result[4],
                    )
                case "dnc":
                    result = (
                        result[0],
                        section_def,
                        result[2],
                        result[3],
                        result[4],
                    )
                case "effects":
                    result = (
                        result[0],
                        result[1],
                        section_def,
                        result[3],
                        result[4],
                    )
                case "security":
                    result = (
                        result[0],
                        result[1],
                        result[2],
                        section_def,
                        result[4],
                    )
                case "workflow":
                    result = (
                        result[0],
                        result[1],
                        result[2],
                        result[3],
                        section_def,
                    )
        return result

    @RULE(
        "'.' ID opt_props",
        "empty",
    )
    def p_opt_props(
        self,
        p: tuple[None] | tuple[str, str, list[str]],
    ) -> list[str]:
        return [] if p[0] is None else [p[1]] + p[2]

    @RULE(
        "params ',' ID",
        "ID",
    )
    def p_params(
        self,
        p: tuple[str] | tuple[list[FuncParam], str, str],
    ) -> list[FuncParam]:
        return [FuncParam(p[0])] if len(p) == 1 else p[0] + [FuncParam(p[2])]

    @RULE(
        "prop '.' ID",
        "prop '.' DATATAG DATAVALUE",
        "ID",
        "DATATAG DATAVALUE",
    )
    def p_prop(
        self,
        p: (
            tuple[str]
            | tuple[list[str], str, str]
            | tuple[str, str]
            | tuple[list[str], str, str, str]
        ),
    ) -> list[str] | TaggedLit:
        if len(p) == 1:
            return [p[0]]
        if len(p) == 2:
            return TaggedLit(p[0], [], p[1])
        if len(p) == 3:
            return p[0] + [p[2]]
        return TaggedLit(p[2], p[0], p[3])

    @RULE(
        "OPTIONAL",
        "LIST",
        "SET",
        "OPTIONAL LIST",
        "OPTIONAL SET",
        "UNIQUE",
        "empty",
    )
    def p_field_mods(
        self,
        p: (
            tuple[None]
            | tuple[
                Literal["optional"]
                | Literal["list"]
                | Literal["set"]
                | Literal["unique"]
            ]
            | tuple[Literal["optional"], Literal["list"] | Literal["set"]]
        ),
    ) -> tuple[bool, bool, CollectionType]:
        if len(p) == 1 and p[0] == "unique":
            return False, True, None
        if len(p) == 1 and p[0] == "optional":
            return True, False, None
        elif len(p) == 1 and p[0] is not None and p[0] != "optional":
            return False, False, list if p[0] == "list" else set
        if len(p) == 2:
            return True, False, list if p[1] == "list" else set
        return False, False, None
