import json
from pathlib import Path
from pylms.core import Person

file_name = "persons.db"


class PersonEncoder(json.JSONEncoder):
    def default(self, o: any) -> any:
        if isinstance(o, Person):
            if o.lastname:
                return {"firstname": o.firstname, "lastname": o.lastname}
            return {"firstname": o.firstname}
        # Let the base class default method raise the TypeError
        return super().default(o)


def to_Person(o: dict) -> Person:
    if not "firstname" in o:
        raise ValueError(f"Missing field 'firstname' type(o=={type(o)} o={str(o)}")

    if "lastname" in o:
        return Person(firstname=o["firstname"], lastname=o["lastname"])
    return Person(firstname=o["firstname"])


def store_persons(persons: list[Person]) -> None:
    if not persons:
        raise ValueError("Can't store an empty list of Persons.")

    with open(file_name, "w") as f:
        f.write(json.dumps(persons, cls=PersonEncoder))


def read_persons() -> list[Person]:
    file = Path(file_name)
    if file.exists():
        with file.open("r") as f:
            content = f.read()
            if content:
                return [to_Person(s) for s in json.loads(content)]

    return []
