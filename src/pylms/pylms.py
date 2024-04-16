from pylms import storage
from pylms.core import Person, PersonIdGenerator


def list_persons() -> None:
    persons = storage.read_persons()
    if persons:
        for person in persons:
            created = person.created
            print(
                f"({person.person_id})",
                person,
                f"({created.year}-{created.month}-{created.day} {created.hour}-{created.minute}-{created.second})",
            )
    else:
        print("No Person registered yet.")


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
