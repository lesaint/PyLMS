#!/bin/env python3

from sys import argv
from pylms.pylms import list_persons, store_person, update_person


def main() -> None:
    argv_length = len(argv)

    if argv_length == 1:
        _command_list()
        return

    if argv[1].lower() == "update":
        _command_update(argv_length)
        return

    _command_create(argv_length)


def _command_list():
    list_persons()


def _command_create(argv_length):
    if argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
        return

    if argv_length == 2:
        store_person(firstname=argv[1])
    else:
        store_person(firstname=argv[1], lastname=argv[2])


def _command_update(argv_length):
    if argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
        return

    if argv_length == 3:
        update_person(pattern=argv[2])
    else:
        print(f"Missing search pattern")


if __name__ == "__main__":
    main()
