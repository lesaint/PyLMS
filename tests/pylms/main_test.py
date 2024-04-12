from unittest.mock import patch
from pylms import __main__


@patch("builtins.print")
def test_main_no_argument(mock_print):
    __main__.main()

    mock_print.assert_called_with("Requires at least one argument")


@patch("builtins.print")
@patch("pylms.__main__.argv", ["pylms", "A"])
def test_main_one_argument(mock_print):
    __main__.main()

    mock_print.assert_called_with("Create Person A.")


@patch("builtins.print")
@patch("pylms.__main__.argv", ["pylms", "A", "B"])
def test_main_two_arguments(mock_print):
    __main__.main()

    mock_print.assert_called_with("Create Person A B.")


@patch("builtins.print")
@patch("pylms.__main__.argv", ["pylms", "A", "B", "C"])
def test_main_three_arguments(mock_print):
    __main__.main()

    mock_print.assert_called_with("Too many arguments (3)")
