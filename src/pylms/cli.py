from pylms.core import RelationshipAlias
from pylms.pylms import IOs, EventListener, ExitPyLMS
from pylms.pylms import Person, Relationship, RelationshipDefinition


class CLI(IOs, EventListener):
    def creating_person(self, person: Person) -> None:
        print(f"Create Person {person}.")

    def show_person(self, person: Person) -> None:
        created = person.created
        print(
            f"({person.person_id})",
            f" {person.sex.name}" if person.sex is not None else "",
            person,
            f"({created.year}-{created.month}-{created.day} {created.hour}-{created.minute}-{created.second})",
        )

    @staticmethod
    def _show_relationship_of(*, relationship: Relationship, person: Person) -> None:
        other = relationship.right if relationship.left == person else relationship.left
        print(f"    -> {relationship.repr_for(person)} ({other.person_id}) {other}")

    def list_persons(self, resolved_persons: list[(Person, list[Relationship])]) -> None:
        if resolved_persons:
            for person, rs in sorted(resolved_persons, key=lambda t: t[0].person_id):
                self.show_person(person)
                for r in rs:
                    self._show_relationship_of(relationship=r, person=person)
        else:
            print("No Person registered yet.")

    def _interactive_hit_enter(self):
        while True:
            s = self._input_or_exit_pylms()

            if len(s) == 0:
                return

            print("Just hit ENTER")

    def _input_or_exit_pylms(self):
        try:
            return input()
        except KeyboardInterrupt:
            raise ExitPyLMS()

    def _interactive_person_id(self, valid_ids: list[int]) -> int:
        if not valid_ids:
            raise ValueError("valid_ids can not be empty.")

        while True:
            n = self._input_or_exit_pylms()

            try:
                res = int(n)
                if res not in valid_ids:
                    print("Not a valid id.")
                    continue

                return res
            except ValueError:
                print("Not an integer.")

    def select_person(self, persons: list[Person]) -> Person | None:
        print("Input id of person to update:")
        for person in sorted(persons, key=lambda p: p.person_id):
            self.show_person(person)
        self._print_how_to_interrupt()

        person_id = self._interactive_person_id([person.person_id for person in persons])
        for person in persons:
            if person.person_id == person_id:
                return person

        # should not happen
        raise RuntimeError(f"id {person_id} does not exist in list of Persons")

    def update_person(self, person_to_update: Person) -> Person:
        print("Input new first name and last name to update:")
        self.show_person(person_to_update)
        self._print_how_to_interrupt()

        firstname: str
        lastname: str
        firstname, lastname = self._get_person_details()

        person_to_update.firstname = firstname
        person_to_update.lastname = lastname

        return person_to_update

    @staticmethod
    def _print_how_to_interrupt():
        print("CTRL+C to exit")

    def _get_person_details(self) -> tuple[str, str | None]:
        while True:
            text = self._input_or_exit_pylms()

            words = text.split(" ")
            if len(words) > 2:
                print("Too many words.")
                continue

            if len(words) == 1:
                return words[0], None
            return words[0], words[1]

    def deleting_person(self, person_to_delete: Person) -> None:
        print("Hit ENTER to delete:")
        self.show_person(person_to_delete)
        self._print_how_to_interrupt()
        self._interactive_hit_enter()

    def deleting_relationship(self, relationship: Relationship, person: Person) -> None:
        print("Hit ENTER to delete:")
        self._show_relationship_of(relationship=relationship, person=person)
        self._print_how_to_interrupt()
        self._interactive_hit_enter()

    def creating_link(self, rl_definition: RelationshipDefinition, person_left: Person, person_right: Person) -> None:
        print(f'Hit ENTER to link as "{rl_definition.name}":')
        self.show_person(person_left)
        self.show_person(person_right)
        self._print_how_to_interrupt()
        self._interactive_hit_enter()

    def configured_from_alias(self, person: Person, alias: RelationshipAlias) -> None:
        print(f"Sex of {person} set to {person.sex} from alias {alias.name}")
