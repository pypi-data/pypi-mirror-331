import argparse
import logging
import sys
from types import ModuleType
import requests
import json
import importlib
import os
import pkgutil
import importlib.util
import multiprocessing

from typing import Awaitable, Callable, List, Generic, Optional
from dataclasses import asdict, is_dataclass, dataclass
from contextlib import asynccontextmanager

from enum import Enum

from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor

from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.routing import Route


from rich.console import Console
from rich.text import Text
from rich.traceback import install
from tortoise import Tortoise
from aerich import Command
import uvicorn

from onbbu.types import T

BASE_DIR: str = os.getcwd()

sys.path.append(BASE_DIR)

environment: str = os.getenv("ENVIRONMENT", "development")

install()


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


DEFAULT_SERVER_URL: str = "https://api.onbbu.ar/logs"


class Logger:
    def __init__(self, log_file: Optional[str], server_url: Optional[str]):
        log_file = log_file or "onbbu.log"
        self.server_url = server_url
        self.executor = ThreadPoolExecutor(max_workers=5)

        self.logger = logging.getLogger("app_logger")
        self.logger.setLevel(logging.DEBUG)
        self.console = Console()

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
                    "level": record.levelname,
                    "message": record.getMessage(),
                }
                if hasattr(record, "extra_data") and record.extra_data:
                    log_entry["extra"] = record.extra_data
                return json.dumps(log_entry, ensure_ascii=False)

        log_format = JsonFormatter()

        file_handler = RotatingFileHandler(log_file, maxBytes=5000000, backupCount=3)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

    def log(self, level: LogLevel, message: str, extra_data=None):
        """Logs a message and prints it nicely in the terminal."""
        log_function = {
            LogLevel.DEBUG: self.logger.debug,
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
            LogLevel.CRITICAL: self.logger.critical,
        }.get(level, self.logger.info)

        log_data = {"level": level.value, "message": message, "extra": extra_data or {}}

        self.pretty_print(level, message, extra_data)

        log_function(message, extra={"extra_data": extra_data})

        if self.server_url:
            self.executor.submit(self.send_log, log_data)

    def pretty_print(self, level: LogLevel, message: str, extra_data: dict):
        """Prints logs in the terminal with colors and nice formatting using Rich."""
        level_colors = {
            LogLevel.DEBUG: "cyan",
            LogLevel.INFO: "green",
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red",
        }
        color = level_colors.get(level, "white")

        text = Text(f"[{level.value}] ", style=color)
        text.append(message, style="bold white")

        if extra_data:
            extra_json = json.dumps(extra_data, indent=2, ensure_ascii=False)
            text.append(f"\n{extra_json}", style="dim")

        self.console.print(text)

    def send_log(self, log_data):
        """Sends logs to the server asynchronously."""
        try:
            headers = {"Content-Type": "application/json"}
            requests.post(self.server_url, json=log_data, headers=headers, timeout=3)
        except requests.RequestException as e:
            self.logger.error(f"Error sending log to server: {e}")


logger: Logger = Logger(log_file=None, server_url=None)


class ConfigLoader:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def load_python_config(self, relative_path, attribute_name, default=None):
        """Upload a configuration file in Python format"""

        config_path = os.path.join(self.base_dir, *relative_path.split("/"))

        if not os.path.exists(config_path):
            print(
                f"⚠️ Advertencia: No se encontró `{relative_path}`. Se usará el valor por defecto."
            )
            return default

        spec = importlib.util.spec_from_file_location("config_module", config_path)

        config_module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(config_module)

        return getattr(config_module, attribute_name, default)


installed_apps: List[str] = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/settings.py",
    attribute_name="INSTALLED_APPS",
    default=[],
)


class Request(Request):
    pass


