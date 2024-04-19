#!/bin/env python3

from sys import argv
from pylms.pylms import list_persons, store_person, update_person, delete_person, link_persons, ExitPyLMS


def main() -> None:
    try:
        _read_and_execute_commands()
    except ExitPyLMS:
        pass


def _read_and_execute_commands() -> None:
    argv_length = len(argv)

    if argv_length == 1:
        _command_list()
        return

    if argv[1].lower() == "update":
        _command_update(argv_length)
        return

    if argv[1].lower() == "delete":
        _command_delete(argv_length)
        return

    if argv[1].lower() == "link":
        _command_link(argv_length)
        return

    _command_create(argv_length)


def _command_list() -> None:
    list_persons()


def _command_create(argv_length: int) -> None:
    if argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
        return

    if argv_length == 2:
        store_person(firstname=argv[1])
    else:
        store_person(firstname=argv[1], lastname=argv[2])


def _command_update(argv_length: int) -> None:
    if argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
        return

    if argv_length == 3:
        update_person(pattern=argv[2])
    else:
        print(f"Missing search pattern")


def _command_delete(argv_length: int) -> None:
    if argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
        return

    if argv_length == 3:
        delete_person(pattern=argv[2])
    else:
        print(f"Missing search pattern")


def _command_link(argv_length: int) -> None:
    if argv_length < 4:
        print(f"Too few arguments ({argv_length -1})")

    natural_link_request = " ".join(argv[2:])
    link_persons(natural_link_request)


if __name__ == "__main__":
    main()
