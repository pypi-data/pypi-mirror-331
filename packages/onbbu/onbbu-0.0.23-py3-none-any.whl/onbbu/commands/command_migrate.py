from .register_command import register_command
from .BaseCommand import BaseCommand

from onbbu.logger import LogLevel, logger
from onbbu.database import database


@register_command
class Command(BaseCommand):
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
