from datetime import datetime
from pathlib import Path
from pylms.core import Person, Relationship, RelationshipDefinition
from pylms.storage import read_persons, store_persons
from pylms.storage import read_relationships, store_relationships
from pytest import raises, mark
from unittest.mock import patch


def test_read_persons_no_file(tmpdir):
    with patch("pylms.storage.persons_file_name", tmpdir + "foo.db"):
        assert not read_persons()


def test_read_persons_empty_file(tmpdir):
    file_name = tmpdir + "foo.db"
    Path(file_name).touch()
    with patch("pylms.storage.persons_file_name", file_name):
        assert not read_persons()


def test_read_one_person_with_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    with file.open("w"):
        file.write_text('[{"id": 11, "firstname": "John", "lastname": "Doe", "created": "2024-04-16 12:40:30.407998"}]')

    with patch("pylms.storage.persons_file_name", file_name):
        persons = read_persons()
        assert len(persons) == 1
        assert persons[0].person_id == 11
        assert persons[0].firstname == "John"
        assert persons[0].lastname == "Doe"
        assert persons[0].created == datetime(2024, 4, 16, 12, 40, 30, 407998)


def test_read_one_person_without_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    with file.open("w"):
        file.write_text(r'[{"id": 10, "firstname": "S\u00e9bastien", "created": "2024-04-16 12:40:30"}]')

    with patch("pylms.storage.persons_file_name", file_name):
        persons = read_persons()
        assert len(persons) == 1
        assert persons[0].person_id == 10
        assert persons[0].firstname == "Sébastien"
        assert persons[0].lastname is None
        assert persons[0].created == datetime(2024, 4, 16, 12, 40, 30)


def test_store_empty_list_of_persons():
    with raises(ValueError, match="Can't store an empty list of Persons."):
        store_persons([])


def test_store_one_person_with_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person = Person(1, "Jim", "Morisson", created=datetime(2024, 4, 5, 12, 41, 9))

    with patch("pylms.storage.persons_file_name", file_name):
        store_persons([person])

    with file.open("r"):
        assert (
            file.read_text()
            == '[{"id": 1, "firstname": "Jim", "lastname": "Morisson", "created": "2024-04-05 12:41:09"}]'
        )


def test_store_one_person_without_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person = Person(2, "Jim", created=datetime(2024, 4, 5, 12, 41, 58))

    with patch("pylms.storage.persons_file_name", file_name):
        store_persons([person])

    with file.open("r"):
        assert file.read_text() == '[{"id": 2, "firstname": "Jim", "created": "2024-04-05 12:41:58"}]'


