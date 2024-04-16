from datetime import datetime
from pylms.core import Person
from pylms.pylms import list_persons, store_person
from unittest.mock import patch, call


@patch("builtins.print")
@patch("pylms.pylms.storage.read_persons")
@patch("pylms.pylms.storage.store_persons")
def test_store_person_no_existing_person(mock_store_persons, mock_read_persons, mock_print):
    firstname = "John"
    lastname = "Doe"
    mock_read_persons.return_value = []

    store_person(firstname=firstname, lastname=lastname)

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    mock_store_persons.assert_called_with([Person(0, firstname=firstname, lastname=lastname)])
    assert mock_store_persons.call_count == 1
    mock_print.assert_called_with(f"Create Person {firstname} {lastname}.")
    assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.pylms.storage.read_persons")
@patch("pylms.pylms.storage.store_persons")
def test_store_person_only_firstname_and_add_to_existing_persons(mock_store_persons, mock_read_persons, mock_print):
    firstname = "Mike"
    lastname = "Jagger"
    persons = [Person(7, "Richard", "Brownsome")]

    mock_read_persons.return_value = persons

    store_person(firstname=firstname, lastname=lastname)

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    mock_store_persons.assert_called_with([Person(8, firstname=firstname, lastname=lastname)] + persons)
    assert mock_store_persons.call_count == 1
    mock_print.assert_called_with(f"Create Person {firstname} {lastname}.")
    assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.pylms.storage.read_persons")
@patch("pylms.pylms.storage.store_persons")
def test_store_person_only_firstname_no_existing_person(mock_store_persons, mock_read_persons, mock_print):
    firstname = "John"
    mock_read_persons.return_value = []

    store_person(firstname=firstname)

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    mock_store_persons.assert_called_with([Person(person_id=0, firstname=firstname)])
    assert mock_store_persons.call_count == 1
    mock_print.assert_called_with(f"Create Person {firstname}.")
    assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.pylms.storage.read_persons")
@patch("pylms.pylms.storage.store_persons")
def test_store_person_only_firstname_and_add_to_existing_persons(mock_store_persons, mock_read_persons, mock_print):
    firstname = "John"
    persons = [Person(2, "Paul", "Valérie")]

    mock_read_persons.return_value = persons

    store_person(firstname=firstname)

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    mock_store_persons.assert_called_with([Person(3, firstname=firstname)] + persons)
    assert mock_store_persons.call_count == 1
    mock_print.assert_called_with(f"Create Person {firstname}.")
    assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.pylms.storage.read_persons")
@patch("pylms.pylms.storage.store_persons")
def test_list_persons_empty_storage(mock_store_persons, mock_read_persons, mock_print):
    mock_read_persons.return_value = []

    list_persons()

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    assert mock_store_persons.call_count == 0
    mock_print.assert_called_with("No Person registered yet.")
    assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.pylms.storage.read_persons")
@patch("pylms.pylms.storage.store_persons")
def test_list_persons_non_empty_storage(mock_store_persons, mock_read_persons, mock_print):
    t1 = datetime(2024, 4, 5, 12, 41, 58)
    t2 = datetime(2024, 9, 18, 21, 8, 8)
    persons = [
        Person(1, "Seb", "King", t1),
        Person(2, "Mario", "Bros", t2),
        Person(3, "Bob", created=t1),
    ]

    mock_read_persons.return_value = persons

    list_persons()

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    assert mock_store_persons.call_count == 0
    mock_print.assert_has_calls(
        [
            call("(1)", persons[0], "(2024-4-5 12-41-58)"),
            call("(2)", persons[1], "(2024-9-18 21-8-8)"),
            call("(3)", persons[2], "(2024-4-5 12-41-58)"),
        ]
    )
    assert mock_print.call_count == 3
