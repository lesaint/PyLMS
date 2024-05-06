from pylms.cli import CLI
from pylms.pylms import Person, RelationshipDefinition, Relationship
from pytest import raises, mark
from unittest.mock import patch, call

CTRL_C_TO_EXIT = "CTRL+C to exit"

under_test = CLI()


class TestListPersons:

    @patch("builtins.print")
    def test_no_persons(self, mock_print):
        under_test.list_persons([])

        mock_print.assert_called_with("No Person registered yet.")
        assert mock_print.call_count == 1

    @patch("builtins.print")
    @patch.object(under_test, "show_person")
    def test_one_person_no_relationship(self, mock_show_person, mock_print):
        person = Person(3, "John", "Doe")

        under_test.list_persons([(person, [])])

        assert mock_show_person.call_count == 1
        mock_show_person.assert_called_once_with(person)
        assert mock_print.call_count == 0

    @patch("builtins.print")
    @patch.object(under_test, "show_person")
    def test_persons_no_relationship(self, mock_show_person, mock_print):
        persons = [
            Person(3, "Bob"),
            Person(1, "Seb", "King"),
            Person(2, "Mario", "Bros"),
        ]

        under_test.list_persons([(person, []) for person in persons])

        assert mock_show_person.call_count == 3
        mock_show_person.assert_has_calls(
            [
                call(persons[1]),
                call(persons[2]),
                call(persons[0]),
            ]
        )
        assert mock_print.call_count == 0


class TestInteractivePersonId:

    def test_sanity_check(self):
        with raises(ValueError, match="valid_ids can not be empty."):
            under_test._interactive_person_id([])

    @patch("builtins.input")
    @mark.parametrize("valid_ids", [[1], [2, 1], [23, 7, 1, 2]])
    def test_straight_correct_input(self, mock_input, valid_ids):
        mock_input.return_value = "1"

        res = under_test._interactive_person_id([2, 1])

        assert res == 1


class TestInteractiveHitEnter:

    @patch("builtins.input")
    def test_interactive_hit_enter_straight_correct_input(self, mock_input):
        mock_input.return_value = ""

        under_test._interactive_hit_enter()

        mock_input.assert_called_once_with()
        assert mock_input.call_count == 1

    @patch("builtins.input")
    def test_interactive_hit_enter_incorrect_inputs(self, mock_input):
        mock_input.side_effect = ["q", "12", "ENTER", ""]

        under_test._interactive_hit_enter()

        mock_input.assert_has_calls([call(), call(), call(), call()])
        assert mock_input.call_count == 4


class TestUpdatePerson:
    @patch("builtins.print")
    @patch.object(under_test, "_get_person_details")
    @patch.object(under_test, "show_person")
    def test_top_level(self, mock_show_person, mock_get_person_details, mock_print):
        person = Person(1, "John", "Doe")
        mock_get_person_details.return_value = ("foo", "bar")

        res = under_test.update_person(person)

        assert res.firstname == "foo"
        assert res.lastname == "bar"

        mock_show_person.assert_called_once_with(person)
        mock_get_person_details.assert_called_once_with()
        mock_print.assert_has_calls(
            [
                call("Input new first name and last name to update:"),
                call(CTRL_C_TO_EXIT),
            ]
        )

    @patch("builtins.print")
    @patch("builtins.input")
    @patch.object(under_test, "show_person")
    def test_get_person_details_one_word(self, mock_show_person, mock_input, mock_print):
        person = Person(1, "John", "Doe")

        mock_input.return_value = "foo"

        res = under_test.update_person(person)

        assert res.firstname == "foo"
        assert res.lastname is None
        mock_input.assert_called_once_with()
        assert mock_print.call_count == 2

    @patch("builtins.print")
    @patch("builtins.input")
    @patch.object(under_test, "show_person")
    def test_get_person_details_two_words(self, mock_show_person, mock_input, mock_print):
        person = Person(1, "John", "Doe")

        mock_input.return_value = "foo bar"

        res = under_test.update_person(person)

        assert res.firstname == "foo"
        assert res.lastname == "bar"
        mock_input.assert_called_once_with()
        assert mock_print.call_count == 2

    @patch("builtins.print")
    @patch("builtins.input")
    @patch.object(under_test, "show_person")
    def test_get_person_three_words(self, mock_show_person, mock_input, mock_print):
        person = Person(1, "John", "Doe")

        mock_input.side_effect = ["foo bar acme", "foo bar"]

        res = under_test.update_person(person)

        assert res.firstname == "foo"
        assert res.lastname == "bar"
        assert mock_input.call_count == 2
        mock_print.assert_has_calls(
            [
                call("Input new first name and last name to update:"),
                call(CTRL_C_TO_EXIT),
                call("Too many words."),
            ]
        )


class TestDeletingRelationship:
    @patch("builtins.print")
    @patch.object(under_test, "_interactive_hit_enter")
    def test_left_person(self, mock_hit_enter, mock_print):
        person1 = Person(1, "Seb", "King")
        person2 = Person(2, "Mario", "Bros")
        rld = RelationshipDefinition(name="rld")
        rl1 = Relationship(person1, person2, rld)

        under_test.deleting_relationship(rl1, person1)

        mock_print.assert_has_calls(
            [
                call("Hit ENTER to delete:"),
                call("    -> rld de (2) Mario Bros"),
                call(CTRL_C_TO_EXIT),
            ]
        )
        assert mock_print.call_count == 3
        mock_hit_enter.assert_called_once_with()
