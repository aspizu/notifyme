from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import session
from .lib import GET_endpoint_decorator, POST_endpoint_decorator


class App:
    def __init__(self) -> None:
        self.routes: list[Route] = []
        self.sessions = session.Sessions()

    def POST(self, path: str, require_logged_in: bool = True):
        return POST_endpoint_decorator(self, path, require_logged_in=require_logged_in)

    def GET(self, path: str, require_logged_in: bool = True):
        return GET_endpoint_decorator(self, path, require_logged_in=require_logged_in)

    def frontend(self, request: Request) -> Response:
        return FileResponse("static/app.html")

    def create_starlette_application(self):
        return Starlette(
            debug=True,
            routes=[
                *self.routes,
                Mount("/static", app=StaticFiles(directory="static"), name="static"),
                Route("/{path:path}", self.frontend),
            ],
        )
