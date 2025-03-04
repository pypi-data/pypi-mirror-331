"""Init command"""

from pathlib import Path
from typing import Annotated
import typer
from rich import print

from quran_cli import QuranVariant
from quran_cli.utils import create_database, insert_initial_data


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

    # Create initial database with Uthmani variant
    quran-cli init db.sqlite3 -v uthmani
    ```
    """

    db_name = (
        database.name.split(".")[0] + f'{variant.value}.{database.name.split(".")[-1]}'
        if database.name.endswith((".sqlite3", ".db"))
        else database.name + f"-{variant.value}.sqlite3"
    )

    try:
        create_database(db_name)
        insert_initial_data(db_name, variant.value)

        print("Database created [bold green]successfully[/bold green].")

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
