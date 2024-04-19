from pylms.core import Person
from pylms.core import RelationshipDefinition
from pylms.pylms import _search_person, _interactive_person_id, _interactive_select_person, _interactive_hit_enter
from pylms.pylms import _parse_nl_link_request
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


class Test_interactive_person_id:

    def test_sanity_check(self):
        with raises(ValueError, match="valid_ids can not be empty."):
            _interactive_person_id([])

    @patch("builtins.input")
    @mark.parametrize("valid_ids", [[1], [2, 1], [23, 7, 1, 2]])
    def test_straight_correct_input(self, mock_input, valid_ids):
        mock_input.return_value = "1"

        res = _interactive_person_id([2, 1])

        assert res == 1


class Test_interactive_select_person:

    @patch("builtins.print")
    @patch("pylms.pylms._search_person")
    def test_no_match(self, mock_search_person, mock_print):
        mock_search_person.return_value = []

        res = _interactive_select_person("p")

        assert res is None
        mock_search_person.assert_called_once_with("p")
        assert mock_search_person.call_count == 1
        mock_print.assert_called_once_with("No match.")
        assert mock_print.call_count == 1

    @patch("builtins.print")
    @patch("pylms.pylms._search_person")
    def test_one_match(self, mock_search_person, mock_print):
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
    def test_several_matches(self, mock_search_person, mock_print_person, mock_interactive_person_id, mock_print):
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
        mock_print_person.assert_has_calls([call(persons[1]), call(persons[0])])
        assert mock_interactive_person_id.call_count == 1
        mock_interactive_person_id.assert_called_once_with([3, 1])

    @patch("builtins.print")
    @patch("pylms.pylms._interactive_person_id")
    @patch("pylms.pylms._search_person")
    def test_interactive_raise_runtime_error_if_interactive_person_id_returns_crap(
        self, mock_search_person, mock_interactive_person_id, mock_print
    ):
        persons = [
            Person(3, "Bob"),
            Person(1, "Seb"),
        ]
        mock_search_person.return_value = persons
        mock_interactive_person_id.return_value = 123

        with raises(RuntimeError, match="id 123 does not exist in list of Persons"):
            _interactive_select_person("p")


class Test_interactive_hit_enter:

    @patch("builtins.input")
    def test_interactive_hit_enter_straight_correct_input(self, mock_input):
        mock_input.return_value = ""

        _interactive_hit_enter()

        mock_input.assert_called_once_with()
        assert mock_input.call_count == 1

    @patch("builtins.input")
    def test_interactive_hit_enter_incorrect_inputs(self, mock_input):
        mock_input.side_effect = ["q", "12", "ENTER", ""]

        _interactive_hit_enter()

        mock_input.assert_has_calls([call(), call(), call(), call()])
        assert mock_input.call_count == 4


relationship_definition_1 = RelationshipDefinition(name="foo", aliases=["aaa", "bbb", "ccc"])
relationship_definition_2 = RelationshipDefinition(name="bar", aliases=["11", "22", "33"])
relationship_definition_3 = RelationshipDefinition(name="acme", aliases=["a2", "b3", "c4"])


class Test_parse_nl_link_request:

    @patch("pylms.pylms.relationship_definitions", [relationship_definition_1])
    @mark.parametrize(
        "nl_request, alias",
        [
            (s.format(f=alias), alias)
            for s in ["donut {f} acme", "donut{f}acme", " donut {f} acme"]
            for alias in relationship_definition_1.aliases
        ],
    )
    def test_parse_the_right_alias_and_strip_person_patterns(self, nl_request, alias):
        link_request = _parse_nl_link_request(nl_request)

        assert link_request.left_person_pattern == "donut"
        assert link_request.right_person_pattern == "acme"
        assert link_request.definition == relationship_definition_1
        assert link_request.alias == alias

    @patch(
        "pylms.pylms.relationship_definitions",
        [relationship_definition_2, relationship_definition_1, relationship_definition_3],
    )
    @mark.parametrize(
        "alias, expected_definition",
        [("aaa", relationship_definition_1), ("c4", relationship_definition_3), ("33", relationship_definition_2)],
    )
    def test_select_the_right_definition_from_alias(self, alias, expected_definition):
        link_request = _parse_nl_link_request(f"Johan {alias} Peter")

        assert link_request.alias == alias
        assert link_request.definition == expected_definition

    @patch(
        "pylms.pylms.relationship_definitions",
        [relationship_definition_2, relationship_definition_1, relationship_definition_3],
    )
    @mark.parametrize("nl_request", ["aaa acme", "aaa", " aaa ", "fooaaa", "foo aaa"])
    def test_return_none_if_missing_person_patterns(self, nl_request):
        assert _parse_nl_link_request(nl_request) is None
