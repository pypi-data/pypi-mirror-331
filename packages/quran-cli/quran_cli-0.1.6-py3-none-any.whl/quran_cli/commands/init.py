"""Init command"""

from pathlib import Path
import sqlite3
from typing import Annotated
import typer
from rich import print

from quran_cli import QuranVariant
from quran_cli.utils import create_database, get_database_name, insert_initial_data


def init(
    database: Annotated[Path, typer.Argument(dir_okay=False, help="Database name")],
    variant: Annotated[
        QuranVariant,
        typer.Option("-v", "--variant", help="Data variant to load."),
    ] = QuranVariant.Uthmani,
) -> None:
    """
    Initialize Quran database.

    Examples:

    ```bash
    # Create initial database
    quran-cli init db.sqlite3

    # Create initial database with uthmani-min variant
    quran-cli init db.sqlite3 -v uthmani-min
    ```
    """

    name = get_database_name(database)

    try:
        connection = sqlite3.connect(name)

        create_database(connection)
        insert_initial_data(connection, variant.value)

        connection.close()

        print("Database created [bold green]successfully[/bold green].")

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
