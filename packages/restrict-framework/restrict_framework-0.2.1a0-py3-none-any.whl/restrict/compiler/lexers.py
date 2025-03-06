import re
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .ply.lex import TOKEN, LexToken, lex

UNICODE_WHITESPACES = [
    "\u0009",  # character tabulation
    "\u000b",  # line tabulation
    "\u000d",  # carriage return
    "\u0020",  # space
    "\u00a0",  # no-break space
    "\u1680",  # ogham space mark
    "\u2000",  # en quad
    "\u2001",  # em quad
    "\u2002",  # en space
    "\u2003",  # em space
    "\u2004",  # three-per-em space
    "\u2005",  # four-per-em space
    "\u2006",  # six-per-em space
    "\u2007",  # figure space
    "\u2008",  # punctuation space
    "\u2009",  # thin space
    "\u200a",  # hair space
    "\u202f",  # narrow no-break space
    "\u205f",  # medium mathematical space
    "\u3000",  # ideographic space
]

LITERALS = "{}<>()|:,.*[];="


@dataclass(frozen=True)
class RestrictLexerError:
    value: str | bool | int | Decimal | None
    state: str
    lineno: int
    colno: int
    pos: int


class RestrictLexer:
    tokens = [
        "ALIAS",
        "AS",
        "CREATE",
        "DATA",
        "DATATAG",
        "DATAVALUE",
        "DECIMAL",
        "DELETE",
        "DETAILS",
        "UNIQUE",
        "DNC",
        "EFFECTS",
        "ENTRYPOINT",
        "FALSE",
        "ID",
        "INT",
        "LIST",
        "MODIFY",
        "NAME",
        "OPTIONAL",
        "OVERRIDE",
        "PATH",
        "PIPEOP",
        "REFER",
        "REL",
        "SECURITY",
        "SELF",
        "SELVES",
        "SET",
        "STRING",
        "TO",
        "TRANSITION",
        "TRUE",
        "TYPE",
        "USE",
        "VALUE",
        "WORKFLOW",
    ]
    states = [
        ("body", "exclusive"),
        ("compmod", "exclusive"),
        ("computation", "exclusive"),
        ("constrainedfield", "exclusive"),
        ("constraint", "exclusive"),
        ("coprop", "exclusive"),
        ("data", "exclusive"),
        ("datatag", "exclusive"),
        ("dnc", "exclusive"),
        ("effects", "exclusive"),
        ("effectsec", "exclusive"),
        ("field", "exclusive"),
        ("path", "exclusive"),
        ("refer", "exclusive"),
        ("referto", "exclusive"),
        ("refertoas", "exclusive"),
        ("rel", "exclusive"),
        ("reldec", "exclusive"),
        ("resource", "exclusive"),
        ("security", "exclusive"),
        ("securitysec", "exclusive"),
        ("use", "exclusive"),
        ("wfarrow", "exclusive"),
        ("wfattr", "exclusive"),
        ("wfdec", "exclusive"),
        ("wfend", "exclusive"),
        ("wfhash", "exclusive"),
        ("wfmeth", "exclusive"),
        ("wfname", "exclusive"),
        ("workflow", "exclusive"),
    ]
    colno = 0
    literals = LITERALS

    _lexer = None
    _errors = []

    @TOKEN(r"""(["'])(?:\\?.)*?\2""")
    def t_constraint_computation_STRING(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"[a-z]+`")
    def t_constraint_computation_DATATAG(self, t: LexToken) -> LexToken:
        t.lexer.push_state("datatag")
        if isinstance(t.value, str):
            t.value = t.value.rstrip("`")
        return self._update_colno(t)

    @TOKEN(r"[^`]*`")
    def t_datatag_DATAVALUE(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        if isinstance(t.value, str):
            t.value = t.value.rstrip("`")
        return self._update_colno(t)

    @TOKEN(r"(\.[0-9]+|[0-9]+\.[0-9]*)")
    def t_constraint_computation_DECIMAL(self, t: LexToken) -> LexToken:
        return self._update_colno(t, Decimal)

    @TOKEN(r"\.")
    def t_constraint_computation_DOT(self, t: LexToken) -> LexToken:
        t.lexer.push_state("coprop")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z]+`")
    def t_coprop_DATATAG(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("datatag")
        if isinstance(t.value, str):
            t.value = t.value.rstrip("`")
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_coprop_ID(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        return self._update_colno(t)

    @TOKEN(r"\b(party|place|thing|role|moment|interval)\b")
    def t_TYPE(self, t: LexToken) -> LexToken:
        t.lexer.push_state("resource")
        return self._update_colno(t)

    @TOKEN(r"\boverride\b")
    def t_OVERRIDE(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\brefer\b")
    def t_REFER(self, t: LexToken) -> LexToken:
        t.lexer.push_state("refer")
        return self._update_colno(t)

    @TOKEN(r"\bto\b")
    def t_refer_TO(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("referto")
        return self._update_colno(t)

    @TOKEN(r"\bas\b")
    def t_referto_AS(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("refertoas")
        return self._update_colno(t)

    @TOKEN(r">")
    def t_referto_endpath(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\buse\b")
    def t_USE(self, t: LexToken) -> LexToken:
        t.lexer.push_state("use")
        return self._update_colno(t)

    @TOKEN(r"<")
    def t_use_referto_startpath(self, t: LexToken) -> LexToken:
        t.lexer.push_state("path")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_refertoas_ID(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        return self._update_colno(t)

    @TOKEN(r">")
    def t_use_endpath(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z0-9_/]+")
    def t_path_PATH(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        return self._update_colno(t)

    @TOKEN(r"[A-Z][a-z0-9A-Z]*")
    def t_resource_NAME(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\{")
    def t_resource_LCB(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("body")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_resource_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\}")
    def t_body_data_dnc_effects_resource_effectsec_security_securitysec_workflow_RCB(
        self,
        t,
    ):
        t.lexer.pop_state()
        t.type = t.value
        return self._update_colno(t)

    @TOKEN(r"\bworkflow\b")
    def t_body_WORKFLOW(self, t: LexToken) -> LexToken:
        t.lexer.push_state("workflow")
        return self._update_colno(t)

    @TOKEN(r"\b(list|details|create|modify|delete)\b")
    def t_workflow_method(self, t: LexToken) -> LexToken:
        t.lexer.push_state("wfarrow")
        t.type = str(t.value).upper()
        return self._update_colno(t)

    @TOKEN(r";")
    def t_wfarrow_SEMI(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"->")
    def t_wfarrow_TRANSITION(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("wfname")
        return self._update_colno(t)

    @TOKEN(r"<")
    def t_workflow_LT(self, t: LexToken) -> LexToken:
        t.lexer.push_state("wfdec")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\b(alias|entrypoint)\b")
    def t_wfdec_decorator(self, t: LexToken) -> LexToken:
        t.type = str(t.value).upper()
        return self._update_colno(t)

    @TOKEN(r">")
    def t_wfdec_GT(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_wfname_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\.")
    def t_wfname_DOT(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[A-Z][a-z0-9A-Z]*")
    def t_wfname_NAME(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("wfhash")
        return self._update_colno(t)

    @TOKEN(r"\#")
    def t_wfhash_HASH(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("wfmeth")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\b(list|details|create|modify|delete)\b")
    def t_wfmeth_method(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("wfend")
        t.type = str(t.value).upper()
        return self._update_colno(t)

    @TOKEN(r";")
    def t_wfend_SEMI(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\{")
    def t_wfend_LCB(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("wfattr")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_wfattr_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"=")
    def t_wfattr_EQ(self, t: LexToken) -> LexToken:
        t.lexer.push_state("computation")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\}")
    def t_wfattr_RCB(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\beffects\b")
    def t_body_EFFECTS(self, t: LexToken) -> LexToken:
        t.lexer.push_state("effects")
        return self._update_colno(t)

    @TOKEN(r"\bcreate\b")
    def t_effects_CREATE(self, t: LexToken) -> LexToken:
        t.lexer.push_state("effectsec")
        return self._update_colno(t)

    @TOKEN(r"\bmodify\b")
    def t_effects_MODIFY(self, t: LexToken) -> LexToken:
        t.lexer.push_state("effectsec")
        return self._update_colno(t)

    @TOKEN(r"\bdelete\b")
    def t_effects_DELETE(self, t: LexToken) -> LexToken:
        t.lexer.push_state("effectsec")
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_effectsec_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"=")
    def t_effectsec_EQ(self, t: LexToken) -> LexToken:
        t.lexer.push_state("computation")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\bdnc\b")
    def t_body_DNC(self, t: LexToken) -> LexToken:
        t.lexer.push_state("dnc")
        return self._update_colno(t)

    @TOKEN(r"\bsecurity\b")
    def t_body_SECURITY(self, t: LexToken) -> LexToken:
        t.lexer.push_state("security")
        return self._update_colno(t)

    @TOKEN(r"\b(list|details|create|modify|delete)\b")
    def t_security_securitysec(self, t: LexToken) -> LexToken:
        t.lexer.push_state("securitysec")
        t.type = str(t.value).upper()
        return self._update_colno(t)

    @TOKEN(r"\*")
    def t_securitysec_STAR(self, t: LexToken) -> LexToken:
        t.lexer.push_state("constrainedfield")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_securitysec_ID(self, t: LexToken) -> LexToken:
        t.lexer.push_state("constrainedfield")
        return self._update_colno(t)

    @TOKEN(r"\{")
    def t_securitysec_LCB(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_dnc_ID(self, t: LexToken) -> LexToken:
        t.lexer.push_state("rel")
        return self._update_colno(t)

    @TOKEN(r"\[")
    def t_rel_LB(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\]")
    def t_rel_RB(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r",")
    def t_rel_COMMA(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\bunique\b")
    def t_rel_UNIQUE(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\boptional\b")
    def t_rel_OPTIONAL(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\blist\b")
    def t_rel_LIST(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\bset\b")
    def t_rel_SET(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"[A-Z][a-z0-9A-Z]*")
    def t_rel_NAME(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_rel_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\b(next|previous|root|details)\b")
    def t_reldec_REL(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r">")
    def t_reldec_LT(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"<")
    def t_dnc_GT(self, t: LexToken) -> LexToken:
        t.lexer.push_state("reldec")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\bdata\b")
    def t_body_DATA(self, t: LexToken) -> LexToken:
        t.lexer.push_state("data")
        return self._update_colno(t)

    @TOKEN(r"\{")
    def t_data_dnc_effects_effectsec_GCB(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_data_ID(self, t: LexToken) -> LexToken:
        t.lexer.push_state("field")
        return self._update_colno(t)

    @TOKEN(r"=")
    def t_field_EQUAL(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("computation")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r":")
    def t_field_COLON(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("constrainedfield")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\bmodify\b")
    def t_computation_MODIFY(self, t: LexToken) -> LexToken:
        t.lexer.push_state("compmod")
        return self._update_colno(t)

    @TOKEN(r"\bcreate\b")
    def t_computation_CREATE(self, t: LexToken) -> LexToken:
        t.lexer.push_state("compmod")
        return self._update_colno(t)

    @TOKEN(r";")
    def t_compmod_SEMI(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_compmod_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"[A-Z][a-z0-9A-Z]*")
    def t_compmod_NAME(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"{")
    def t_compmod_LCB(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("effectsec")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\bvalue\b")
    def t_computation_VALUE(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\bselves\b")
    def t_ANY_SELVES(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\bself\b")
    def t_ANY_SELF(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\bfalse\b")
    def t_constraint_computation_FALSE(self, t: LexToken) -> LexToken:
        t.value = False
        return self._update_colno(t)

    @TOKEN(r"\btrue\b")
    def t_constraint_computation_TRUE(self, t: LexToken) -> LexToken:
        t.value = True
        return self._update_colno(t)

    @TOKEN(r"\bunique\b")
    def t_constrainedfield_UNIQUE(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\boptional\b")
    def t_constrainedfield_OPTIONAL(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\blist\b")
    def t_constrainedfield_LIST(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\bset\b")
    def t_constrainedfield_SET(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_constrainedfield_computation_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r";")
    def t_computation_constrainedfield_constraint_rel__SEMI(
        self,
        t: LexToken,
    ) -> LexToken:
        t.lexer.pop_state()
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r":")
    def t_constrainedfield_securitysec_COLON(self, t: LexToken) -> LexToken:
        t.lexer.pop_state()
        t.lexer.push_state("constraint")
        t.type = str(t.value)
        return self._update_colno(t)

    @TOKEN(r"\|>")
    def t_constraint_computation_PIPEOP(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\bvalue\b")
    def t_constraint_VALUE(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"[0-9]+")
    def t_constraint_computation_rel_INT(self, t: LexToken) -> LexToken:
        return self._update_colno(t, int)

    @TOKEN(r"[a-z][a-z0-9_]*")
    def t_constraint_ID(self, t: LexToken) -> LexToken:
        return self._update_colno(t)

    @TOKEN(r"\n+")
    def t_ANY_newline(self, t: LexToken) -> None:
        t.lexer.lineno += len(str(t.value))
        t.colno = self.colno
        self.colno = 0

    @TOKEN(f"[{''.join(UNICODE_WHITESPACES)}]")
    def t_ANY_spaces(self, t: LexToken) -> None:
        self._update_colno(t)

    @TOKEN(f"[{re.escape(LITERALS)}]")
    def t_ANY_punct(self, t: LexToken) -> LexToken:
        t.type = str(t.value)
        return self._update_colno(t)

    def t_ANY_error(self, t: LexToken) -> None:
        self._add_error(t)
        self.colno += 1
        t.lexer.skip(1)

    def build(self, **kwargs):
        self._lexer = lex(module=self, **kwargs)
        return self

    def input(self, input: str) -> None:
        if self._lexer is None:
            raise RuntimeError(
                "Cannot set the input of an unbuilt RestrictLexer"
            )
        self._lexer.lineno = 1
        self.colno = 0
        while self._lexer.current_state() != "INITIAL":
            self._lexer.pop_state()
        self._errors = []
        self._lexer.input(input)

    def current_state(self) -> str:
        if self._lexer is not None:
            return self._lexer.current_state()
        return "<UNBUILT>"

    @property
    def errors(self):
        return [x for x in self._errors]

    def token(self):
        if self._lexer is None:
            raise RuntimeError("Cannot use an unbuilt RestrictLexer")
        return self._lexer.token()

    @property
    def lineno(self):
        if self._lexer is None:
            return -1
        return self._lexer.lineno

    @property
    def lexpos(self):
        if self._lexer is None:
            return -1
        return self._lexer.lexpos

    def __iter__(self):
        if self._lexer is None:
            raise RuntimeError("Cannot use an unbuilt RestrictLexer")
        return self._lexer.__iter__()

    def _update_colno(
        self, t: LexToken, fn: Callable[[str], Any] | None = None
    ) -> LexToken:
        t.colno = self.colno
        self.colno += len(str(t.value))
        if fn is not None:
            t.value = fn(str(t.value))
        return t

    def _add_error(self, t: LexToken):
        error = RestrictLexerError(
            t.value,
            self.current_state(),
            t.lineno,
            self.colno,
            t.lexpos,
        )
        self._errors.append(error)
