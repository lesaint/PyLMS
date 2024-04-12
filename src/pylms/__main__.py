#!/bin/env python3

from sys import argv
from pylms.pylms import list_persons, store_person


def main() -> None:
    argv_length = len(argv)
    if argv_length == 2:
        store_person(firstname=argv[1])
    elif argv_length == 3:
        store_person(firstname=argv[1], lastname=argv[2])
    elif argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
    else:
        list_persons()


if __name__ == "__main__":
    main()
