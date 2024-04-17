from datetime import datetime
from pylms.core import Person
from pylms.pylms import list_persons, store_person, search_person, update_person
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
        Person(3, "Bob", created=t1),
        Person(1, "Seb", "King", t1),
        Person(2, "Mario", "Bros", t2),
    ]

    mock_read_persons.return_value = persons

    list_persons()

    mock_read_persons.assert_called_with()
    assert mock_read_persons.call_count == 1
    assert mock_store_persons.call_count == 0
    mock_print.assert_has_calls(
        [
            call("(1)", persons[1], "(2024-4-5 12-41-58)"),
            call("(2)", persons[2], "(2024-9-18 21-8-8)"),
            call("(3)", persons[0], "(2024-4-5 12-41-58)"),
        ]
    )
    assert mock_print.call_count == 3


@patch("builtins.print")
@patch("pylms.pylms._search_person")
def test_search_person_no_result(mock_search_person, mock_print):
    mock_search_person.return_value = []

    search_person("p")

    mock_search_person.assert_called_once_with("p")
    assert mock_print.call_count == 0


@patch("pylms.pylms._print_person")
@patch("pylms.pylms._search_person")
def test_search_person_results(mock_search_person, mock_print_persons):
    persons = [
        Person(3, "Bob"),
        Person(1, "Seb"),
        Person(2, "MarioEb"),
    ]
    mock_search_person.return_value = persons

    search_person("p")

    mock_search_person.assert_called_once_with("p")
    assert mock_print_persons.call_count == 3
    mock_print_persons.assert_has_calls([call(person) for person in persons])


@patch("pylms.pylms.storage")
@patch("pylms.pylms._interactive_select_person")
def test_update_no_person_selected(mock_select, mock_storage):
    mock_select.return_value = None

    update_person("p")

    mock_select.assert_called_once_with("p")
    assert mock_storage.store_persons.call_count == 0


@patch("pylms.pylms.storage")
@patch("pylms.pylms._interactive_person_details")
@patch("pylms.pylms._interactive_select_person")
def test_update_single_person(mock_select, mock_person_details, mock_storage):
    person = Person(1, "foo", "bar")
    mock_select.return_value = person
    mock_person_details.return_value = ("donut", "acme")
    mock_storage.read_persons.return_value = [person]

    update_person("p")

    mock_select.assert_called_once_with("p")
    assert mock_storage.read_persons.call_count == 1
    assert mock_storage.store_persons.call_count == 1
    mock_storage.store_persons.assert_called_once_with([Person(1, "donut", "acme")])


@patch("pylms.pylms.storage")
@patch("pylms.pylms._interactive_person_details")
@patch("pylms.pylms._interactive_select_person")
def test_update_person_out_of_several(mock_select, mock_person_details, mock_storage):
    person1 = Person(1, "foo", "bar")
    person2 = Person(2, "foo", "bar")
    person3 = Person(3, "foo", "bar")
    mock_select.return_value = person2
    mock_person_details.return_value = ("donut", "acme")
    mock_storage.read_persons.return_value = [person3, person1, person2]

    update_person("p")

    mock_select.assert_called_once_with("p")
    assert mock_storage.read_persons.call_count == 1
    assert mock_storage.store_persons.call_count == 1
    mock_storage.store_persons.assert_called_once_with([person3, person1, Person(2, "donut", "acme")])
