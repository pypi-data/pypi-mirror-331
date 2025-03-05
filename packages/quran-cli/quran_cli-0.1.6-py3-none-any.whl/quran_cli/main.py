"""Quran CLI"""

import typer
from quran_cli.commands import command_list


# CLI
app = typer.Typer(
    name="quran-cli",
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="Quran CLI, A tool to generate the most sophisticated Quran data.",
)

for command in command_list:
    app.command(no_args_is_help=True)(command)


if __name__ == "__main__":
    app()
