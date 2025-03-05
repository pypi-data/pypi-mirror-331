import argparse
import json
import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Runs the tailwind compiler"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.input_filepath = (
            "./crimsonslate_portfolio/static/crimsonslate_portfolio/css/input.css"
        )
        self.output_filepath = (
            "./crimsonslate_portfolio/static/crimsonslate_portfolio/css/output.css"
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Adds subcommand arguments to the ``tailwind`` command.

        +-------------+-------------------------------------------------------------------+
        | Subcommand  | Action                                                            |
        +=============+===================================================================+
        | ``install`` | Installs the tailwind compiler for the project.                   |
        +-------------+-------------------------------------------------------------------+
        | ``start``   | Starts the tailwind compiler. Must be canceled with ``<CTRL>-c``. |
        +-------------+-------------------------------------------------------------------+
        | ``build``   | Builds the tailwind output file for production.                   |
        +-------------+-------------------------------------------------------------------+

        :param parser: An argument parser.
        :type parser: :py:obj:`argparse.ArgumentParser`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        subparsers = parser.add_subparsers(dest="subcommand")
        subparsers.add_parser("install", help="Install tailwind compiler")
        subparsers.add_parser("start", help="Start tailwind compiler")
        subparsers.add_parser("build", help="Compile tailwind for production")

    def handle(self, *args, **options):
        """
        Handles command execution based on the provided subcommand.

        :raises CommandError: If the subcommand is invalid.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        subcommand = options["subcommand"]
        try:
            command = self.generate_command(subcommand)
            os.system(command)
        except ValueError as e:
            raise CommandError(e)

    def generate_command(self, subcommand: str | None) -> str:
        """
        Generates a tailwind command based on the provided subcommand.

        :returns: A command to be executed by :py:func:`os.system`.
        :rtype: :py:obj:`str`

        """
        command = (
            f"npx @tailwindcss/cli -i {self.input_filepath} -o {self.output_filepath} "
        )
        match subcommand:
            case "start":
                styled = self.style.NOTICE
                message = "Starting tailwind compiler..."
                command += "--watch"
            case "build":
                styled = self.style.NOTICE
                message = "Compiling tailwind for production..."
                command += "--minify"
            case "install":
                if self.node_package_installed("tailwind"):
                    styled = self.style.WARNING
                    message = "Tailwind is already installed, building for production instead..."
                    command += "--minify"
                else:
                    styled = self.style.NOTICE
                    message = "Installing tailwind..."
                    command = "npm install -D tailwindcss @tailwindcss/cli"
            case _:
                raise ValueError(f"Invalid subcommand: '{subcommand}'.")

        self.stdout.write(styled(message))
        return command

    def get_node_dependencies(self) -> list[str]:
        """
        Retrives a list of npm dependencies from ``package.json``.

        Returns an empty list if ``package.json`` does not exist.

        :returns: A list of application dependencies as strings.
        :rtype: :py:obj:`list`

        """
        dependencies: list[str] = []
        if not os.path.isfile("package.json"):
            return dependencies

        with open("package.json", "r") as file:
            dependencies.extend(json.load(file).get("devDependencies", {}).keys())
        return dependencies

    def node_package_installed(self, name: str) -> bool:
        """
        Whether or not a node package is installed.

        :type: :py:obj:`bool`

        """
        return name in self.get_node_dependencies()