def test_store_persons(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    t1 = datetime(2024, 4, 5, 12, 41, 58)
    t2 = datetime(2024, 9, 18, 21, 8, 8)
    persons = [
        Person(3, "Sébastien", "Lesaint", t1),
        Person(4, "Max", "Payne", t2),
        Person(5, "Bob", created=t2),
    ]

    with patch("pylms.storage.persons_file_name", file_name):
        store_persons(persons)

    with file.open("r"):
        assert (
            file.read_text() == "["
            r'{"id": 3, "firstname": "S\u00e9bastien", "lastname": "Lesaint", "created": "2024-04-05 12:41:58"}, '
            '{"id": 4, "firstname": "Max", "lastname": "Payne", "created": "2024-09-18 21:08:08"}, '
            '{"id": 5, "firstname": "Bob", "created": "2024-09-18 21:08:08"}'
            "]"
        )


def test_store_empty_list_of_relationships():
    with raises(ValueError, match="Can't store an empty list of Relationships."):
        store_relationships([])


def test_store_one_relationship(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person1 = Person(1, "Jim", "Morisson")
    person2 = Person(2, "Paul", "John")
    definition = RelationshipDefinition(name="rs_name")
    relationship = Relationship(person_left=person1, person_right=person2, definition=definition)

    with patch("pylms.storage.relationships_file_name", file_name):
        store_relationships([relationship])

    with file.open("r"):
        assert file.read_text() == '[{"left": 1, "right": 2, "definition": "rs_name"}]'


def test_store_relationships(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person1 = Person(1, "Jim", "Morisson")
    person2 = Person(2, "Paul", "John")
    person3 = Person(3, "Tony", "Parker")
    definition1 = RelationshipDefinition(name="rs1_name")
    definition2 = RelationshipDefinition(name="rs2_name")

    with patch("pylms.storage.relationships_file_name", file_name):
        store_relationships(
            [
                Relationship(person_left=person1, person_right=person2, definition=definition1),
                Relationship(person_left=person2, person_right=person3, definition=definition2),
                Relationship(person_left=person3, person_right=person2, definition=definition1),
                Relationship(person_left=person1, person_right=person3, definition=definition2),
                Relationship(person_left=person1, person_right=person2, definition=definition1),
            ]
        )

    with file.open("r"):
        assert file.read_text() == (
            "["
            '{"left": 1, "right": 2, "definition": "rs1_name"}'
            ", "
            '{"left": 2, "right": 3, "definition": "rs2_name"}'
            ", "
            '{"left": 3, "right": 2, "definition": "rs1_name"}'
            ", "
            '{"left": 1, "right": 3, "definition": "rs2_name"}'
            ", "
            '{"left": 1, "right": 2, "definition": "rs1_name"}'
            "]"
        )


def test_read_relationships_empty_list_of_persons():
    with raises(ValueError, match="Persons can't be empty"):
        read_relationships([])


def test_read_relationships_no_file(tmpdir):
    persons = [Person(2, "Foo", "Bar")]

    with patch("pylms.storage.relationships_file_name", tmpdir + "foo.db"):
        assert not read_relationships(persons)


def test_read_relationships_empty_file(tmpdir):
    persons = [Person(2, "Foo", "Bar")]
    file_name = tmpdir + "foo.db"
    Path(file_name).touch()

    with patch("pylms.storage.relationships_file_name", file_name):
        assert not read_relationships(persons)


def test_read_one_relationship(tmpdir):
    file_name = tmpdir + "foo.db"
    persons = [
        Person(2, "Foo", "Bar"),
        Person(3, "Acme", "Donut"),
    ]
    relationship = RelationshipDefinition(name="rs1_name")
    file = Path(file_name)
    with file.open("w"):
        file.write_text('[{"left": 3, "right": 2, "definition": "rs1_name"}]')

    with (
        patch("pylms.storage.relationships_file_name", file_name),
        patch("pylms.storage.relationship_definitions", new=[relationship]),
    ):
        relationships = read_relationships(persons)
        assert len(relationships) == 1
        assert relationships[0].left == persons[1]
        assert relationships[0].right == persons[0]
        assert relationships[0].definition is relationship


@mark.parametrize(
    "serialized_relationship",
    [
        '{"left": 4, "right": 2, "definition": "rs1_name"}',
        '{"left": 3, "right": 1, "definition": "rs1_name"}',
        '{"left": 3, "right": 2, "definition": "does_not_exist"}',
        '{"left": 4, "right": 2, "definition": "rs1_name"}',
        '{"left": 1, "right": 4, "definition": "rs1_name"}',
        '{"left": 10, "right": 12, "definition": "does_not_exist"}',
    ],
)
def test_read_relationship_ignore_entry_if_person_or_definition_does_not_exist(serialized_relationship, tmpdir):
    file_name = tmpdir + "foo.db"
    persons = [
        Person(2, "Foo", "Bar"),
        Person(3, "Acme", "Donut"),
    ]
    relationship = RelationshipDefinition(name="rs1_name")
    file = Path(file_name)
    with file.open("w"):
        file.write_text(f"[{serialized_relationship}]")

    with (
        patch("pylms.storage.relationships_file_name", file_name),
        patch("pylms.storage.relationship_definitions", new=[relationship]),
    ):
        assert not read_relationships(persons)


def test_read_relationships(tmpdir):
    file_name = tmpdir + "foo.db"
    persons = [
        Person(1, "Jim", "Morisson"),
        Person(2, "Paul", "John"),
        Person(3, "Tony", "Parker"),
    ]
    relationship1 = RelationshipDefinition(name="rs1_name")
    relationship2 = RelationshipDefinition(name="rs2_name")
    file = Path(file_name)
    with file.open("w"):
        file.write_text(
            "["
            '{"left": 1, "right": 2, "definition": "rs1_name"}'
            ", "
            '{"left": 2, "right": 3, "definition": "rs2_name"}'
            ", "
            '{"left": 3, "right": 2, "definition": "rs1_name"}'
            ", "
            '{"left": 1, "right": 3, "definition": "rs2_name"}'
            ", "
            '{"left": 1, "right": 2, "definition": "rs1_name"}'
            "]"
        )

    with (
        patch("pylms.storage.relationships_file_name", file_name),
        patch("pylms.storage.relationship_definitions", new=[relationship1, relationship2]),
    ):
        relationships = read_relationships(persons)
        assert len(relationships) == 5

        assert relationships[0].left == persons[0]
        assert relationships[0].right == persons[1]
        assert relationships[0].definition is relationship1

        assert relationships[1].left == persons[1]
        assert relationships[1].right == persons[2]
        assert relationships[1].definition is relationship2

        assert relationships[2].left == persons[2]
        assert relationships[2].right == persons[1]
        assert relationships[2].definition is relationship1

        assert relationships[3].left == persons[0]
        assert relationships[3].right == persons[2]
        assert relationships[3].definition is relationship2

        assert relationships[4].left == persons[0]
        assert relationships[4].right == persons[1]
        assert relationships[4].definition is relationship1
