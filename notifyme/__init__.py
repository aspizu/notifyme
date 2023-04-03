from .app import App

app = App()

from . import notification as _
from . import user as _

starlette_application = app.create_starlette_application()
