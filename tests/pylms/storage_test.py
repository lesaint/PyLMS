from pathlib import Path
from pylms.core import Person
from pylms.storage import read_persons, store_persons
from pytest import raises
from pytest import mark
from unittest.mock import patch
import json


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
        file.write_text('[{"firstname": "John", "lastname": "Doe"}]')

    with patch("pylms.storage.file_name", file_name):
        persons = read_persons()
        assert len(persons) == 1
        assert persons[0].firstname == "John"
        assert persons[0].lastname == "Doe"


def test_read_one_person_without_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    with file.open("w"):
        file.write_text(r'[{"firstname": "S\u00e9bastien"}]')

    with patch("pylms.storage.file_name", file_name):
        persons = read_persons()
        assert len(persons) == 1
        assert persons[0].firstname == "Sébastien"
        assert persons[0].lastname is None


def test_store_empty_list():
    with raises(ValueError, match="Can't store an empty list of Persons."):
        store_persons([])


def test_store_one_person_with_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person = Person("Jim", "Morisson")

    with patch("pylms.storage.file_name", file_name):
        store_persons([person])

    with file.open("r"):
        assert file.read_text() == '[{"firstname": "Jim", "lastname": "Morisson"}]'


def test_store_one_person_without_lastname(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    person = Person("Jim")

    with patch("pylms.storage.file_name", file_name):
        store_persons([person])

    with file.open("r"):
        assert file.read_text() == '[{"firstname": "Jim"}]'


def test_store_persons(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    persons = [Person("Sébastien", "Lesaint"), Person("Max", "Payne"), Person("Bob")]

    with patch("pylms.storage.file_name", file_name):
        store_persons(persons)

    with file.open("r"):
        assert (
            file.read_text() == "["
            r'{"firstname": "S\u00e9bastien", "lastname": "Lesaint"}, '
            '{"firstname": "Max", "lastname": "Payne"}, '
            '{"firstname": "Bob"}'
            "]"
        )
