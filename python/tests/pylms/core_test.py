from datetime import datetime
from pylms.pylms import Person
from pylms.pylms import PersonIdGenerator
from unittest.mock import patch
from pylms.core import RelationshipDefinition, Relationship, RelationshipAlias
from pylms.core import Sex, MALE, FEMALE
from pytest import raises, mark


@patch("pylms.core.datetime.datetime")
def test_created_not_provided_in_constructor(mock_datetime):
    expected = datetime(2024, 4, 16, 2, 2, 2)
    mock_datetime.now.return_value = expected

    under_test = Person(person_id=1, firstname="f", lastname="n")

    assert under_test.created == expected


def test_created_provided_in_constructor():
    expected = datetime(2024, 4, 16, 2, 2, 2)
    other = datetime(2024, 4, 16, 10, 10, 10)

    with patch("pylms.core.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = other
        under_test = Person(person_id=1, firstname="f", lastname="n", created=expected)

    assert under_test.created == expected


def test_eq():
    under_test = Person(person_id=1, firstname="f", lastname="n")

    assert under_test == Person(1, "f", "n")
    assert under_test != Person(2, "f", "n")
    assert under_test != Person(1, "d", "n")
    assert under_test != Person(1, "f", "m")
    assert under_test != Person(1, "f", None)
    assert under_test != (1, "f", "n")


def test_created_not_in_eq():
    t1 = datetime(2023, 4, 16, 11, 52, 56)
    t2 = datetime(2023, 4, 16, 11, 53, 15)

    assert Person(person_id=1, firstname="f", lastname="n", created=t1) == Person(
        person_id=1, firstname="f", lastname="n", created=t2
    )


def test_generator_no_person():
    under_test = PersonIdGenerator([])

    assert under_test.next_person_id() == 0


def test_generator_one_person():
    under_test = PersonIdGenerator([Person(2, "n")])

    assert under_test.next_person_id() == 3


class TestRelationship:
    person1 = Person(1, "John", "Doe")
    person2 = Person(2, "Jane", "Doe")
    person3 = Person(3, "Diana", "King")
    definition = RelationshipDefinition(
        name="FooDef",
        person_left_default_repr="LeftFoo",
        person_right_default_repr="RightFoo",
    )
    relationship = Relationship(person_left=person1, person_right=person2, definition=definition)

    def test_repr_for_fails_if_neither_left_nor_right(self):
        expected_message = f"{self.person3} is neither the left nor right person of this FooDef relationship"
        with raises(ValueError, match=expected_message):
            self.relationship.repr_for(self.person3)

    def test_repr_for_left_person(self):
        assert self.relationship.repr_for(self.person1) == "LeftFoo"

    def test_repr_for_right_person(self):
        assert self.relationship.repr_for(self.person2) == "RightFoo"


class TestPersonSex:
    @mark.parametrize("constant_sex", [MALE, FEMALE])
    def test_init_accepts_constant_as_parameter(self, constant_sex):
        Person(person_id=1, firstname="foo", lastname="acme", sex=constant_sex)

    @mark.parametrize("non_constant_sex", [Sex("MALE"), Sex("FEMALE"), Sex("FOO")])
    def test_init_fails_if_sex_is_not_constant(self, non_constant_sex):
        with raises(ValueError, match="Sex must be either constant MALE or FEMALE"):
            Person(person_id=1, firstname="foo", lastname="bar", sex=non_constant_sex)

    @mark.parametrize(
        "person",
        [
            Person(person_id=1, firstname="foo", sex=None),
            Person(person_id=1, firstname="foo", sex=MALE),
        ],
    )
    @mark.parametrize("non_constant_sex", [Sex("MALE"), Sex("FEMALE"), Sex("FOO")])
    def test_setter_fails_if_sex_is_not_constant(self, person, non_constant_sex):
        with raises(ValueError, match="Sex must be either constant MALE or FEMALE"):
            Person(person_id=1, firstname="foo", lastname="bar", sex=non_constant_sex)


class TestRelationshipReprFor:
    person1 = Person(1, "John", "Doe")
    person2 = Person(2, "Alita", "Donut")
    rl_def = RelationshipDefinition(name="rl")
    rl1 = Relationship(person_left=person1, person_right=person2, definition=rl_def)

    def test_raise_value_error_if_neither_left_nor_right(self):
        other_person = Person(12, "other", "unknown")
        with raises(ValueError, match="other unknown is neither the left nor right person of this rl relationship"):
            self.rl1.repr_for(other_person)

    @patch.object(rl_def, "left_repr")
    @patch.object(rl_def, "right_repr")
    def test_calls_left_repr_for_left_person(self, mock_right_repr, mock_left_repr):
        self.rl1.repr_for(self.person1)

        mock_left_repr.assert_called_once_with(self.person1)
        assert mock_right_repr.call_count == 0

    @patch.object(rl_def, "left_repr")
    @patch.object(rl_def, "right_repr")
    def test_calls_right_repr_for_right_person(self, mock_right_repr, mock_left_repr):
        self.rl1.repr_for(self.person2)

        assert mock_left_repr.call_count == 0
        mock_right_repr.assert_called_once_with(self.person2)


class TestRelationshipDefinitionRepr:
    person_no_sex = Person(1, "Camilla")
    person_male = Person(1, "Camille", sex=MALE)
    person_female = Person(1, "Pita", sex=FEMALE)
    rld_name = "foo"
    left_default = "bar"
    right_default = "donut"
    rld_no_default_no_alias = RelationshipDefinition(name=rld_name)
    rld_defaults_no_alias = RelationshipDefinition(
        name=rld_name, person_left_default_repr=left_default, person_right_default_repr=right_default
    )
    rld_defaults_all_aliases_variants = RelationshipDefinition(
        name=rld_name,
        person_left_default_repr=left_default,
        person_right_default_repr=right_default,
        aliases=[
            RelationshipAlias("no_sex_forward", reverse=False),
            RelationshipAlias("no_sex_reverse", reverse=True),
            RelationshipAlias("left_male_forward", left_person_sex=MALE, reverse=False),
            RelationshipAlias("left_female_forward", left_person_sex=FEMALE, reverse=False),
            RelationshipAlias("left_male_reverse", left_person_sex=MALE, reverse=True),
            RelationshipAlias("left_female_reverse", left_person_sex=FEMALE, reverse=True),
            RelationshipAlias("right_male_forward", right_person_sex=MALE, reverse=False),
            RelationshipAlias("right_female_forward", right_person_sex=FEMALE, reverse=False),
            RelationshipAlias("right_male_reverse", right_person_sex=MALE, reverse=True),
            RelationshipAlias("right_female_reverse", right_person_sex=FEMALE, reverse=True),
        ],
    )

    def test_right_repr_return_if_no_alias_nor_default(self):
        assert self.rld_no_default_no_alias.right_repr(self.person_no_sex) == self.rld_name

    def test_left_repr_return_if_no_alias_nor_default(self):
        assert self.rld_no_default_no_alias.left_repr(self.person_no_sex) == self.rld_name

    def test_right_repr_return_right_default_if_no_alias(self):
        assert self.rld_defaults_no_alias.right_repr(self.person_no_sex) == self.right_default

    def test_left_repr_return_right_default_if_no_alias(self):
        assert self.rld_defaults_no_alias.left_repr(self.person_no_sex) == self.left_default

    def test_left_repr_return_alias_forward_no_sex(self):
        assert self.rld_defaults_all_aliases_variants.left_repr(self.person_no_sex) == "no_sex_forward"

    def test_right_repr_return_alias_reverse_no_sex(self):
        assert self.rld_defaults_all_aliases_variants.right_repr(self.person_no_sex) == "no_sex_reverse"

    def test_left_repr_return_alias_forward_male(self):
        assert self.rld_defaults_all_aliases_variants.left_repr(self.person_male) == "left_male_forward"

    def test_right_repr_return_alias_reverse_male(self):
        assert self.rld_defaults_all_aliases_variants.right_repr(self.person_male) == "left_male_reverse"

    def test_left_repr_return_alias_forward_female(self):
        assert self.rld_defaults_all_aliases_variants.left_repr(self.person_female) == "left_female_forward"

    def test_right_repr_return_alias_reverse_female(self):
        assert self.rld_defaults_all_aliases_variants.right_repr(self.person_female) == "left_female_reverse"
