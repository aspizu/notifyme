from .main import Main

main = Main()

from . import post as _
from . import reaction as _
from . import user as _

application = main.create_starlette_application()
