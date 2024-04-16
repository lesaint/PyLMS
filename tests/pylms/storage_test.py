from datetime import datetime
from pathlib import Path
from pylms.core import Person
from pylms.storage import read_persons, store_persons
from pytest import raises
from unittest.mock import patch


def test_read_persons_no_file(tmpdir):
    with patch("pylms.storage.file_name", tmpdir + "foo.db"):
        assert not read_persons()


def test_read_persons_empty_file(tmpdir):
    file_name = tmpdir + "foo.db"
    Path(file_name).touch()
    with patch("pylms.storage.file_name", file_name):
        assert not read_persons()


def test_read_one_person_with_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    with file.open("w"):
        file.write_text('[{"id": 11, "firstname": "John", "lastname": "Doe", "created": "2024-04-16 12:40:30.407998"}]')

    with patch("pylms.storage.file_name", file_name):
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

    with patch("pylms.storage.file_name", file_name):
        persons = read_persons()
        assert len(persons) == 1
        assert persons[0].person_id == 10
        assert persons[0].firstname == "Sébastien"
        assert persons[0].lastname is None
        assert persons[0].created == datetime(2024, 4, 16, 12, 40, 30)


def test_store_empty_list():
    with raises(ValueError, match="Can't store an empty list of Persons."):
        store_persons([])


def test_store_one_person_with_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person = Person(1, "Jim", "Morisson", created=datetime(2024, 4, 5, 12, 41, 9))

    with patch("pylms.storage.file_name", file_name):
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

    with patch("pylms.storage.file_name", file_name):
        store_persons([person])

    with file.open("r"):
        assert file.read_text() == '[{"id": 2, "firstname": "Jim", "created": "2024-04-05 12:41:58"}]'


def test_store_persons(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    t1 = datetime(2024, 4, 5, 12, 41, 58)
    t2 = datetime(2024, 9, 18, 21, 8, 8)
    persons = [Person(3, "Sébastien", "Lesaint", t1), Person(4, "Max", "Payne", t2), Person(5, "Bob", created=t2)]

    with patch("pylms.storage.file_name", file_name):
        store_persons(persons)

    with file.open("r"):
        assert (
            file.read_text() == "["
            r'{"id": 3, "firstname": "S\u00e9bastien", "lastname": "Lesaint", "created": "2024-04-05 12:41:58"}, '
            '{"id": 4, "firstname": "Max", "lastname": "Payne", "created": "2024-09-18 21:08:08"}, '
            '{"id": 5, "firstname": "Bob", "created": "2024-09-18 21:08:08"}'
            "]"
        )
