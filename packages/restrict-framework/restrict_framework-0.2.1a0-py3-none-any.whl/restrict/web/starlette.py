import logging
from importlib import import_module
from typing import override
import os
from argparse import ArgumentParser
from pathlib import Path
from functools import partial

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from restrict.compiler import RestrictCompiler
from restrict.compiler.compiled import Repository
from restrict.resources.starlette import ResourceMiddleware


class SingletonEndpoint(HTTPEndpoint):
    def __init__(self, scope, receive, send, repository: Repository):
        super().__init__(scope, receive, send)
        self.repo = repository

    @override
    async def dispatch(self) -> None:
        logging.info(f"STATIC: {self.repo.app_resource_type.__name__}")
        return await super().dispatch()

    async def get(self, request):
        instance = await self.repo.get_object(self.scope, None)
        if instance is not None:
            return JSONResponse(instance._to_json("details"))
        return JSONResponse({}, status_code=404)

    async def patch(self, request):
        return JSONResponse({"msg": "updating one"})

    async def post(self, request):
        instance = await self.repo.get_object(self.scope, None)
        if instance is not None:
            data = await request.json()
            instance = instance._alter(data)
            await self.repo.save_object(self.scope, None, instance)
            return JSONResponse(instance._to_json("details"))
        return JSONResponse({}, status_code=404)

    async def put(self, request):
        print(await request.json())
        return JSONResponse({"msg": "creating or updating one"})


class ResourceEndpoint(HTTPEndpoint):
    def __init__(self, scope, receive, send, repository):
        super().__init__(scope, receive, send)
        self.repo = repository

    def __call__(self, *args):
        super().__init__(*args)
        return self

    @override
    async def dispatch(self) -> None:
        logging.info(f"DYNAMIC: {self.repo.__name__}")
        return await super().dispatch()

    async def get(self, request):
        if "id" in request.path_params:
            return JSONResponse({"msg": "getting one"})
        return JSONResponse({"msg": "getting many"})

    async def patch(self, request):
        print(await request.json())
        return JSONResponse({"msg": "updating one"})

    async def post(self, request):
        print(await request.json())
        return JSONResponse({"msg": "creating one"})

    async def put(self, request):
        print(await request.json())
        return JSONResponse({"msg": "creating or updating one"})

    async def delete(self, request):
        if "id" in request.path_params:
            return JSONResponse({"msg": "deleting one"})
        return JSONResponse({"msg": "deleting many"})


argparser = ArgumentParser()
argparser.add_argument(
    "--log-level",
    choices=["critical", "error", "warning", "info", "debug", "trace"],
    default="info",
)
args, _ = argparser.parse_known_args()
logging.basicConfig(
    format="%(levelname)-9s %(message)s",
    level=args.log_level.upper(),
)
root_var = os.environ.get("RESTRICT_ROOT")
if root_var is None:
    logging.critical("RESTRICT_ROOT is not defined")
    raise ValueError()
base_var = os.environ.get("RESTRICT_BASE", os.getcwd())

root = Path(root_var)
base = Path(base_var)

if not root.is_absolute():
    root = base / root

if not root.exists():
    logging.critical(f"ROOT does not exist at {root}")
    raise ValueError()

logging.info(f"RESTRICT_ROOT={root}")
logging.info(f"RESTRICT_BASE={base}")

compiler = RestrictCompiler()
restrict_app = compiler.compile(root, base)

routes = []
middleware = []
for name in restrict_app.paths:
    Res = restrict_app.get_resource(name)
    Repo = restrict_app.get_repository(name)
    if issubclass(Repo, ResourceMiddleware):
        repo = Repo(None, Res)
        for dep in repo.get_middleware_dependencies():
            mod = import_module(dep.module)
            dep_mw_cls = getattr(mod, dep.name)
            mw = Middleware(dep_mw_cls, **dep.kwargs)
            middleware.append(mw)
        middleware.append(Middleware(partial(Repo, app_resource_type=Res)))
    else:
        repo = Repo(Res)
    route = Res.__qualname__
    if Res._is_singleton:
        routes.append(Route(route, partial(SingletonEndpoint, repository=repo)))
    else:
        routes.append(Route(route, partial(ResourceEndpoint, repository=repo)))
        routes.append(
            Route(route + "/{id}", partial(ResourceEndpoint, repository=repo))
        )

app = Starlette(middleware=middleware, routes=routes)
