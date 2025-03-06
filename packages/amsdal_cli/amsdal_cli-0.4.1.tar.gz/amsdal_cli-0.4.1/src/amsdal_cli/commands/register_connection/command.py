import asyncio
import tempfile
from pathlib import Path
from typing import Annotated

import typer

from amsdal_cli.app import app
from amsdal_cli.commands.cloud.enums import DBType
from amsdal_cli.commands.generate.enums import SOURCES_DIR
from amsdal_cli.commands.register_connection.utils.config_updater import ConfigUpdater
from amsdal_cli.commands.register_connection.utils.credentials import process_credentials
from amsdal_cli.commands.register_connection.utils.migrate_models import migrate_models_to_lakehouse
from amsdal_cli.commands.register_connection.utils.model_generator import ModelGenerator


@app.command(name='register-connection, reg-conn')
def register_connection_command(
    ctx: typer.Context,
    db_type: DBType,
    credentials: Annotated[
        list[str],
        typer.Option(
            ...,
            '-creds',
            help='Credentials for the connection in the format: prop="value". The `prop=1.0` format is also supported '
            'and will be converted to a float. To get a boolean, use `prop=true` or `prop=false`. To get a Path '
            'use `prop="path/to/file"::path`.',
        ),
    ],
    *,
    connection_name: Annotated[
        str | None,
        typer.Option(help='Name of the connection to be registered. If not provided, it will be generated.'),
    ] = None,
    backend: Annotated[
        str | None,
        typer.Option(
            help="Backend to use for the connection. If it's not provided, it will be resolved from db_type.",
        ),
    ] = None,
    config: Annotated[Path | None, typer.Option(help='Path to custom config.yml file')] = None,
) -> None:
    """
    Registers and adds a new connection to the AMSDAL configuration.

    Args:
        ctx (typer.Context): The Typer context object.
        credentials (list[str]): Credentials for the connection.
        db_type (DBType): The type of database to connect to.
        connection_name (Optional[str]): Name of the connection to be registered. If not provided, it will be generated.
        backend (Optional[str]): Backend to use for the connection. If it's not provided, it will be resolved from
        db_type.
        config (Optional[Path]): Path to custom config.yml file.

    Example of usage:

    1. Register a connection to a SQLite database:
    ```bash
    amsdal reg-conn sqlite -creds db_path='path/to/file/db.sqlite3'::path
    ```
    2. Register a connection to a PostgreSQL database:
    ```bash
    amsdal reg-conn postgres -creds dsn='postgresql://user:password@localhost:5432/mydatabase' -creds schema=public
    ```

    Returns:
        None
    """
    asyncio.run(
        _register_connection_command(
            ctx,
            db_type,
            credentials,
            connection_name=connection_name,
            backend=backend,
            config=config,
        )
    )


async def _register_connection_command(
    ctx: typer.Context,
    db_type: DBType,
    credentials: list[str],
    *,
    connection_name: str | None,
    backend: str | None,
    config: Path | None,
) -> None:
    from amsdal_cli.commands.register_connection.utils.initialize import init_amsdal
    from amsdal_cli.commands.register_connection.utils.tables import fetch_tables
    from amsdal_cli.utils.cli_config import CliConfig

    cli_config: CliConfig = ctx.meta['config']

    _creds = process_credentials(credentials)
    _config = config or cli_config.config_path

    with ConfigUpdater(_config) as updater:
        _connection_name, _ = updater.add_connection(db_type, connection_name, backend, _creds)

    with tempfile.TemporaryDirectory() as _temp_dir:
        temp_dir = Path(_temp_dir)
        await init_amsdal(_config, temp_dir)

        models = await fetch_tables(_connection_name)

    if not models:
        typer.echo('No tables found for the connection.')
        return

    with ConfigUpdater(_config) as updater:
        updater.link_connection_to_models(_connection_name, models)

    generator = ModelGenerator(
        config_path=_config,
        output_dir=cli_config.app_directory / SOURCES_DIR / 'models',
        models_format=cli_config.models_format,
    )

    generator.generate(_connection_name, cli_config=cli_config)

    await migrate_models_to_lakehouse(cli_config, _config)
