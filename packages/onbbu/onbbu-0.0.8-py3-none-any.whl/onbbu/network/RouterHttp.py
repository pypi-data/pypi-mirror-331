from enum import Enum
from typing import Awaitable, Callable

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


EndpointType = Callable[[Request], Awaitable[JSONResponse]]


class RouterHttp:
    __router: list[Route]
    __prefix: str

    def __init__(self, prefix: str = ""):
        self.__router = []
        self.__prefix = prefix.rstrip("/")

    def add_route(self, path: str, endpoint: EndpointType, method: HTTPMethod):

        async def wrapper(request: Request) -> JSONResponse:
            """Forza a que el endpoint siempre retorne JSONResponse."""
            return await endpoint(request)

        full_path: str = f"{self.__prefix}{path}"

        self.__router.append(
            Route(path=full_path, endpoint=wrapper, methods=[method.value])
        )

    def get_router(self):
        return self.__router

    def get_routes(self):
        return [route.path for route in self.__router]

    def get_endpoints(self):
        return [route.endpoint for route in self.__router]

    def get_router(self):
        """Devuelve las rutas como un `Mount` si hay un prefijo, o una lista de rutas."""
        if self.__prefix:
            return [Mount(self.__prefix, routes=self.__router)]
        return self.__router
