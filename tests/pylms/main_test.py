from unittest.mock import patch, call
from pylms import __main__
from pytest import fixture
from random import randint
from typing import ContextManager

COMMAND_CREATE = "create"
COMMAND_UPDATE = "update"
COMMAND_DELETE = "delete"
COMMAND_LINK = "link"


program_name = "pylms"


def random_maj_char() -> chr:
    return chr(randint(ord("A"), ord("Z")))


# Fixtures
@fixture
def no_arguments() -> list[str]:
    return []


@fixture
def one_argument() -> list[str]:
    return [random_maj_char()]


@fixture
def two_arguments() -> list[str]:
    return [random_maj_char(), random_maj_char()]


@fixture
def more_than_one_argument() -> list[str]:
    return [random_maj_char() for _ in range(0, 2 + randint(0, 5))]


@fixture
def more_than_two_arguments() -> list[str]:
    return [random_maj_char() for _ in range(0, 3 + randint(0, 5))]


def mock_argv(arguments_list: list[str]) -> ContextManager[any]:
    return patch("pylms.__main__.argv", [program_name] + arguments_list)


@patch("builtins.print")
@patch("pylms.__main__.list_persons")
def test_main_no_argument(mock_list_persons, mock_print, no_arguments):
    with mock_argv(no_arguments):
        __main__.main()

        mock_list_persons.assert_called_once_with()
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.search_persons")
def test_main_one_argument(mock_search_person, mock_print, one_argument):
    with mock_argv(one_argument):
        __main__.main()

        mock_search_person.assert_called_once_with(one_argument[0])
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.search_persons")
def test_main_two_arguments(mock_search_person, mock_print, two_arguments):
    with mock_argv(two_arguments):
        __main__.main()

        mock_search_person.assert_called_once_with(two_arguments[0] + " " + two_arguments[1])
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.search_persons")
def test_main_three_arguments(mock_search_person, mock_print, more_than_two_arguments):
    with mock_argv(more_than_two_arguments):
        __main__.main()

        mock_search_person.assert_called_once_with(" ".join(more_than_two_arguments))
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.store_person")
def test_create_no_argument(mock_store_person, mock_print, no_arguments):
    with mock_argv([COMMAND_CREATE] + no_arguments):
        __main__.main()

        assert mock_store_person.call_count == 0
        mock_print.assert_called_once_with("Too few arguments (0)")


@patch("builtins.print")
@patch("pylms.__main__.store_person")
def test_create_one_argument(mock_store_person, mock_print, one_argument):
    with mock_argv([COMMAND_CREATE] + one_argument):
        __main__.main()

        mock_store_person.assert_called_once_with(firstname=one_argument[0])
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.store_person")
def test_create_two_arguments(mock_store_person, mock_print, two_arguments):
    with mock_argv([COMMAND_CREATE] + two_arguments):
        __main__.main()

        mock_store_person.assert_called_once_with(firstname=two_arguments[0], lastname=two_arguments[1])
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.store_person")
def test_create_more_than_two_arguments(mock_store_person, mock_print, more_than_two_arguments):
    with mock_argv([COMMAND_CREATE] + more_than_two_arguments):
        __main__.main()

        assert mock_store_person.call_count == 0
        mock_print.assert_called_once_with(f"Too many arguments ({len(more_than_two_arguments)})")


@patch("builtins.print")
@patch("pylms.__main__.update_person")
def test_update_no_argument(mock_update_person, mock_print, no_arguments):
    with mock_argv([COMMAND_UPDATE] + no_arguments):
        __main__.main()

        assert mock_update_person.call_count == 0
        mock_print.assert_called_once_with("Missing search pattern")


@patch("builtins.print")
@patch("pylms.__main__.update_person")
def test_update_one_argument(mock_update_person, mock_print, one_argument):
    with mock_argv([COMMAND_UPDATE] + one_argument):
        __main__.main()

        mock_update_person.assert_called_once_with(pattern=one_argument[0])
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.update_person")
def test_update_more_than_one_argument(mock_update_person, mock_print, more_than_one_argument):
    with mock_argv([COMMAND_UPDATE] + more_than_one_argument):
        __main__.main()

        assert mock_update_person.call_count == 0
        mock_print.assert_called_once_with(f"Too many arguments ({len(more_than_one_argument)})")


@patch("builtins.print")
@patch("pylms.__main__.delete_person")
def test_delete_no_argument(mock_delete_person, mock_print, no_arguments):
    with mock_argv([COMMAND_DELETE] + no_arguments):
        __main__.main()

        assert mock_delete_person.call_count == 0
        mock_print.assert_called_once_with("Missing search pattern")


@patch("builtins.print")
@patch("pylms.__main__.delete_person")
def test_delete_one_argument(mock_delete_person, mock_print, one_argument):
    with mock_argv([COMMAND_DELETE] + one_argument):
        __main__.main()

        mock_delete_person.assert_called_once_with(pattern=one_argument[0])
        assert mock_print.call_count == 0


@patch("builtins.print")
@patch("pylms.__main__.delete_person")
def test_delete_more_than_one_argument(mock_delete_person, mock_print, more_than_one_argument):
    with mock_argv([COMMAND_DELETE] + more_than_one_argument):
        __main__.main()

        assert mock_delete_person.call_count == 0
        mock_print.assert_called_once_with(f"Too many arguments ({len(more_than_one_argument)})")


@patch("builtins.print")
@patch("pylms.__main__.link_persons")
def test_link_no_argument(mock_link_persons, mock_print, no_arguments):
    with mock_argv([COMMAND_LINK] + no_arguments):
        __main__.main()

        assert mock_link_persons.call_count == 0
        mock_print.assert_called_once_with("Too few arguments (0)")


@patch("builtins.print")
@patch("pylms.__main__.link_persons")
def test_link_one_argument(mock_link_persons, mock_print, one_argument):
    with mock_argv([COMMAND_LINK] + one_argument):
        __main__.main()

        assert mock_link_persons.call_count == 0
        mock_print.assert_called_once_with("Too few arguments (1)")


@patch("builtins.print")
@patch("pylms.__main__.link_persons")
def test_link_two_arguments(mock_link_persons, mock_print, two_arguments):
    with mock_argv([COMMAND_LINK] + two_arguments):
        __main__.main()

        mock_link_persons.assert_called_once_with(two_arguments[0] + " " + two_arguments[1])
        assert mock_print.call_count == 0
