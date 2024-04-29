import datetime


class Sex:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self):
        return self._name


MALE: Sex = Sex("MALE")
FEMALE: Sex = Sex("FEMALE")


class Person:
    def __init__(
        self,
        person_id: int,
        firstname: str,
        lastname: str = None,
        created: datetime.datetime = None,
        sex: Sex = None,
    ) -> None:
        if person_id is None:
            raise ValueError("id can't be None")
        if not firstname:
            raise ValueError("firstname can't be None")

        self.person_id = int(person_id)
        self.firstname = firstname
        self.lastname = lastname
        self._sex = None if sex is None else Person._check_sex(sex)
        self.created = Person._check_or_set_created(created)

    @staticmethod
    def _check_sex(sex: Sex) -> Sex:
        if sex != MALE and sex != FEMALE:
            raise ValueError("Sex must be either constant MALE or FEMALE")
        return sex

    @staticmethod
    def _check_or_set_created(dt: datetime.datetime | None) -> datetime.datetime:
        if not dt:
            return datetime.datetime.now()
        # can't make isinstance work:  :'(
        #    fails with "TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union"
        # if not isinstance(dt, datetime.datetime):
        #     raise ValueError(f"created parameter must be a datetime (got {type(dt)})")
        return dt

    @property
    def sex(self) -> Sex | None:
        return self._sex

    @sex.setter
    def sex(self, sex: Sex) -> None:
        self._sex = Person._check_sex(sex)

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


class RelationshipAlias:
    def __init__(
        self,
        name: str,
        *,
        left_person_sex: Sex = None,
        right_person_sex: Sex = None,
        reverse: bool = False,
    ) -> None:
        """
        A RelationshipAlias has a direction, that match the direction of the link request and may (`reversed=False`) or
        may not (`reversed`=True) match the one of the RelationshipDefinition,
        :param name:
        :param left_person_sex:
        :param right_person_sex:
        :param reverse: ignored if RelationshipDefinition.directional is False
        """
        self._name: str = name
        self._left_person_sex: Sex = left_person_sex
        self._right_person_sex: Sex = right_person_sex
        self._reverse: bool = reverse

    @property
    def name(self) -> str:
        return self._name

    def configure_left_person(self, person: Person) -> Person | None:
        if person.sex is None and self._left_person_sex is not None:
            person.sex = self._left_person_sex
            return person
        return None

    def configure_right_person(self, person: Person) -> Person | None:
        if person.sex is None and self._right_person_sex is not None:
            person.sex = self._right_person_sex
            return person
        return None

    def to_relationship_definition_direction(self, left_person: Person, right_person: Person) -> (Person, Person):
        if self._reverse:
            return right_person, left_person
        return left_person, right_person


class RelationshipDefinition:
    def __init__(
        self,
        name: str,
        aliases: list[RelationshipAlias] = None,
        person_left_repr: str = None,
        person_right_repr: str = None,
        directional: bool = False,
    ) -> None:
        self._name: str = name
        self._person_left_repr: str = name if person_left_repr is None else person_left_repr
        self._person_right_repr: str = name if person_right_repr is None else person_right_repr
        self._aliases: list[RelationshipAlias] = [] if aliases is None else aliases[:]
        self._directional: bool = directional

    @property
    def name(self) -> str:
        return self._name

    @property
    def aliases(self) -> list[RelationshipAlias]:
        return self._aliases

    @property
    def directional(self) -> bool:
        return self._directional

    def left_repr(self, person: Person) -> str:
        return self._person_left_repr

    def right_repr(self, person: Person) -> str:
        return self._person_right_repr

    def __repr__(self) -> str:
        return self._name


parent_enfant = RelationshipDefinition(
    name="Parent/Enfant",
    aliases=[
        RelationshipAlias("père de", left_person_sex=MALE),
        RelationshipAlias("mère de", left_person_sex=FEMALE),
        RelationshipAlias("fils de", left_person_sex=MALE, reverse=True),
        RelationshipAlias("fille de", left_person_sex=FEMALE, reverse=True),
        RelationshipAlias("parent de"),
        RelationshipAlias("enfant de", reverse=True),
    ],
    person_left_repr="parent",
    person_right_repr="enfant",
    directional=True,
)

copain_copine = RelationshipDefinition(
    name="Copain/Copine",
    aliases=[
        RelationshipAlias("copain de", left_person_sex=MALE),
        RelationshipAlias("copine de", left_person_sex=FEMALE),
    ],
    person_left_repr="copain",
    person_right_repr="copain",
)

relationship_definitions: list[RelationshipDefinition] = [parent_enfant, copain_copine]


class Relationship:
    def __init__(self, person_left: Person, person_right: Person, definition: RelationshipDefinition) -> None:
        """
        A RelationshipDefinition has a default direction. Left and right designate People in the direction of this
        default direction.
        """
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
