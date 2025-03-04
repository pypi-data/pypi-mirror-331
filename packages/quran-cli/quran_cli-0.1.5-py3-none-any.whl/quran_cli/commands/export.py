"""JSON Export command"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Annotated
import typer
from rich import print


def export(
    database: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Database name"),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "-o",
            "--output",
            file_okay=False,
            dir_okay=True,
            help="Output folder",
        ),
    ] = Path("quran"),
) -> None:
    """
    Export Quran data to json.

    Examples:

    ```bash
    # Create initial database
    quran-cli init db.sqlite3

    # Normalize initial database
    quran-cli normalize db.sqlite3

    # Export normalized database
    quran-cli export db.sqlite3
    quran-cli export db.sqlite3 -o data
    ```
    """

    try:
        connection = sqlite3.connect(database.name)
        os.makedirs(output.name, exist_ok=True)

        tables = {
            "chapters": {
                0: "id",
                1: "name",
                2: "order",
                3: "type",
                4: "verse_count",
                5: "page_count",
            },
            "parts": {0: "id", 1: "name", 2: "verse_count", 3: "page_count"},
            "groups": {
                0: "id",
                1: "name",
                2: "verse_count",
                3: "page_count",
                4: "part_id",
            },
            "quarters": {
                0: "id",
                1: "name",
                2: "verse_count",
                3: "page_count",
                4: "group_id",
                5: "part_id",
            },
            "pages": {
                0: "id",
                1: "name",
                2: "verse_count",
                3: "chapter_id",
                4: "group_id",
                5: "part_id",
                6: "quarter_id",
            },
            "verses": {
                0: "id",
                1: "number",
                2: "content",
                3: "chapter_id",
                4: "group_id",
                5: "page_id",
                6: "part_id",
                7: "quarter_id",
            },
        }

        for name, fields in tables.items():
            print(f"Exporting [bold]{name}[/bold] table...", end=" ")

            with open(
                f"{os.path.join(output.name, name)}.json",
                mode="w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    [
                        {fields[k]: v for k, v in list(enumerate(row))}
                        for row in connection.cursor()
                        .execute(f'SELECT * FROM "{name}"')
                        .fetchall()
                    ],
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            print("[bold green]Done[/bold green]")

        connection.close()

        print("Export completed [bold green]successfully[/bold green].")

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
