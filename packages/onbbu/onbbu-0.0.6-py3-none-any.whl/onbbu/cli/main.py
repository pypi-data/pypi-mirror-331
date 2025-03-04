import argparse
import asyncio

from onbbu.cli.cli_run_server import run_server
from onbbu.cli.cli_create_migration import create_migration
from onbbu.cli.cli_apply_migrations import apply_migrations
from onbbu.cli.cli_list_routes import list_routes


def main():
    parser = argparse.ArgumentParser(description="CLI para manejar HexoServer")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Iniciar el servidor")

    subparsers.add_parser("makemigrations", help="Generar una nueva migración")

    subparsers.add_parser("migrate", help="Aplicar migraciones")

    subparsers.add_parser("routes", help="Listar rutas de")

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(run_server())
    elif args.command == "makemigrations":
        create_migration()
    elif args.command == "migrate":
        apply_migrations()
    elif args.command == "routes":
        list_routes()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
