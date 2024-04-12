import json
from pathlib import Path

file_name = "persons.db"


def store_persons(persons: list[tuple[str, str]]) -> None:
    if not persons:
        raise ValueError("Can't store an empty list of Persons.")

    with open(file_name, "w") as f:
        f.write(json.dumps(persons))


def read_persons() -> list[tuple[str, str]]:
    file = Path(file_name)
    if file.exists():
        with file.open("r") as f:
            content = f.read()
            if content:
                return json.loads(content)
            return []
