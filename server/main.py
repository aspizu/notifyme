import sqlite3
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from .misc import GET_endpoint_decorator, POST_endpoint_decorator
from .session import Sessions


class Main:
    def __init__(self):
        self.database = "database.db"
        self.routes: list[Route] = []
        self.sessions = Sessions(self)

    def POST(
        self,
        path: str,
        require_logged_in: bool = True,
        permissions: tuple[int, ...] = (),
    ):
        """Define a POST endpoint which takes in JSON and returns JSON.

        Usage:
          >>> @main.POST("/api/endpoint/path")
          ... def function(request: Request, session: Session) -> RESPONSE:
          ...     return {"data": "Some JSON data."}

        Omit the `session: Session` parameter if `require_logged_in` is set to `False`.

        Any other arguments will be taken from the request's JSON body.
        Any argument with the type in a union with `None` will be treated as optional and
        will default to `None` if not present in the request's JSON body.

        Raising a `Error` will respond with
          >>> {"success": False, "error": "Error message here..."}
        """
        return POST_endpoint_decorator(self, path, require_logged_in, permissions)

    def GET(
        self,
        path: str,
        require_logged_in: bool = True,
        permissions: tuple[int, ...] = (),
    ):
        """Define a GET endpoint which takes in query parameters and returns JSON.

        Usage:
          >>> @main.GET("/api/endpoint/path")
          ... def function(request: Request, session: Session) -> RESPONSE:
          ...     return {"data": "Some JSON data."}

        Omit the `session: Session` parameter if `require_logged_in` is set to `False`.

        Any other arguments will be taken from the request's query parameters.
        Any argument with the type in a union with `None` will be treated as optional and
        will default to `None` if that query parameter was not passed.

        Raising a `Error` will respond with
          >>> {"success": False, "error": "Error message here..."}
        """
        return GET_endpoint_decorator(self, path, require_logged_in, permissions)

    def application_route(self, request: Request) -> FileResponse:
        return FileResponse("client/app.html")

    def db(self):
        con = sqlite3.connect(self.database)
        con.row_factory = sqlite3.Row
        return con, con.cursor()

    def db_fetchone(self, query: str, params: list[Any]) -> dict[str, Any] | None:
        con, cur = self.db()
        row = cur.execute(query, params).fetchone()
        con.close()
        return row

    def db_fetchall(self, query: str, params: list[Any]) -> list[dict[str, Any]]:
        con, cur = self.db()
        cur = con.cursor()
        rows = cur.execute(query, params).fetchall()
        con.close()
        return rows

    def create_starlette_application(self) -> Starlette:
        return Starlette(
            routes=[
                *self.routes,
                Mount("/dist", app=StaticFiles(directory="dist"), name="dist"),
                Mount("/static", app=StaticFiles(directory="static"), name="static"),
                Route("/{path:path}", self.application_route),
            ],
        )
