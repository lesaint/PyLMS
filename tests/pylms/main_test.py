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
@patch("pylms.__main__.store_person")
@patch("pylms.__main__.list_persons")
def test_main_no_argument(mock_list_persons, mock_store_person, mock_print, no_arguments):
    with mock_argv(no_arguments):
        __main__.main()

        mock_list_persons.assert_called_with()
        assert mock_list_persons.call_count == 1
        assert mock_store_person.call_count == 0
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.store_person")
@patch("pylms.__main__.list_persons")
def test_main_one_argument(mock_list_persons, mock_store_person, mock_print, one_argument):
    with mock_argv(one_argument):
        __main__.main()

        mock_store_person.assert_called_with(firstname=one_argument[0])
        assert mock_store_person.call_count == 1
        assert mock_list_persons.call_count == 0
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.store_person")
@patch("pylms.__main__.list_persons")
def test_main_two_arguments(mock_list_persons, mock_store_person, mock_print, two_arguments):
    with mock_argv(two_arguments):
        __main__.main()

        mock_store_person.assert_called_with(firstname=two_arguments[0], lastname=two_arguments[1])
        assert mock_store_person.call_count == 1
        assert mock_list_persons.call_count == 0
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.store_person")
@patch("pylms.__main__.list_persons")
def test_main_three_arguments(mock_list_persons, mock_store_person, mock_print, more_than_two_arguments):
    with mock_argv(more_than_two_arguments):
        __main__.main()

        mock_print.assert_called_with(f"Too many arguments ({len(more_than_two_arguments)})")
        assert mock_store_person.call_count == 0
        assert mock_list_persons.call_count == 0
        assert mock_print.call_count == 1
