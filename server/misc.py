"""Basically a minimalistic version of FastAPI."""

import builtins
from types import GenericAlias, UnionType
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

if TYPE_CHECKING:
    from rich.repr import RichReprResult

    from .main import Main


try:
    from rich import print
except ImportError:
    print = print


JSON = (
    None
    | bool
    | int
    | float
    | str
    | list["JSON"]
    | dict[None | bool | int | float | str, "JSON"]
)
# RESPONSE = dict[None | bool | int | float | str, JSON]
RESPONSE = Any


def strtype(t: Any) -> str:
    if isinstance(t, type):
        return t.__name__
    return str(t)


class Error(Exception):
    def __init__(self, exception: str):
        super().__init__(exception)

    def to_JSONResponse(self) -> JSONResponse:
        return JSONResponse({"success": False, "error": self.args[0]})


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

    def to_dict(self) -> RESPONSE:
        data: RESPONSE = {}
        for name in type(self).__annotations__:
            value = getattr(self, name)
            data[name] = value.to_dict() if isinstance(value, Model) else value
        return data

    def __repr__(self):
        return f"{type(self).__name__}({self.to_dict()!r})"

    def __rich_repr__(self) -> "RichReprResult":
        for name in type(self).__annotations__:
            yield name, getattr(self, name)


def isoftype(obj: Any, T: Any) -> bool:
    if T in (str, int, float, bool, type(None)):
        return isinstance(obj, T)
    elif T is None:
        return obj is None
    elif isinstance(T, UnionType):
        return any(isoftype(obj, subT) for subT in T.__args__)
    elif isinstance(T, GenericAlias) and T.__name__ == "list":
        return isinstance(obj, list) and all(
            isoftype(each, T.__args__[0]) for each in obj  # type: ignore
        )
    elif isinstance(T, GenericAlias) and T.__name__ == "dict":
        return isinstance(obj, dict) and all(
            isoftype(each, T.__args__[1]) for each in obj.values()  # type: ignore
        )
    elif issubclass(T, Model):  # type: ignore
        try:
            T(obj)
            return True
        except TypeError:
            pass
    return False


def parse_query_parameter(parameter: str, type: Any) -> Any:
    try:
        if type is bool:
            return bool(parameter)
        if type is str:
            return parameter
        if type is int:
            return int(parameter)
        if type is float:
            return float(parameter)
        if type in (type(None), None):
            return None
        if isinstance(type, UnionType):
            for member_type in type.__args__:
                try:
                    return parse_query_parameter(parameter, member_type)
                except TypeError:
                    continue
    except (ValueError, TypeError):
        raise TypeError


EndpointFunction = Callable[..., Awaitable[RESPONSE]]


def validate_endpoint_function(
    func: EndpointFunction, require_logged_in: bool, permissions: tuple[int, ...]
):
    from . import session

    if len(permissions) > 0 and not require_logged_in:
        raise SyntaxError(
            "If permissions are given, require_logged_in must be set to True."
        )
    if func.__annotations__["return"] != RESPONSE:
        raise SyntaxError("Return type must be - .misc.RESPONSE")
    if list(func.__annotations__.items())[0] != ("request", Request):
        raise SyntaxError(
            "First parameter must be - request: starlette.requests.Request"
        )
    if require_logged_in and list(func.__annotations__.items())[1] != (
        "session",
        session.Session,
    ):
        raise SyntaxError("Second parameter must be - session: .sessions.Session")


def GET_endpoint_decorator(
    main: "Main", path: str, require_logged_in: bool, permissions: tuple[int, ...]
):
    def decorator(func: EndpointFunction) -> EndpointFunction:
        validate_endpoint_function(func, require_logged_in, permissions)

        async def endpoint(request: Request) -> Response:
            params = {**request.path_params, **request.query_params}
            kwargs: dict[str, Any] = {"request": request}
            if require_logged_in:
                kwargs["session"] = main.sessions.get_session(request)
                if kwargs["session"] is None:
                    return Error(
                        "This API endpoint requires you to be logged in."
                    ).to_JSONResponse()
                if (
                    len(permissions) > 0
                    and kwargs["session"].permission not in permissions
                ):
                    return Error(
                        "Unauthorized to access this endpoint."
                    ).to_JSONResponse()
            for name, type in func.__annotations__.items():
                if name in ("request", "session", "return"):
                    continue
                if name not in params:
                    if (
                        isinstance(type, UnionType)
                        and builtins.type(None) in type.__args__
                    ):
                        params[name] = None
                    else:
                        return Error(
                            f"Missing query parameter {name} of type {strtype(type)}."
                        ).to_JSONResponse()
                try:
                    kwargs[name] = parse_query_parameter(params[name], type)
                except TypeError:
                    return Error(
                        f"Query parameter {name} must be of type {strtype(type)}."
                    ).to_JSONResponse()
            try:
                response = await func(**kwargs)
            except Error as err:
                return err.to_JSONResponse()
            return JSONResponse({"success": True, **response})

        main.routes.append(Route(path, endpoint, methods=["GET"]))
        return func

    return decorator


def POST_endpoint_decorator(
    main: "Main", path: str, require_logged_in: bool, permissions: tuple[int, ...]
):
    def decorator(func: EndpointFunction) -> EndpointFunction:
        validate_endpoint_function(func, require_logged_in, permissions)

        async def endpoint(request: Request) -> Response:
            data: dict[str, Any] = await request.json()
            kwargs: dict[str, Any] = {"request": request}
            if require_logged_in:
                kwargs["session"] = main.sessions.get_session(request)
                if kwargs["session"] is None:
                    return Error(
                        "This API endpoint requires you to be logged in."
                    ).to_JSONResponse()
                if (
                    len(permissions) > 0
                    and kwargs["session"].permission not in permissions
                ):
                    return Error(
                        "Unauthorized to access this endpoint."
                    ).to_JSONResponse()
            for name, type in func.__annotations__.items():
                if name in ("request", "session", "return"):
                    continue
                if name not in data:
                    if (
                        isinstance(type, UnionType)
                        and builtins.type(None) in type.__args__
                    ):
                        data[name] = None
                    else:
                        return Error(
                            f"Missing parameter {name} of type {strtype(type)}."
                        ).to_JSONResponse()
                if not isoftype(data[name], type):
                    return Error(
                        f"Parameter {name} must be of type {strtype(type)}."
                    ).to_JSONResponse()
                kwargs[name] = (
                    type(data[name])
                    if isinstance(type, builtins.type) and issubclass(type, Model)
                    else data[name]
                )
            try:
                response = await func(**kwargs)
            except Error as err:
                return err.to_JSONResponse()
            return JSONResponse({"success": True, **response})

        main.routes.append(Route(path, endpoint, methods=["POST"]))
        return func

    return decorator
