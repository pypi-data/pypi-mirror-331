"""Normalize command"""

from pathlib import Path
import sqlite3
from typing import Annotated
import typer
from rich import print

from quran_cli import utils


def normalize(
    database: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Database file"),
    ],
) -> None:
    """
    Normalize initial Quran database.

    Examples:

    ```bash
    # Create initial database
    quran-cli init db.sqlite3

    quran-cli normalize db.sqlite3
    ```
    """

    try:
        connection = sqlite3.connect(database)

        utils.apply_normalized_schema(connection)
        utils.insert_chapters(connection)
        utils.insert_verses(connection)
        utils.insert_metadata(connection)
        utils.add_verse_related_fields(connection)
        utils.add_verse_count(connection)
        utils.add_related_fields(connection)
        utils.add_page_count(connection)
        utils.create_views(connection)

        connection.close()

        print("Normalization completed [bold green]successfully[/bold green].")

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
