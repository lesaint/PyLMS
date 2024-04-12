#!/bin/env python3

from sys import argv
from pylms.storage import store_persons, read_persons


def list_persons():
    persons = read_persons()
    if persons:
        for person in persons:
            print("*", person[0], person[1] if len(person) > 1 else None)
    else:
        print("No Person registered yet.")


def main() -> None:
    argv_length = len(argv)
    if argv_length == 2:
        print(f"Create Person {argv[1]}.")
        store_persons([(argv[1],)])
    elif argv_length == 3:
        print(f"Create Person {argv[1]} {argv[2]}.")
        store_persons([(argv[1], argv[2])])
    elif argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
    else:
        list_persons()


if __name__ == "__main__":
    main()
