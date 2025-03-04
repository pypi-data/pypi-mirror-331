"""SQL Explore command"""

from pathlib import Path
import sqlite3
from typing import Annotated
import typer
from rich import box, print
from rich.table import Table


def explore(
    database: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Database name"),
    ],
) -> None:
    """
    Explore the Quran database with SQL.

    Examples:

    ```bash
    # Create initial database
    quran-cli init db.sqlite3

    quran-cli explore db.sqlite3
    ```
    """

    db_name = (
        database.name
        if database.name.endswith((".sqlite3", ".db"))
        else database.name + ".sqlite3"
    )

    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        print(
            "[bold]QuranCLI Shell[/bold]\n"
            "Type [bold red]exit[/bold red] or [bold red]quit[/bold red] to exit.\n"
        )

        while True:
            query = typer.prompt("sqlite", prompt_suffix=" >>> ")

            if query.lower() in ("exit", "quit"):
                break

            try:
                results = cursor.execute(query).fetchall()

                if len(results) >= 1:
                    table = Table(
                        title="Query Results",
                        title_justify="left",
                        title_style="bold",
                        box=box.ROUNDED,
                        highlight=True,
                        show_lines=True,
                    )

                    for column in cursor.description:
                        table.add_column(column[0])

                    for row in results:
                        table.add_row(*[str(item) for item in row])

                    print(table)

                else:
                    print("Query executed [bold green]successfully[/bold green].")

            except Exception as error:
                print(f"[bold red]Error[/bold red]: {error}")

                continue

    except Exception as error:
        print(f"[bold red]Error[/bold red]: {error}")
