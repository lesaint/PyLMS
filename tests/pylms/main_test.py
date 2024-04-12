from unittest.mock import patch
from pylms import __main__


@patch("builtins.print")
def test_main(mock_print):
    __main__.main()

    mock_print.assert_called_with("Hello world!")
