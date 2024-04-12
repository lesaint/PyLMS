from pathlib import Path
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


def test_read_persons_returns_json_content_of_file(tmpdir):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)
    expected = {"a": "b", "c": ["d", "e"]}
    with file.open("w"):
        file.write_text(json.dumps(expected))

    with patch("pylms.storage.file_name", file_name):
        assert read_persons() == expected


def test_store_persons_empty_list():
    with raises(ValueError, match="Can't store an empty list of Persons."):
        store_persons([])


@mark.parametrize(
    ["persons"],
    [
        ([("Sébastien", "Lesaint")],),
        ([("Sébastien", "Lesaint"), ("Max", "Payne"), ("Homer", "Simpson")],),
    ],
)
def test_store_persons(tmpdir, persons):
    file_name = tmpdir + "foo.db"
    file = Path(file_name)

    with patch("pylms.storage.file_name", file_name):
        store_persons(persons)

    with file.open("r"):
        assert file.read_text() == json.dumps(persons)
