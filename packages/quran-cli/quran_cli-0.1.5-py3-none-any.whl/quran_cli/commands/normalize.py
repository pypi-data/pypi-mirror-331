"""Normalize command"""

from pathlib import Path
from typing import Annotated
import typer
from rich import print

from quran_cli.utils import (
    add_page_count,
    apply_normalized_schema,
    create_views,
    insert_chapters,
    insert_metadata,
    insert_verses,
    add_verse_related_fields,
    add_related_fields,
    add_verse_count,
)


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

    db_name = (
        database.name
        if database.name.endswith((".sqlite3", ".db"))
        else database.name + ".sqlite3"
    )

    try:
        apply_normalized_schema(db_name)
        insert_chapters(db_name)
        insert_verses(db_name)
        insert_metadata(db_name)
        add_verse_related_fields(db_name)
        add_verse_count(db_name)
        add_related_fields(db_name)
        add_page_count(db_name)
        create_views(db_name)

        print("Normalization completed [bold green]successfully[/bold green].")

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
