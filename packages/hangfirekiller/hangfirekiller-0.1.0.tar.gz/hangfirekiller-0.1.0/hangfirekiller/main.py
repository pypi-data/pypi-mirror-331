import json
import re
from pathlib import Path

import typer
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.engine import URL

from hangfirekiller.models import ApplicationSettings, DBConnectionSettings

app = typer.Typer()


@app.command(name='kill')
def kill_hangfire(path: str):
    settings = get_settings_file(path)
    connection_string = read_connection_string(settings)
    connection_settings = parse_connection_string(connection_string)
    engine = make_engine(connection_settings)
    drop_hangfire(engine)


def get_settings_file(directory: str) -> Path:
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ValueError(f"Указанная директория не существует: {directory}")

    lookup_files = ('appsettings.Development.json', 'appsettings.json')

    files = (find_file_in_dir(dir_path, name) for name in lookup_files)

    for file in files:
        if file.exists():
            return file

    raise LookupError(f"Файл с настройками не найден")


def find_file_in_dir(dir_path: Path, name: str) -> Path | None:
    file = dir_path / name
    if file.is_file():
        return file


def read_connection_string(file: Path) -> str:
    with open(file, 'r') as f:
        data = json.load(f)

    application_settings = ApplicationSettings(**data)

    return application_settings.connection_settings.connection_string


def parse_connection_string(conn_str: str) -> DBConnectionSettings:
    pattern = re.compile(
        r"(Host)=(?P<Host>.*?);|"
        r"(Port)=(?P<Port>\d+);|"
        r"(Database)=(?P<Database>.*?);|"
        r"(Username)=(?P<Username>.*?);|"
        r"(Password)=(?P<Password>.*?);"
    )

    matches = pattern.finditer(conn_str)

    extracted = {}
    for match in matches:
        for key in ['Host', 'Port', 'Database', 'Username', 'Password']:
            if match.group(key):
                extracted[key] = match.group(key)

    return DBConnectionSettings(**extracted)


def make_engine(conn_settings: DBConnectionSettings) -> Engine:
    url_object = URL.create(
        'postgresql+psycopg2',
        **conn_settings.model_dump()
    )

    return create_engine(url_object)


def drop_hangfire(engine: Engine):
    drop_query = text('DROP SCHEMA IF EXISTS hangfire CASCADE;')
    with engine.connect() as conn:
        conn.execute(drop_query)
        conn.commit()


if __name__ == '__main__':
    kill_hangfire("/home/alex/Documents/RiderProjects/Sport74/minsport/WebUI/")
