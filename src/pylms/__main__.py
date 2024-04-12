#!/bin/env python3

from sys import argv


def main() -> None:
    argv_length = len(argv)
    if argv_length == 2:
        print(f"Create Person {argv[1]}.")
    elif argv_length == 3:
        print(f"Create Person {argv[1]} {argv[2]}.")
    elif argv_length > 3:
        print(f"Too many arguments ({argv_length - 1})")
    else:
        print("Requires at least one argument")


if __name__ == "__main__":
    main()
