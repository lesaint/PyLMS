#!/bin/env python3

import logging
import sys
from sys import argv
import pylms.pylms
from pylms.pylms import list_persons, store_person, update_person, delete_person, link_persons, search_persons
from pylms.pylms import ExitPyLMS
from pylms.cli import CLI


def main() -> None:
    _cli = CLI()
    pylms.pylms.ios = _cli
    pylms.pylms.events = _cli
    logging.basicConfig(level=logging.INFO)
    try:
        _read_and_execute_commands()
    except ExitPyLMS:
        pass


def _read_and_execute_commands() -> None:
    args: list[str] = argv[1:]

    if not args:
        _command_list()
        return

    command = args[0].lower()
    if command == "create":
        _command_create(args[1:])
        return

    if command == "update":
        _command_update(args[1:])
        return

    if command == "delete":
        _command_delete(args[1:])
        return

    if command == "link":
        _command_link(args[1:])
        return

    _command_search(args)


def _command_list() -> None:
    list_persons()


def _command_create(arguments: list[str]) -> None:
    arguments_count = len(arguments)
    if arguments_count < 1:
        print(f"Too few arguments ({arguments_count})")
        return
    if arguments_count > 2:
        print(f"Too many arguments ({arguments_count})")
        return

    if arguments_count == 1:
        store_person(firstname=arguments[0])
    else:
        store_person(firstname=arguments[0], lastname=arguments[1])


def _command_update(arguments: list[str]) -> None:
    arguments_count = len(arguments)
    if arguments_count > 1:
        print(f"Too many arguments ({arguments_count})")
        return

    if arguments_count == 1:
        update_person(pattern=arguments[0])
    else:
        print(f"Missing search pattern")


def _command_delete(arguments: list[str]) -> None:
    arguments_count = len(arguments)
    if arguments_count > 1:
        print(f"Too many arguments ({arguments_count})")
        return

    if arguments_count == 1:
        delete_person(pattern=arguments[0])
    else:
        print(f"Missing search pattern")


def _command_link(arguments: list[str]) -> None:
    arguments_count = len(arguments)
    if arguments_count < 2:
        print(f"Too few arguments ({arguments_count})")
        return

    natural_link_request = " ".join(arguments)
    link_persons(natural_link_request)


def _command_search(arguments: list[str]) -> None:
    arguments_count = len(arguments)
    if arguments_count < 1:
        print(f"Too few arguments ({arguments_count})")
        return

    natural_search_request = " ".join(arguments)
    search_persons(natural_search_request)


if __name__ == "__main__":
    main()
