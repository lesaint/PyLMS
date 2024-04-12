from unittest.mock import patch
from pylms import __main__
from pytest import fixture
from random import randint

program_name = "pylms"


def random_maj_char():
    return chr(randint(ord("A"), ord("Z")))


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


@patch("builtins.print")
def test_main_no_argument(mock_print, no_arguments):
    with patch("pylms.__main__.argv", [program_name] + no_arguments):
        __main__.main()
        mock_print.assert_called_with("Requires at least one argument")


@patch("builtins.print")
def test_main_one_argument(mock_print, one_argument):
    with patch("pylms.__main__.argv", [program_name] + one_argument):
        __main__.main()
        mock_print.assert_called_with(f"Create Person {one_argument[0]}.")


@patch("builtins.print")
def test_main_two_arguments(mock_print, two_arguments):
    with patch("pylms.__main__.argv", [program_name] + two_arguments):
        __main__.main()
        mock_print.assert_called_with(f"Create Person {two_arguments[0]} {two_arguments[1]}.")


@patch("builtins.print")
def test_main_three_arguments(mock_print, more_than_two_arguments):
    with patch("pylms.__main__.argv", [program_name] + more_than_two_arguments):
        __main__.main()
        mock_print.assert_called_with(f"Too many arguments ({len(more_than_two_arguments)})")
