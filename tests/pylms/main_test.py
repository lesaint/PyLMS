from unittest.mock import patch, call
from pylms import __main__
from pytest import fixture
from random import randint

program_name = "pylms"


def random_maj_char():
    return chr(randint(ord("A"), ord("Z")))


# Fixtures
@fixture
def no_arguments():
    return []


@fixture
def one_argument():
    return [random_maj_char()]


@fixture
def two_arguments():
    return [random_maj_char(), random_maj_char()]


@fixture
def more_than_two_arguments():
    return [program_name] + [random_maj_char() for _ in range(1, 3 + randint(0, 5))]


def mock_argv(arguments_list):
    return patch("pylms.__main__.argv", [program_name] + arguments_list)


@patch("builtins.print")
@patch("pylms.__main__.read_persons")
def test_main_no_argument_and_no_persons(mock_read_persons, mock_print, no_arguments):
    mock_read_persons.return_value = []
    with mock_argv(no_arguments):
        __main__.main()
        mock_print.assert_called_with("No Person registered yet.")
        assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.__main__.read_persons")
def test_main_no_argument_and_one_person(mock_read_persons, mock_print, no_arguments):
    mock_read_persons.return_value = [("Sebastien", "Lesaint")]
    with mock_argv(no_arguments):
        __main__.main()
        mock_print.assert_called_with("*", "Sebastien", "Lesaint")
        assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.__main__.read_persons")
def test_main_no_argument_and_person_no_lastname(mock_read_persons, mock_print, no_arguments):
    mock_read_persons.return_value = [("Bob",)]
    with mock_argv(no_arguments):
        __main__.main()
        mock_print.assert_called_with("*", "Bob", None)
        assert mock_print.call_count == 1


@patch("builtins.print")
@patch("pylms.__main__.read_persons")
def test_main_no_argument_and_two_persons(mock_read_persons, mock_print, no_arguments):
    mock_read_persons.return_value = [("Sebastien", "Lesaint"), ("Bernard", "Tapie")]
    with mock_argv(no_arguments):
        __main__.main()
        mock_print.assert_has_calls([call("*", "Sebastien", "Lesaint"), call("*", "Bernard", "Tapie")])
        assert mock_print.call_count == 2


@patch("builtins.print")
def test_main_one_argument(mock_print, one_argument):
    with mock_argv(one_argument):
        __main__.main()
        mock_print.assert_called_with(f"Create Person {one_argument[0]}.")
        assert mock_print.call_count == 1


@patch("builtins.print")
def test_main_two_arguments(mock_print, two_arguments):
    with mock_argv(two_arguments):
        __main__.main()
        mock_print.assert_called_with(f"Create Person {two_arguments[0]} {two_arguments[1]}.")
        assert mock_print.call_count == 1


@patch("builtins.print")
def test_main_three_arguments(mock_print, more_than_two_arguments):
    with mock_argv(more_than_two_arguments):
        __main__.main()
        mock_print.assert_called_with(f"Too many arguments ({len(more_than_two_arguments)})")
        assert mock_print.call_count == 1
