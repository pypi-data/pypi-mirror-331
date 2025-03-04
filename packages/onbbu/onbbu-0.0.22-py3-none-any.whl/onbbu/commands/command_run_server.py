import uvicorn

from onbbu.commands.main import BaseCommand, register_command
from onbbu.logger.main import LogLevel
from onbbu.settings import logger, server

@register_command
class Command(BaseCommand):
    """Command to run the server."""

    name: str = "run"
    help: str = "Command to run the server."

    # def add_arguments(self, parser):
    #    parser.add_argument(
    #        "--host", type=str, default="0.0.0.0", help="Host for the server"
    #    )
    #    parser.add_argument(
    #        "--port", type=int, default=8000, help="Port for the server"
    #    )

    def handle(self, args):
        
        if hasattr(server, "server"):
            logger.log(
                level=LogLevel.INFO,
                message=f"🚀 Iniciando servidor en {server.host}:{server.port} ...",
            )

            for route in server.server.routes:
                logger.log(
                    level=LogLevel.INFO,
                    message=f"🔗 {route.path} -> {route.name} ({route.methods})",
                )

            uvicorn.run(
                "internal.main:server.server",
                host=server.host,
                port=server.port,
                reload=server.reload,
                workers=server.workers,
            )

        else:
            logger.log(
                level=LogLevel.ERROR,
                message=f"❌ `internal/main.py` no contiene una instancia `server`.",
            )
