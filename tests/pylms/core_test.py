from datetime import datetime
from pylms.pylms import Person
from pylms.pylms import PersonIdGenerator
from unittest.mock import patch


@patch("pylms.core.datetime.datetime")
def test_created_not_provided_in_constructor(mock_datetime):
    expected = datetime(2024, 4, 16, 2, 2, 2)
    mock_datetime.now.return_value = expected

    under_test = Person(person_id=1, firstname="f", lastname="n")

    assert under_test.created == expected


def test_created_provided_in_constructor():
    expected = datetime(2024, 4, 16, 2, 2, 2)
    other = datetime(2024, 4, 16, 10, 10, 10)

    with patch("pylms.core.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = other
        under_test = Person(person_id=1, firstname="f", lastname="n", created=expected)

    assert under_test.created == expected


def test_eq():
    under_test = Person(person_id=1, firstname="f", lastname="n")

    assert under_test == Person(1, "f", "n")
    assert under_test != Person(2, "f", "n")
    assert under_test != Person(1, "d", "n")
    assert under_test != Person(1, "f", "m")
    assert under_test != Person(1, "f", None)
    assert under_test != (1, "f", "n")


def test_created_not_in_eq():
    t1 = datetime(2023, 4, 16, 11, 52, 56)
    t2 = datetime(2023, 4, 16, 11, 53, 15)

    assert Person(person_id=1, firstname="f", lastname="n", created=t1) == Person(
        person_id=1, firstname="f", lastname="n", created=t2
    )


def test_generator_no_person():
    under_test = PersonIdGenerator([])

    assert under_test.next_person_id() == 0


def test_generator_one_person():
    under_test = PersonIdGenerator([Person(2, "n")])

    assert under_test.next_person_id() == 3
