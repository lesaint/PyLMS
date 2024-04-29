from datetime import datetime
import json
from pathlib import Path
from pylms.core import Person, Relationship, relationship_definitions, Sex, MALE, FEMALE

persons_file_name = "persons.db"
relationships_file_name = "relationships.db"


def _from_sex(sex: Sex | None) -> str | None:
    if sex is None:
        return None
    if sex == MALE:
        return "M"
    if sex == FEMALE:
        return "F"
    raise ValueError(f"Unsupported sex {sex}")


class PersonEncoder(json.JSONEncoder):
    def default(self, o: any) -> any:
        if isinstance(o, Person):
            if o.lastname:
                return {
                    "id": o.person_id,
                    "firstname": o.firstname,
                    "lastname": o.lastname,
                    "created": str(o.created),
                    "sex": _from_sex(o.sex),
                }
            return {
                "id": o.person_id,
                "firstname": o.firstname,
                "created": str(o.created),
                "sex": _from_sex(o.sex),
            }
        # Let the base class default method raise the TypeError
        return super().default(o)


def _to_sex(o: dict) -> Sex | None:
    try:
        sex = o["sex"]
        if sex is None:
            return None
        if sex == "M":
            return MALE
        if sex == "F":
            return FEMALE
        raise ValueError(f"Unsupported value {sex} for sex")
    except KeyError:
        return None


def to_person(o: dict) -> Person:
    if "firstname" not in o:
        raise ValueError(f"Missing field 'firstname' type(o=={type(o)} o={str(o)}")

    sex: Sex = _to_sex(o)
    if "lastname" in o:
        return Person(
            person_id=o["id"],
            firstname=o["firstname"],
            lastname=o["lastname"],
            created=datetime.fromisoformat(o["created"]),
            sex=sex,
        )
    return Person(person_id=o["id"], firstname=o["firstname"], created=datetime.fromisoformat(o["created"]), sex=sex)


def store_persons(persons: list[Person]) -> None:
    if not persons:
        raise ValueError("Can't store an empty list of Persons.")

    with open(persons_file_name, "w") as f:
        f.write(json.dumps(persons, cls=PersonEncoder))


def read_persons() -> list[Person]:
    file = Path(persons_file_name)
    if file.exists():
        with file.open("r") as f:
            content = f.read()
            if content:
                return [to_person(s) for s in json.loads(content)]

    return []


class RelationshipEncoder(json.JSONEncoder):
    def default(self, o: any) -> any:
        if isinstance(o, Relationship):
            return {"left": o.left.person_id, "right": o.right.person_id, "definition": o.definition.name}
        # Let the base class default method raise the TypeError
        return super().default(o)


def _to_relationship(o: dict, persons: list[Person]) -> Relationship | None:
    field_names = ("left", "right", "definition")
    if not all(field_name in o for field_name in field_names):
        raise ValueError(f"Missing at least one field of {field_names}")

    left_id = int(o["left"])
    right_id = int(o["right"])
    definition_name = o["definition"]

    person_index = {person.person_id: person for person in persons}
    if left_id not in person_index or right_id not in person_index:
        print(f"Either person {left_id} or person {right_id} does not exist")
        return None

    definition_index = {definition.name: definition for definition in relationship_definitions}
    if definition_name not in definition_index:
        print(f"definition {definition_name} does not exist")
        return None

    return Relationship(
        person_left=person_index[left_id],
        person_right=person_index[right_id],
        definition=definition_index[definition_name],
    )


def store_relationships(relationships: list[Relationship]) -> None:
    if not relationships:
        raise ValueError("Can't store an empty list of Relationships.")

    with open(relationships_file_name, "w") as f:
        f.write(json.dumps(relationships, cls=RelationshipEncoder))


def read_relationships(persons: list[Person]) -> list[Relationship]:
    if not persons:
        raise ValueError("Persons can't be empty")

    file = Path(relationships_file_name)
    if file.exists():
        with file.open("r") as f:
            content = f.read()
            if content:
                res = [_to_relationship(s, persons) for s in json.loads(content)]
                return list(filter(lambda t: t is not None, res))

    return []


def update_person(person_to_update: Person) -> None:
    persons = read_persons()
    for p in persons[:]:
        if p.person_id == person_to_update.person_id:
            persons.remove(p)
            persons.append(person_to_update)
            store_persons(persons)
            return
    raise ValueError(f"Can't find person with id {person_to_update.person_id}")
