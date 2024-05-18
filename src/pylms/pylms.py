from pylms import storage
from pylms.core import Person, PersonIdGenerator
from pylms.core import relationship_definitions, RelationshipDefinition, Relationship, RelationshipAlias
from pylms.core import resolve_persons
from abc import abstractmethod, ABC
import logging

logger = logging.getLogger(__name__)


class ExitPyLMS(BaseException):
    pass


class IOs(ABC):
    @abstractmethod
    def show_person(self, person: Person) -> None:
        pass

    @abstractmethod
    def list_persons(self, persons: list[(Person, list[Relationship])]) -> None:
        pass

    @abstractmethod
    def select_person(self, persons: list[Person]) -> Person | None:
        pass

    @abstractmethod
    def update_person(self, person_to_update: Person) -> Person:
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

    @abstractmethod
    def configured_from_alias(self, person: Person, alias: RelationshipAlias) -> None:
        pass

    @abstractmethod
    def deleting_relationship(self, relationship, person: Person | None) -> None:
        """
        :param relationship:
        :param person: the person of the relationship for whom it is being deleted
        """
        pass


ios: IOs
events: EventListener


def list_persons() -> None:
    persons = storage.read_persons()

    resolved_persons = []
    if persons:
        relationships = storage.read_relationships(persons)
        resolved_persons = resolve_persons(persons, relationships)

    ios.list_persons(resolved_persons)


def _select_person(pattern: str) -> Person | None:
    persons = _search_persons(pattern)
    if not persons:
        return

    if len(persons) == 1:
        return persons[0]

    return ios.select_person(persons)


def update_person(pattern: str) -> None:
    person_to_update: Person = _select_person(pattern)
    if not person_to_update:
        return

    updated_person = ios.update_person(person_to_update)

    storage.update_person(updated_person)


def _search_persons(pattern: str) -> list[Person]:
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
    person_to_delete: Person = _select_person(pattern)
    if not person_to_delete:
        return

    persons = storage.read_persons()
    relationships = storage.read_relationships(persons[:])

    events.deleting_person(person_to_delete)
    persons.remove(person_to_delete)
    for relationship in relationships[:]:
        if relationship.right == person_to_delete or relationship.left == person_to_delete:
            events.deleting_relationship(relationship, person_to_delete)
            relationships.remove(relationship)
    storage.store_persons(persons)
    storage.store_relationships(relationships)


class LinkRequest:
    def __init__(
        self,
        *,
        left_person_pattern: str,
        right_person_pattern: str,
        definition: RelationshipDefinition,
        alias: RelationshipAlias,
    ) -> None:
        self.left_person_pattern: str = left_person_pattern
        self.right_person_pattern: str = right_person_pattern
        self.definition: RelationshipDefinition = definition
        self.alias: RelationshipAlias = alias


def _find_relation_ship(natural_language_link_order: str) -> tuple[RelationshipDefinition, RelationshipAlias] | None:
    if len(natural_language_link_order) == 0:
        return None

    natural_language_link_order: str = natural_language_link_order.lower()

    for rl in relationship_definitions:
        for alias in rl.aliases:
            if alias.name.lower() in natural_language_link_order:
                return rl, alias

    return None


def _parse_nl_link_request(natural_language_link_request: str) -> LinkRequest | None:
    match = _find_relation_ship(natural_language_link_request)
    if match is None:
        return None
    definition, alias = match

    person_patterns = list(
        filter(lambda s: len(s) > 0, map(str.strip, natural_language_link_request.split(alias.name)))
    )
    patterns_count = len(person_patterns)
    if patterns_count != 2:
        logger.error(f"Unsupported link request: wrong number of person patterns ({patterns_count})")
        return None

    return LinkRequest(
        left_person_pattern=person_patterns[0],
        right_person_pattern=person_patterns[1],
        definition=definition,
        alias=alias,
    )


def _configure_person(alias: RelationshipAlias, person: Person, configure_method: str) -> Person:
    configure_person = getattr(alias, configure_method)
    configured_person = configure_person(person)
    if configured_person is None:
        return person
    events.configured_from_alias(alias=alias, person=configured_person)
    storage.update_person(person)
    return configured_person


def link_persons(natural_language_link_request: str) -> None:
    link_request = _parse_nl_link_request(natural_language_link_request)
    if link_request is None:
        return

    rq_person_left = _select_person(link_request.left_person_pattern)
    rq_person_right = _select_person(link_request.right_person_pattern)

    if rq_person_left is None:
        logger.info(f'No match for "{link_request.left_person_pattern}".')
    if rq_person_right is None:
        logger.info(f'No match for "{link_request.right_person_pattern}".')
    if rq_person_left is None or rq_person_right is None:
        return

    # configure persons from alias, if any
    person_left = _configure_person(link_request.alias, rq_person_left, "configure_left_person")
    person_right = _configure_person(link_request.alias, rq_person_right, "configure_right_person")

    rl_person_left, rl_person_right = link_request.alias.to_relationship_definition_direction(
        left_person=person_left, right_person=person_right
    )

    # create link
    events.creating_link(link_request.definition, rl_person_left, rl_person_right)
    persons = storage.read_persons()
    relationships = storage.read_relationships(persons)
    relationship = Relationship(
        person_left=rl_person_left,
        person_right=rl_person_right,
        definition=link_request.definition,
    )
    storage.store_relationships(relationships + [relationship])