class ResponseNotFoundError(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:
        content = {"error": str(content)}

        return super().render(content, status_code=404)


class ResponseValueError(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:
        content = {"error": str(content)}

        return super().render(content, status_code=500)


class ResponseValidationError(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:
        content = {"detail": content.errors()}

        return super().render(content, status_code=400)


class Response(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:

        if is_dataclass(content):
            content = asdict(content)

        elif isinstance(content, list):
            content = [
                (asdict(item) if is_dataclass(item) else item) for item in content
            ]

        return super().render(content)


COMMANDS = {}


class BaseCommand:
    """Base class for all commands."""

    name: str
    help: str = "Base command description"

    def __init__(self):
        self.parser = None

    def add_arguments(self, parser):
        """Override this method to add custom arguments."""
        pass

    def handle(self, *args, **kwargs):
        """Override this method to implement command logic."""
        raise NotImplementedError("Subclasses must implement handle()")


def register_command(cls):
    """Decorator to register commands automatically."""
    COMMANDS[cls.name.lower()] = cls()
    return cls


class DatabaseManager:
    def __init__(self, INSTALLED_APPS: list[str]):
        self.database_url = os.getenv("DATABASE_URL", "sqlite://db.sqlite3")
        self.model_modules: list[str] = []
        self.INSTALLED_APPS = INSTALLED_APPS

    async def load_models(self) -> None:
        """Dynamically load models from installed applications."""
        for app in self.INSTALLED_APPS:
            model_path: str = f"pkg.{app}.infrastructure.persistence.models"

            try:
                module: ModuleType = importlib.import_module(model_path)
                logger.log(LogLevel.INFO, f"📦 Base module found: {model_path}")

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):
                        full_module_name = f"{model_path}.{module_name}"
                        self.model_modules.append(full_module_name)
                        logger.log(
                            LogLevel.INFO, f"✅ Loaded model: {full_module_name}"
                        )

            except ModuleNotFoundError as e:
                logger.log(
                    LogLevel.WARNING, f"⚠️ Warning: Could not import {model_path}: {e}"
                )

    async def init(self) -> None:
        """Initialize the database and apply the migrations."""

        await self.load_models()

        if not self.model_modules:
            logger.log(
                level=LogLevel.ERROR,
                message="❌ No models found. Check Check `INSTALLED_APPS`.",
            )

            return

        logger.log(
            level=LogLevel.INFO,
            message=f"🔄 Initializing Tortoise with models: {self.model_modules}",
        )

        tortoise_config = {
            "connections": {
                "default": self.database_url,
            },
            "apps": {
                "models": {
                    "models": self.model_modules,
                    "default_connection": "default",
                },
            },
        }

        await Tortoise.init(config=tortoise_config)

        self.command = Command(tortoise_config=tortoise_config)

        logger.log(LogLevel.INFO, "✅ Connected database. Generating schematics...")

        await Tortoise.generate_schemas()

        logger.log(LogLevel.INFO, "🎉 Schemes generated successfully.")

        await Tortoise.close_connections()

    async def migrate(self) -> None:
        """Generate new migrations."""

        await self.command.init()

        await self.command.migrate()

    async def upgrade(self) -> None:
        """Apply pending migrations."""

        await self.command.init()

        await self.command.upgrade()

    async def downgrade(self, steps=1) -> None:
        """Revert migrations (default: 1 step)."""

        await self.command.init()

        await self.command.downgrade(steps)

    async def history(self) -> None:
        """Show the history of applied migrations."""

        await self.command.init()

        await self.command.history()

    async def create_database(self) -> None:
        """Create the database if it does not exist."""

        logger.log(LogLevel.INFO, f"🛠️ Creating database...")

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise.generate_schemas()

        await Tortoise.close_connections()

    async def drop_database(self) -> None:
        """Delete all tables from the database."""

        logger.log(LogLevel.INFO, "🗑️ Dropping database...")

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise._drop_databases()

        await Tortoise.close_connections()

    async def reset_database(self) -> None:
        """Delete and recreate the database."""

        logger.log(LogLevel.INFO, "🔄 Resetting database...")

        await self.drop_database()

        await self.create_database()

    async def show_status(self) -> None:
        """Show the current status of the database."""

        await self.command.init()

        applied = await self.command.history()

        logger.log(LogLevel.INFO, f"📜 Applied migrations:\n{applied}")

    async def apply_all_migrations(self) -> None:
        """Generate and apply all migrations in a single step."""

        logger.log(LogLevel.INFO, "🚀 Applying all migrations...")

        await self.migrate()

        await self.upgrade()

    async def rollback_all_migrations(self) -> None:
        """Revert all migrations to the initial state."""

        logger.log(LogLevel.INFO, "⏪ Rolling back all migrations...")

        await self.command.init()

        while True:
            try:
                await self.command.downgrade(1)
            except Exception:
                logger.log(LogLevel.INFO, "✅ No more migrations to revert.")
                break

    async def seed_data(self) -> None:
        """Insert initial data into the database."""

        logger.log(LogLevel.INFO, "🌱 Seeding initial data...")

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise.close_connections()

    async def close(self) -> None:
        """Close the database connections."""
        logger.log(LogLevel.INFO, "🔌 Closing database connections...")
        await Tortoise.close_connections()
        logger.log(LogLevel.INFO, "✅ Database connections closed.")


database = DatabaseManager(installed_apps)


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


EndpointHttpType = Callable[[Request], Awaitable[JSONResponse]]


class RouterHttp:
    __router: list[Route]
    __prefix: str

    def __init__(self, prefix: str = ""):
        self.__router = []
        self.__prefix = prefix.rstrip("/")

    def add_route(self, path: str, endpoint: EndpointHttpType, method: HTTPMethod):

        full_path: str = f"{self.__prefix}{path}"

        self.__router.append(
            Route(path=full_path, endpoint=endpoint, methods=[method.value])
        )

    def get_router(self):
        return self.__router

    def get_routes(self):
        return [route.path for route in self.__router]

    def get_endpoints(self):
        return [route.endpoint for route in self.__router]


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


server: ServerHttp = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/main.py",
    attribute_name="server",
    default=None,
)


@register_command
class CommandMigrate(BaseCommand):
    """Command to run the server."""

    name: str = "migrate"
    help: str = "Command to run the server."

    # def add_arguments(self, parser):
    #    parser.add_argument(
    #        "--host", type=str, default="0.0.0.0", help="Host for the server"
    #    )
    #    parser.add_argument(
    #        "--port", type=int, default=8000, help="Port for the server"
    #    )

    async def handle(self, args):

        await database.init()

        await database.migrate()

        await database.close()


@register_command
class CommandRunServer(BaseCommand):
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


class Manager:
    """Command-line manager for executing various tasks."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Management script",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=30
            ),
        )

        self.subparsers = self.parser.add_subparsers(dest="command", metavar="command")

        self.INSTALLED_APPS = installed_apps

        self.load_commands()

    def internal_command(self):
        """Execute a system command."""

        commands: list[BaseCommand] = [
            CommandRunServer(),
            CommandMigrate(),
        ]

        for command in commands:
            COMMANDS[command.name] = command

    def load_commands(self):
        """Dynamically load commands from installed apps."""
        for app in self.INSTALLED_APPS:
            commands_path = f"pkg.{app}.application.commands"
            try:
                module = importlib.import_module(commands_path)

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):

                        full_module_name = f"{commands_path}.{module_name}"

                        command_module = importlib.import_module(full_module_name)

                        if hasattr(command_module, "Command"):
                            command_instance = command_module.Command()
                            COMMANDS[command_instance.name] = command_instance

            except ModuleNotFoundError as e:
                print(f"Warning: Could not import {commands_path}: {e}")

        self.internal_command()

        for name, command in COMMANDS.items():
            command_parser = self.subparsers.add_parser(name, help=command.help)
            command.add_arguments(command_parser)
            command.parser = command_parser

    def execute(self):
        """Parse and execute commands dynamically."""
        args = self.parser.parse_args()
        command = COMMANDS.get(args.command)

        if command:
            command.handle(args)
        else:
            self.parser.print_help()


def main():

    parser = argparse.ArgumentParser(description="CLI para manejar Onbbu")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Iniciar el servidor")

    subparsers.add_parser("makemigrations", help="Generar una nueva migración")

    subparsers.add_parser("migrate", help="Aplicar migraciones")

    subparsers.add_parser("routes", help="Listar rutas de")

    args = parser.parse_args()

    parser.print_help()

    # if args.command == "run":
    #    run_server(server=server)
    # elif args.command == "routes":
    #    list_routes()
    # else:
    #    parser.print_help()


__all__ = [
    "COMMANDS",
    "BaseCommand",
    "register_command",
    "DatabaseManager",
    "Paginate",
    "PaginateDTO",
    "createPaginateResponse",
    "ConsoleStyle",
    "Response",
    "ResponseNotFoundError",
    "ResponseValidationError",
    "ResponseValueError",
    "HexoServer",
]
