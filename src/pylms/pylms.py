from pylms import storage
from pylms.core import Person


def list_persons() -> None:
    persons = storage.read_persons()
    if persons:
        for person in persons:
            print("*", person)
    else:
        print("No Person registered yet.")


def store_person(firstname: str) -> None:
    persons = storage.read_persons()
    person = Person(firstname=firstname)
    print(f"Create Person {person}.")
    storage.store_persons([person] + persons)


def store_person(firstname: str, lastname: str = None) -> None:
    persons = storage.read_persons()
    person = Person(firstname=firstname, lastname=lastname)
    print(f"Create Person {person}.")
    storage.store_persons([person] + persons)
