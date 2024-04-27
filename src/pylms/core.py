import datetime


class Person:
    def __init__(self, person_id: int, firstname: str, lastname: str = None, created: datetime.datetime = None) -> None:
        if person_id is None:
            raise ValueError("id can't be None")
        if not firstname:
            raise ValueError("firstname can't be None")

        self.person_id = int(person_id)
        self.firstname = firstname
        self.lastname = lastname
        self.created = Person.check_or_set(created)

    @staticmethod
    def check_or_set(dt: datetime.datetime | None) -> datetime.datetime:
        if not dt:
            return datetime.datetime.now()
        # can't make isinstance work:  :'(
        #    fails with "TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union"
        # if not isinstance(dt, datetime.datetime):
        #     raise ValueError(f"created parameter must be a datetime (got {type(dt)})")
        return dt

    def __eq__(self, other: any) -> bool:
        if isinstance(other, Person):
            return (
                self.person_id == other.person_id
                and other.firstname == self.firstname
                and other.lastname == self.lastname
            )
        return False

    def __repr__(self) -> str:
        if self.lastname:
            return f"{self.firstname} {self.lastname}"
        return self.firstname


class PersonIdGenerator:
    def __init__(self, existing_persons: list[Person]):
        self.next_id = max(map(lambda person: person.person_id, existing_persons), default=-1) + 1

    def next_person_id(self) -> int:
        res = self.next_id
        self.next_id += 1
        return res


class RelationshipDefinition:
    def __init__(
        self,
        name: str,
        aliases: list[str] = None,
        person_left_repr: str = None,
        person_right_repr: str = None,
    ) -> None:
        self._name: str = name
        self._person_left_repr: str = name if person_left_repr is None else person_left_repr
        self._person_right_repr: str = name if person_right_repr is None else person_right_repr
        self._aliases: list[str] = [] if aliases is None else aliases[:]

    @property
    def name(self) -> str:
        return self._name

    @property
    def aliases(self) -> list[str]:
        return self._aliases

    def left_repr(self, person: Person) -> str:
        return self._person_left_repr

    def right_repr(self, person: Person) -> str:
        return self._person_right_repr

    def __repr__(self) -> str:
        return self._name


parent_enfant = RelationshipDefinition(
    name="Parent/Enfant",
    aliases=[
        "père de",
        "mère de",
        "fils de",
        "fille de",
        "parent de",
        "enfant de",
    ],
    person_left_repr="parent",
    person_right_repr="enfant",
)

copain_copine = RelationshipDefinition(
    name="Copain/Copine",
    aliases=["copain de", "copine de"],
    person_left_repr="copain",
    person_right_repr="copain",
)

relationship_definitions = [parent_enfant, copain_copine]


class Relationship:
    def __init__(self, person_left: Person, person_right: Person, definition: RelationshipDefinition) -> None:
        self._person_left: Person = person_left
        self._person_right: Person = person_right
        self._definition: RelationshipDefinition = definition

    @property
    def left(self) -> Person:
        return self._person_left

    @property
    def right(self) -> Person:
        return self._person_right

    @property
    def definition(self) -> RelationshipDefinition:
        return self._definition

    def applies_to(self, person: Person) -> bool:
        return self._person_left == person or self._person_right == person

    def repr_for(self, person: Person) -> str:
        if person == self._person_left:
            return self._definition.left_repr(person)
        if person == self._person_right:
            return self._definition.right_repr(person)
        raise ValueError(f"{person} is neither the left nor right person of this {self._definition.name} relationship")


def resolve_persons(persons: list[Person], relationships: list[Relationship]) -> list[(Person, list[Relationship])]:
    return [(person, list(filter(lambda r: r.applies_to(person), relationships))) for person in persons]
