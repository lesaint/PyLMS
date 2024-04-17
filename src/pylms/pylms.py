from pylms import storage
from pylms.core import Person, PersonIdGenerator


def list_persons() -> None:
    persons = storage.read_persons()
    if persons:
        for person in sorted(persons, key=lambda p: p.person_id):
            _print_person(person)
    else:
        print("No Person registered yet.")


def _print_person(person):
    created = person.created
    print(
        f"({person.person_id})",
        person,
        f"({created.year}-{created.month}-{created.day} {created.hour}-{created.minute}-{created.second})",
    )


def _interactive_person_id(valid_ids: list[int]) -> int:
    if not valid_ids:
        raise ValueError("valid_ids can not be empty.")

    while True:
        n = input()
        try:
            res = int(n)
            if res not in valid_ids:
                print("Not a valid id.")
                continue

            return res
        except ValueError:
            print("Not an integer.")


def _interactive_select_person(pattern: str) -> Person | None:
    persons = _search_person(pattern)
    if not persons:
        print("No match.")
        return

    if len(persons) == 1:
        return persons[0]

    print("Input id of person to update:")
    for person in persons:
        _print_person(person)
    print("CTRL+C to exit")

    person_id = _interactive_person_id([person.person_id for person in persons])
    for person in persons:
        if person.person_id == person_id:
            return person

    # should not happen
    raise RuntimeError(f"id {person_id} does not exist in list of Persons")


def _interactive_person_details() -> tuple[str, str | None]:
    while True:
        text = input()

        words = text.split(" ")
        if len(words) > 2:
            print("Too many words.")
            continue

        if len(words) == 1:
            return words[0], None
        return words[0], words[1]


def update_person(pattern: str) -> None:
    person_to_update: Person = _interactive_select_person(pattern)
    if not person_to_update:
        return

    print("Input new first name and last name to update:")
    _print_person(person_to_update)
    print("CTRL+C to exit")

    firstname: str
    lastname: str
    firstname, lastname = _interactive_person_details()

    persons = storage.read_persons()
    for person in persons:
        if person.person_id == person_to_update.person_id:
            person.firstname = firstname
            person.lastname = lastname
    storage.store_persons(persons)


def search_person(pattern: str) -> None:
    for person in _search_person(pattern):
        _print_person(person)


def _search_person(pattern: str) -> list[Person]:
    persons = storage.read_persons()

    res = []
    for person in persons:
        if _search_match(pattern, person):
            res.append(person)

    return res


def _search_match(pattern: str, person: Person) -> bool:
    pattern = pattern.lower()
    if person.lastname:
        return pattern in person.lastname.lower() or pattern in person.firstname.lower()

    return pattern in person.firstname.lower()


def store_person(firstname: str) -> None:
    persons = storage.read_persons()
    id_generator = PersonIdGenerator(persons)
    person = Person(person_id=id_generator.next_person_id(), firstname=firstname)
    print(f"Create Person {person}.")
    storage.store_persons([person] + persons)


def store_person(firstname: str, lastname: str = None) -> None:
    persons = storage.read_persons()
    id_generator = PersonIdGenerator(persons)
    person = Person(person_id=id_generator.next_person_id(), firstname=firstname, lastname=lastname)
    print(f"Create Person {person}.")
    storage.store_persons([person] + persons)
