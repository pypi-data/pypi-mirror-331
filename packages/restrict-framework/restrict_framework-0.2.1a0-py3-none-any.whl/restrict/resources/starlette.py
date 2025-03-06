from __future__ import annotations

import logging
import os
from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, cast, override

from ..compiler.ast import DataComputedField, PipedExprList, Self
from ..compiler.compiled import AppResource, Repository
from ..compiler.types import Module
from ..types.builtins import Boolean
from ..types.text import Text
from .specs import SpecField, SpecResource


@dataclass(frozen=True)
class MiddlewareSpec:
    module: str
    name: str
    kwargs: dict


class ResourceMiddleware(Repository):
    def __init__(self, app, app_resource_type: type[AppResource]):
        super().__init__(app_resource_type)
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            if scope["type"] == "lifespan":
                await self.initialize_middleware(scope)
            elif scope["type"] == "http":
                await self.run_middleware(scope)
        except Exception as e:
            logging.critical("Failed to start middleware", exc_info=e)
            exit(1)
        await self.app(scope, receive, send)

    @abstractmethod
    def get_middleware_dependencies(self) -> list[MiddlewareSpec]: ...

    @abstractmethod
    async def initialize_middleware(self, scope) -> None: ...

    @abstractmethod
    async def run_middleware(self, scope) -> None: ...


class GlobalMiddlewareRepository(ResourceMiddleware):
    @override
    async def create_object(
        self,
        scope,
        data: dict[str, Any],
    ) -> AppResource | None:
        if "app" in scope:
            app = scope["app"]
            instance = self.app_resource_type._create(data)
            if isinstance(instance, Global):
                if not hasattr(app.state, instance.key):
                    await self.save_object(scope, None, instance)
                else:
                    instance = await self.get_object(scope, None)
            return instance

    @override
    async def get_object(self, scope, id: Any) -> AppResource | None:
        if "app" in scope:
            app = scope["app"]
            if issubclass(self.app_resource_type, Global):
                instance = cast(Global, self.app_resource_type._create({}))
                key = instance.key
                if hasattr(app.state, key):
                    return getattr(app.state, key)

    @override
    async def save_object(self, scope, id: Any | None, o: Global) -> None:
        if "app" in scope:
            app = scope["app"]
            if issubclass(self.app_resource_type, Global):
                setattr(app.state, o.key, o)

    @override
    def get_middleware_dependencies(self):
        return []

    @override
    async def initialize_middleware(self, scope) -> None:
        await self.create_object(scope, {})

    @override
    async def run_middleware(self, scope):
        pass


class SessionMiddlewareRepository(ResourceMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialized = False

    @override
    async def create_object(
        self,
        scope,
        data: dict[str, Any],
    ) -> AppResource | None:
        if "session" in scope:
            session = scope["session"]
            instance = self.app_resource_type._create(data)
            sess = cast(Session, instance)
            key = sess.key
            if key not in session:
                await self.save_object(scope, None, sess)
            else:
                instance = await self.get_object(scope, None)
            return instance

    @override
    async def get_object(self, scope, id: Any) -> AppResource | None:
        if "session" in scope:
            session = scope["session"]
            instance = self.app_resource_type._create({})
            if isinstance(instance, Session):
                key = instance.key
                return instance._hydrate(session[key])

    @override
    async def save_object(
        self,
        scope,
        id: Any | None,
        o: Session,
    ) -> None:
        if "session" in scope and isinstance(o, AppResource):
            session = scope["session"]
            session[o.key] = o._to_json("all")

    @override
    def get_middleware_dependencies(self):
        instance = cast(Session, self.app_resource_type._create({}))
        return [
            MiddlewareSpec(
                "starlette.middleware.sessions",
                "SessionMiddleware",
                {
                    "secret_key": instance.session_secret,
                    "https_only": instance.https_only,
                },
            )
        ]

    @override
    async def initialize_middleware(self, scope) -> None:
        pass

    @override
    async def run_middleware(self, scope):
        await self.create_object(scope, {})


class Global(SpecResource):
    key: str

    _is_singleton = True
    _repository = GlobalMiddlewareRepository
    _order = 1

    specs = {
        "key": SpecField(Text(), lambda _: True, False),
    }
    spec_effects = {
        "key": SpecResource._field_effects({"create": lambda _: "RESTRICT_GLOBAL"})
    }
    spec_security = {"key": SpecResource._field_security([])}

    fields = {"global": DataComputedField(PipedExprList([Self([])]))}
    field_effects = {}
    field_security = {}

    @override
    def get_global_names(self) -> Sequence[str]:
        return ["global"]

    @property
    @override
    def field_order(self) -> list[str]:
        return ["key", "global"]


class Session(SpecResource):
    key: str
    session_secret: str
    https_only: bool

    _is_singleton = True
    _repository = SessionMiddlewareRepository
    _order = 2

    specs = {
        "key": SpecField(Text(), lambda _: True, False),
        "session_secret": SpecField(Text(), lambda _: True, False),
        "https_only": SpecField(Boolean(), lambda _: True, False),
    }
    spec_effects = {
        "key": SpecResource._field_effects(
            {
                "create": lambda _: os.getenv(
                    "RESTRICT_SESSION_KEY_NAME", "RESTRICT_SESSION"
                )
            }
        ),
        "session_secret": SpecResource._field_effects(
            {"create": lambda _: os.environ["RESTRICT_SESSION_SECRET"]}
        ),
        "https_only": SpecResource._field_effects(
            {
                "create": lambda _: os.getenv("RESTRICT_ENV", "production")
                == "production"
            }
        ),
    }
    spec_security = {
        "key": SpecResource._field_security([]),
        "session_secret": SpecResource._field_security([]),
        "https_only": SpecResource._field_security([]),
    }

    fields = {}
    field_effects = {}
    field_security = {}

    @override
    def get_global_names(self) -> Sequence[str]:
        return []

    @property
    @override
    def field_order(self) -> list[str]:
        return ["key", "session_secret", "https_only"]


restrict_module = Module(
    {},
    {},
    {x.__name__: x() for x in [Global, Session]},
)
