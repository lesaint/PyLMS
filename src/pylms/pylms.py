from pylms import storage
from pylms.core import Person, PersonIdGenerator
from pylms.core import relationship_definitions, RelationshipDefinition, Relationship, RelationshipAlias
from pylms.core import resolve_persons
from pylms.python_utils import require_not_none
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


ios: IOs | None = None
events: EventListener | None = None


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


class SearchRequest:
    def __init__(
        self,
        *,
        pattern: str,
        definition: RelationshipDefinition | None = None,
        alias: RelationshipAlias | None = None,
    ):
        self.pattern = require_not_none(pattern, "pattern can't be None")
        if (definition is None) != (alias is None):
            raise ValueError("Either both definition and alias must be provided or neither of them")
        self.definition: RelationshipDefinition | None = definition
        self.alias: RelationshipAlias | None = alias


class RelationshipPattern:
    def __init__(
        self,
        *,
        pattern_before: str | None,
        definition: RelationshipDefinition | None = None,
        alias: RelationshipAlias | None = None,
        pattern_after: str,
    ):
        """
        Neither pattern_before nor pattern_after are trimmed.
        """
        self.pattern_before: str | None = pattern_before
        self.definition: RelationshipDefinition | None = definition
        self.alias: RelationshipAlias | None = alias
        self.pattern_after: str | None = pattern_after


def _find_relationship_by_alias(
    definition: RelationshipDefinition, alias: RelationshipAlias, request: str
) -> RelationshipPattern | None:
    name = alias.name.lower()
    try:
        index = request.index(name)
        return RelationshipPattern(
            pattern_before=request[0:index],
            definition=definition,
            alias=alias,
            pattern_after=request[index + len(name) :],
        )
    except ValueError:
        return None


def _find_relationship_pattern(request: str) -> RelationshipPattern | None:
    if len(request) == 0:
        return None

    request: str = request.lower()

    for rl in relationship_definitions:
        for alias in rl.aliases:
            rl_pattern = _find_relationship_by_alias(rl, alias, request)
            if rl_pattern:
                return rl_pattern

    return None


def _parse_nl_link_request(natural_language_link_request: str) -> LinkRequest | None:
    rl_pattern = _find_relationship_pattern(natural_language_link_request)
    if rl_pattern is None:
        return None

    pattern_before = rl_pattern.pattern_before.strip() if rl_pattern.pattern_before else None
    pattern_after = rl_pattern.pattern_after.strip() if rl_pattern.pattern_after else None
    if not pattern_before or not pattern_after:
        logger.error("Unsupported link request: wrong number of person patterns")
        return None

    return LinkRequest(
        left_person_pattern=pattern_before,
        right_person_pattern=pattern_after,
        definition=rl_pattern.definition,
        alias=rl_pattern.alias,
    )


def _parse_search_request(search_request: str) -> SearchRequest | None:
    rl_pattern = _find_relationship_pattern(search_request)
    if rl_pattern is None:
        return SearchRequest(pattern=search_request)

    if rl_pattern.pattern_before:
        logger.error(f"Unsupported relationship search request has prefix: {rl_pattern.pattern_before}")
        return None

    return SearchRequest(
        pattern=rl_pattern.pattern_after.strip(), definition=rl_pattern.definition, alias=rl_pattern.alias
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


def _rl_match(search_request: SearchRequest, rl: Relationship) -> bool:
    """
    Test whether the provided Relationship match the SearchRequest.
    First, a matching relationship must have the same definition as the SearchRequest.
    Then, the SearchRequest can have a forward (eg. "Père de Peter")  or a reverse alias (eg. "Fils de John").
    In the former case, a matching relationship must have the _right_ person matching the pattern ("Peter"),
    in the later case a matching relationship must have the _left_ person matching the pattern ("John" this time).
    Finally, the alias in the SearchRequest can have a left person sex. If so, the person must also have the same sex.
    """
    if rl.definition != search_request.definition:
        return False

    person_to_match_pattern, person_to_match_sex = rl.right, rl.left
    if search_request.alias.reverse:
        person_to_match_pattern, person_to_match_sex = rl.left, rl.right
    if _search_match(search_request.pattern, person_to_match_pattern):
        expected_sex = search_request.alias.left_person_sex
        if expected_sex:
            return person_to_match_sex.sex == expected_sex
        return True

    return False


def _search_request_relationship(search_request: SearchRequest) -> list[Person]:
    persons = storage.read_persons()
    relationships = storage.read_relationships(persons)

    return [r.right if search_request.alias.reverse else r.left for r in relationships if _rl_match(search_request, r)]


def search_persons(search_request_string: str) -> None:
    search_request = _parse_search_request(search_request_string)

    if search_request.definition:
        person_hits = _search_request_relationship(search_request)
    else:
        person_hits = _search_persons(search_request_string)

    if not person_hits:
        logger.info(f'No match for "{search_request_string}".')
        return

    persons = storage.read_persons()

    resolved_persons = []
    if persons:
        relationships = storage.read_relationships(persons)

        def p_filter(p: Person) -> bool:
            return p in person_hits

        def rl_filter(p: Person, _: Relationship) -> bool:
            return p in person_hits

        resolved_persons = resolve_persons(
            persons=persons, relationships=relationships, person_filter=p_filter, relationship_filter=rl_filter
        )

    ios.list_persons(resolved_persons)
