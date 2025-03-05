import argparse

from onbbu.cli.cli_run_server import run_server
from onbbu.cli.cli_list_routes import list_routes
from onbbu.settings import server

def main():

    parser = argparse.ArgumentParser(description="CLI para manejar Onbbu")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Iniciar el servidor")

    subparsers.add_parser("makemigrations", help="Generar una nueva migración")

    subparsers.add_parser("migrate", help="Aplicar migraciones")

    subparsers.add_parser("routes", help="Listar rutas de")

    args = parser.parse_args()

    if args.command == "run":
        run_server(server=server)
    elif args.command == "routes":
        list_routes()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
