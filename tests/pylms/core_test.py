from pylms.pylms import Person
from pylms.pylms import PersonIdGenerator


def test_eq():
    under_test = Person(person_id=1, firstname="f", lastname="n")

    assert under_test == Person(1, "f", "n")
    assert under_test != Person(2, "f", "n")
    assert under_test != Person(1, "d", "n")
    assert under_test != Person(1, "f", "m")
    assert under_test != Person(1, "f", None)
    assert under_test != (1, "f", "n")


def test_generator_no_person():
    under_test = PersonIdGenerator([])

    assert under_test.next_person_id() == 0


def test_generator_no_person():
    under_test = PersonIdGenerator([Person(2, "n")])

    assert under_test.next_person_id() == 3
