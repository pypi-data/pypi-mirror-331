from contextlib import asynccontextmanager
from dataclasses import dataclass
import multiprocessing

from starlette.applications import Starlette

from onbbu.network.RouterHttp import RouterHttp
from onbbu.settings import environment
from onbbu.database import database


class ServerHttp:
    def __init__(self, port=8000):
        self.host = "0.0.0.0"
        self.port = port
        self.environment = environment
        self.reload = self.environment == "development"
        self.workers = 1 if self.reload else max(2, multiprocessing.cpu_count() - 1)

        self.server = Starlette(debug=True, routes=[], lifespan=self._lifespan)

        self.config = ConfigInit(http=self)

    @asynccontextmanager
    async def _lifespan(self, app: Starlette):
        """Gestor de eventos de vida para FastAPI"""
        await database.init()
        yield
        await database.close()

    def include_router(self, router: RouterHttp):
        """Agrega todas las rutas de un RouterHttp a la aplicación"""
        self.server.router.routes.extend(router.get_router())


def create_app(port=8000) -> ServerHttp:
    """Crea y retorna una instancia del servidor."""
    return ServerHttp(port=port)


@dataclass(frozen=True, slots=True)
class ConfigInit:
    http: ServerHttp
