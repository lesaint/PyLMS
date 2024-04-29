from pylms.core import Person
from pylms.core import RelationshipDefinition, RelationshipAlias
from pylms.pylms import _search_person, _select_person
from pylms.pylms import _parse_nl_link_request
from pytest import mark
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


class Test_select_person:

    @patch("builtins.print")
    @patch("pylms.pylms._search_person")
    def test_no_match(self, mock_search_person, mock_print):
        mock_search_person.return_value = []

        res = _select_person("p")

        assert res is None
        mock_search_person.assert_called_once_with("p")
        assert mock_search_person.call_count == 1
        assert mock_print.call_count == 0

    @patch("builtins.print")
    @patch("pylms.pylms._search_person")
    def test_one_match(self, mock_search_person, mock_print):
        person = Person(123, "John", "Wick")
        mock_search_person.return_value = [person]

        res = _select_person("p")

        assert res == person
        mock_search_person.assert_called_once_with("p")
        assert mock_search_person.call_count == 1
        assert mock_print.call_count == 0

    @patch("pylms.pylms.ios.select_person")
    @patch("pylms.pylms._search_person")
    def test_several_matches(self, mock_search_person, mock_select_person):
        persons = [
            Person(3, "Bob"),
            Person(1, "Seb"),
        ]
        mock_search_person.return_value = persons
        mock_select_person.return_value = persons[0]

        res = _select_person("p")

        assert res == persons[0]
        mock_search_person.assert_called_once_with("p")
        assert mock_search_person.call_count == 1
        assert mock_select_person.call_count == 1
        mock_select_person.assert_called_once_with(persons)


relationship_definition_1 = RelationshipDefinition(
    name="foo",
    aliases=[
        RelationshipAlias("aaa"),
        RelationshipAlias("bbb"),
        RelationshipAlias("ccc"),
    ],
    person_left_repr="leftFoo",
    person_right_repr="rightFoo",
)
relationship_definition_2 = RelationshipDefinition(
    name="bar",
    aliases=[
        RelationshipAlias("11"),
        RelationshipAlias("22"),
        RelationshipAlias("33"),
    ],
    person_left_repr="leftBar",
)
relationship_definition_3 = RelationshipDefinition(
    name="acme",
    aliases=[
        RelationshipAlias("a2"),
        RelationshipAlias("b3"),
        RelationshipAlias("c4"),
    ],
)


class Test_parse_nl_link_request:

    @patch("pylms.pylms.relationship_definitions", [relationship_definition_1])
    @mark.parametrize(
        "nl_request, alias",
        [
            (s.format(f=alias.name), alias)
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
        [
            (relationship_definition_1.aliases[0], relationship_definition_1),
            (relationship_definition_3.aliases[1], relationship_definition_3),
            (relationship_definition_2.aliases[2], relationship_definition_2),
        ],
    )
    def test_select_the_right_definition_from_alias(self, alias, expected_definition):
        link_request = _parse_nl_link_request(f"Johan {alias.name} Peter")

        assert link_request.alias == alias
        assert link_request.definition == expected_definition

    @patch(
        "pylms.pylms.relationship_definitions",
        [relationship_definition_2, relationship_definition_1, relationship_definition_3],
    )
    @mark.parametrize("nl_request", ["aaa acme", "aaa", " aaa ", "fooaaa", "foo aaa"])
    def test_return_none_if_missing_person_patterns(self, nl_request):
        assert _parse_nl_link_request(nl_request) is None
