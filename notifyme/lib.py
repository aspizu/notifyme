"""
Basically a minimalistic version of Pydantic and FastAPI.
"""

import sqlite3
import types
from time import time as _time
from typing import TYPE_CHECKING, Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from . import session

if TYPE_CHECKING:
    from rich.repr import RichReprResult

    from .app import App


JSON = (
    None
    | bool
    | int
    | float
    | str
    | list["JSON"]
    | dict[None | bool | int | float | str, "JSON"]
)

try:
    from rich import print
except ImportError:
    print = print


def db():
    return sqlite3.connect("1.db")


def time() -> int:
    return int(_time())


def successful_response(data: dict[str, JSON] = {}, **kwargs: JSON):
    return JSONResponse({"success": True, **kwargs, **data})


def failed_response(exception: str, data: dict[str, JSON] = {}, **kwargs: JSON):
    return JSONResponse({"success": False, "exception": exception, **data, **kwargs})


def exception_response(
    exception: BaseException, data: dict[str, JSON] = {}, **kwargs: JSON
):
    return JSONResponse(
        {"success": False, "exception": str(exception), **data, **kwargs}
    )


def isoftype(obj: Any, T: Any) -> bool:
    if T in (str, int, float, bool, type(None)):
        return isinstance(obj, T)
    elif T is None:
        return obj is None
    elif issubclass(T, Model):
        try:
            T(obj)
            return True
        except TypeError:
            pass
    elif isinstance(T, types.UnionType):
        return any(isoftype(obj, subT) for subT in T.__args__)
    elif isinstance(T, types.GenericAlias) and T.__name__ == "list":
        return isinstance(obj, list) and all(
            isoftype(each, T.__args__[0]) for each in obj  # type: ignore
        )
    elif isinstance(T, types.GenericAlias) and T.__name__ == "dict":
        return isinstance(obj, dict) and all(
            isoftype(each, T.__args__[1]) for each in obj.values()  # type: ignore
        )
    return False


class Model:
    def __init__(self, data: dict[str, Any]):
        for name, T in type(self).__annotations__.items():
            try:
                value = data[name]
            except KeyError:
                raise TypeError(f"DATA DOES NOT HAVE FIELD {name}")
            if not isoftype(value, T):
                raise TypeError(f"FIELD {name} HAS INCORRECT TYPE")
            setattr(self, name, T(data[name]) if issubclass(T, Model) else data[name])

    def to_dict(self):
        data: dict[str, Any] = {}
        for name in type(self).__annotations__:
            value = getattr(self, name)
            data[name] = value.to_dict() if isinstance(value, Model) else value
        return data

    def __repr__(self):
        return f"{type(self).__name__}({self.to_dict()!r})"

    def __rich_repr__(self) -> "RichReprResult":
        for name in type(self).__annotations__:
            yield name, getattr(self, name)


def POST_endpoint_decorator(app: "App", path: str, require_logged_in: bool = True):
    def decorator(func: Any):
        assert func.__annotations__["return"] is Response
        assert func.__annotations__["request"] is Request
        if require_logged_in:
            assert func.__annotations__["session"] is session.Session
        else:
            assert "session" not in func.__annotations__

        async def endpoint(request: Request) -> Response:
            kwargs = {}
            if require_logged_in:
                session = app.sessions.get(request)
                if session is None:
                    return failed_response(
                        "this API endpoint requires you to be logged in."
                    )
                kwargs["session"] = session
            data = await request.json()
            for name, t in func.__annotations__.items():
                if name in ("app", "request", "session", "return"):
                    continue
                try:
                    value = data[name]
                except KeyError:
                    return failed_response(f"FIELD {name} HAS INCORRECT TYPE")
                if not isoftype(value, t):
                    return failed_response(f"{value} is not of type {t}")
                kwargs[name] = value if issubclass(t, Model) else value
            return await func(request, **kwargs)

        app.routes.append(Route(path, endpoint=endpoint, methods=["POST"]))
        return func

    return decorator


def GET_endpoint_decorator(app: "App", path: str, require_logged_in: bool = True):
    def decorator(func: Any):
        async def endpoint(request: Request) -> Response:
            if require_logged_in:
                session = app.sessions.get(request)
                if session is None:
                    return failed_response(
                        "this API endpoint requires you to be logged in."
                    )
                return await func(request, session, **request.path_params)
            else:
                return await func(request, **request.path_params)

        app.routes.append(Route(path, endpoint=endpoint, methods=["GET"]))
        return func

    return decorator