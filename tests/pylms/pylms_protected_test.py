from pylms.core import Person
from pylms.pylms import _search_person, _interactive_person_id, _interactive_select_person
from pytest import raises, mark
from unittest.mock import patch, call


@patch("pylms.pylms.storage")
def test_search_person(mock_storage):
    persons = [
        Person(3, "Bob"),
        Person(1, "Seb"),
        Person(2, "MarioEb"),
    ]
    mock_storage.read_persons.return_value = persons

    assert _search_person("bob") == [persons[0]]
    assert _search_person("BOB") == [persons[0]]
    assert _search_person("eb") == [persons[1], persons[2]]
    assert _search_person("bob") == [persons[0]]
    assert _search_person("foo") == []


def test_interactive_person_id_sanity_check():
    with raises(ValueError, match="valid_ids can not be empty."):
        _interactive_person_id([])


@patch("builtins.input")
@mark.parametrize("valid_ids", [[1], [2, 1], [23, 7, 1, 2]])
def test_interactive_person_straight_correct_input(mock_input, valid_ids):
    mock_input.return_value = "1"

    res = _interactive_person_id([2, 1])

    assert res == 1


@patch("builtins.print")
@patch("pylms.pylms._search_person")
def test_interactive_select_person_no_match(mock_search_person, mock_print):
    mock_search_person.return_value = []

    res = _interactive_select_person("p")

    assert res is None
    mock_search_person.assert_called_once_with("p")
    assert mock_search_person.call_count == 1
    mock_print.assert_called_once_with("No match.")
    assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.pylms._search_person")
def test_interactive_select_person_one_match(mock_search_person, mock_print):
    person = Person(123, "John", "Wick")
    mock_search_person.return_value = [person]

    res = _interactive_select_person("p")

    assert res == person
    mock_search_person.assert_called_once_with("p")
    assert mock_search_person.call_count == 1
    assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.pylms._interactive_person_id")
@patch("pylms.pylms._print_person")
@patch("pylms.pylms._search_person")
def test_interactive_select_person_several_matches(
    mock_search_person, mock_print_person, mock_interactive_person_id, mock_print
):
    persons = [
        Person(3, "Bob"),
        Person(1, "Seb"),
    ]
    mock_search_person.return_value = persons
    mock_interactive_person_id.return_value = 3

    res = _interactive_select_person("p")

    assert res == persons[0]
    mock_search_person.assert_called_once_with("p")
    assert mock_search_person.call_count == 1
    assert mock_print.call_count == 2
    mock_print.assert_has_calls([call("Input id of person to update:"), call("CTRL+C to exit")])
    assert mock_print_person.call_count == 2
    mock_print_person.assert_has_calls([call(persons[0]), call(persons[1])])
    assert mock_interactive_person_id.call_count == 1
    mock_interactive_person_id.assert_called_once_with([3, 1])


@patch("builtins.print")
@patch("pylms.pylms._interactive_person_id")
@patch("pylms.pylms._search_person")
def test_interactive_raise_runtime_error_if_interactive_person_id_returns_crap(
    mock_search_person, mock_interactive_person_id, mock_print
):
    persons = [
        Person(3, "Bob"),
        Person(1, "Seb"),
    ]
    mock_search_person.return_value = persons
    mock_interactive_person_id.return_value = 123

    with raises(RuntimeError, match="id 123 does not exist in list of Persons"):
        _interactive_select_person("p")
