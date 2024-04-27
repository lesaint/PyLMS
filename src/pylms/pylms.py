from pylms import storage
from pylms.core import Person, PersonIdGenerator
from pylms.core import relationship_definitions, RelationshipDefinition, Relationship
from pylms.core import resolve_persons
from abc import abstractmethod, ABC


class ExitPyLMS(BaseException):
    pass


class IOs(ABC):
    @abstractmethod
    def show_person(self, person: Person) -> None:
        pass

    @abstractmethod
    def list_persons(self, persons: list[Person]) -> None:
        pass

    @abstractmethod
    def select_person(self, persons: list[Person]) -> Person | None:
        pass

    @abstractmethod
    def get_person_details(self) -> tuple[str, str | None]:
        pass


class EventListener(ABC):
    @abstractmethod
    def creating_person(self, person: Person) -> None:
        pass

    @abstractmethod
    def deleting_person(self, person_to_delete: Person) -> None:
        pass

    @abstractmethod
    def creating_link(self, rl_definition: RelationshipDefinition, person_left: Person, person_right: Person) -> None:
        pass


class CLI(IOs, EventListener):
    def creating_person(self, person: Person) -> None:
        print(f"Create Person {person}.")

    def show_person(self, person: Person) -> None:
        created = person.created
        print(
            f"({person.person_id})",
            person,
            f"({created.year}-{created.month}-{created.day} {created.hour}-{created.minute}-{created.second})",
        )

    def list_persons(self, resolved_persons: list[(Person, list[Relationship])]) -> None:
        if resolved_persons:
            for person, rs in sorted(resolved_persons, key=lambda t: t[0].person_id):
                ios.show_person(person)
                for r in rs:
                    other = r.right if r.left == person else r.left
                    print(f"    -> {r.repr_for(person)} de ({other.person_id}) {other}")
        else:
            print("No Person registered yet.")

    def _interactive_hit_enter(self):
        while True:
            s = self._input_or_exit_pylms()

            if len(s) == 0:
                return

            print("Just hit ENTER")
            continue

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
        print("CTRL+C to exit")

        person_id = self._interactive_person_id([person.person_id for person in persons])
        for person in persons:
            if person.person_id == person_id:
                return person

        # should not happen
        raise RuntimeError(f"id {person_id} does not exist in list of Persons")

    def get_person_details(self) -> tuple[str, str | None]:
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
        print("CTRL+C to exit")
        self._interactive_hit_enter()

    def creating_link(self, rl_definition: RelationshipDefinition, person_left: Person, person_right: Person) -> None:
        print(f'Hit ENTER to link as "{rl_definition.name}":')
        self.show_person(person_left)
        self.show_person(person_right)
        print("CTRL+C to exit")
        self._interactive_hit_enter()


_cli: CLI = CLI()
ios: IOs = _cli
events: EventListener = _cli


def list_persons() -> None:
    persons = storage.read_persons()

    resolved_persons = []
    if persons:
        relationships = storage.read_relationships(persons)
        resolved_persons = resolve_persons(persons, relationships)

    ios.list_persons(resolved_persons)


def _interactive_select_person(pattern: str) -> Person | None:
    persons = _search_person(pattern)
    if not persons:
        print("No match.")
        return

    if len(persons) == 1:
        return persons[0]

    return ios.select_person(persons)


def update_person(pattern: str) -> None:
    person_to_update: Person = _interactive_select_person(pattern)
    if not person_to_update:
        return

    print("Input new first name and last name to update:")
    ios.show_person(person_to_update)
    print("CTRL+C to exit")

    firstname: str
    lastname: str
    firstname, lastname = ios.get_person_details()

    persons = storage.read_persons()
    for person in persons:
        if person.person_id == person_to_update.person_id:
            person.firstname = firstname
            person.lastname = lastname
    storage.store_persons(persons)


def search_person(pattern: str) -> None:
    for person in _search_person(pattern):
        ios.show_person(person)


def _search_person(pattern: str) -> list[Person]:
    persons = storage.read_persons()

    res = []
    for person in persons:
        if _search_match(pattern, person):
            res.append(person)

    return res


def _search_match(pattern: str, person: Person) -> bool:
    pattern = pattern.lower()
    if person.lastname:
        return pattern in person.lastname.lower() or pattern in person.firstname.lower()

    return pattern in person.firstname.lower()


def store_person(firstname: str) -> None:
    persons = storage.read_persons()
    id_generator = PersonIdGenerator(persons)
    person = Person(person_id=id_generator.next_person_id(), firstname=firstname)
    events.creating_person(person)
    storage.store_persons([person] + persons)


def store_person(firstname: str, lastname: str = None) -> None:
    persons = storage.read_persons()
    id_generator = PersonIdGenerator(persons)
    person = Person(person_id=id_generator.next_person_id(), firstname=firstname, lastname=lastname)
    events.creating_person(person)
    storage.store_persons([person] + persons)


def delete_person(pattern: str) -> None:
    person_to_delete: Person = _interactive_select_person(pattern)
    if not person_to_delete:
        return

    events.deleting_person(person_to_delete)

    persons = storage.read_persons()
    persons.remove(person_to_delete)
    storage.store_persons(persons)


class LinkRequest:
    def __init__(
        self, *, left_person_pattern: str, right_person_pattern: str, definition: RelationshipDefinition, alias: str
    ) -> None:
        self.left_person_pattern: str = left_person_pattern
        self.right_person_pattern: str = right_person_pattern
        self.definition: RelationshipDefinition = definition
        self.alias: str = alias


def _find_relation_ship(natural_language_link_order: str) -> tuple[RelationshipDefinition, str] | None:
    if len(natural_language_link_order) == 0:
        return None

    natural_language_link_order = natural_language_link_order.lower()

    for rl in relationship_definitions:
        for alias in rl.aliases:
            if alias.lower() in natural_language_link_order:
                return rl, alias

    return None


def _parse_nl_link_request(natural_language_link_request: str) -> LinkRequest | None:
    match = _find_relation_ship(natural_language_link_request)
    if match is None:
        return None
    definition, alias = match

    person_patterns = list(filter(lambda s: len(s) > 0, map(str.strip, natural_language_link_request.split(alias))))
    patterns_count = len(person_patterns)
    if patterns_count != 2:
        print(f"Unsupported link request: wrong number of person patterns ({patterns_count})")
        return None

    return LinkRequest(
        left_person_pattern=person_patterns[0],
        right_person_pattern=person_patterns[1],
        definition=definition,
        alias=alias,
    )


def link_persons(natural_language_link_request: str) -> None:
    link_request = _parse_nl_link_request(natural_language_link_request)
    if link_request is None:
        return

    person_left = _interactive_select_person(link_request.left_person_pattern)
    person_right = _interactive_select_person(link_request.right_person_pattern)

    if person_left is None:
        print(f'No match for "{link_request.left_person_pattern}".')
    if person_right is None:
        print(f'No match for "{link_request.right_person_pattern}".')
    if person_left is None or person_right is None:
        return

    events.creating_link(link_request.definition, person_left, person_right)

    persons = storage.read_persons()
    relationships = storage.read_relationships(persons)
    relationship = Relationship(
        person_left=person_left,
        person_right=person_right,
        definition=link_request.definition,
    )
    storage.store_relationships(relationships + [relationship])
