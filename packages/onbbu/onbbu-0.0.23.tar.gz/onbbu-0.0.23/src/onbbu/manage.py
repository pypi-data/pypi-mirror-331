import argparse
import importlib
import pkgutil

from onbbu.commands import BaseCommand, CommandMigrate, CommandRunServer
from onbbu.settings import COMMANDS, installed_apps


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
