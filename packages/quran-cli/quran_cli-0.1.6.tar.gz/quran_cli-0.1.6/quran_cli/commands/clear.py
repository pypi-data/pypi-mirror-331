"""Clear command"""

from pathlib import Path
import sqlite3
from typing import Annotated
import typer
from rich import print


def clear(
    database: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Database file"),
    ],
) -> None:
    """
    Drops unused tables after normalizing the Quran database.

    Notes:
        In case you wanted to rerun normalize command after running clear command,
        you should rerun the init command then normalize command.

    Examples:

    ```bash
    # Create initial database
    quran-cli init db.sqlite3

    # Normalize the database
    quran-cli normalize db.sqlite3

    quran-cli clear db.sqlite3
    ```
    """

    try:
        connection = sqlite3.connect(database)
        connection.cursor().execute('DROP TABLE IF EXISTS "quran";')
        connection.close()

        print("Database cleared [bold green]successfully[/bold green].")

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
