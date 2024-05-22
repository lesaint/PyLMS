import pylms.core
from pylms.core import Person
from pylms.pylms import list_persons, store_person, update_person, search_persons, delete_person, link_persons
from pylms.pylms import LinkRequest, Relationship, RelationshipDefinition, RelationshipAlias
from pylms.core import parent_enfant, copain_copine, MALE, FEMALE
from unittest.mock import patch, call
from pytest import mark


class TestStorePerson:

    @patch("builtins.print")
    @patch("pylms.pylms.storage.read_persons")
    @patch("pylms.pylms.storage.store_persons")
    def test_no_existing_person(self, mock_store_persons, mock_read_persons, mock_print):
        firstname = "John"
        lastname = "Doe"
        mock_read_persons.return_value = []

        store_person(firstname=firstname, lastname=lastname)

        mock_read_persons.assert_called_with()
        assert mock_read_persons.call_count == 1
        mock_store_persons.assert_called_with([Person(0, firstname=firstname, lastname=lastname)])
        assert mock_store_persons.call_count == 1
        mock_print.assert_called_with(f"Create Person {firstname} {lastname}.")
        assert mock_print.call_count == 1

    @patch("builtins.print")
    @patch("pylms.pylms.storage.read_persons")
    @patch("pylms.pylms.storage.store_persons")
    def test_only_firstname_and_add_to_existing_persons(self, mock_store_persons, mock_read_persons, mock_print):
        firstname = "Mike"
        lastname = "Jagger"
        persons = [Person(7, "Richard", "Brownsome")]

        mock_read_persons.return_value = persons

        store_person(firstname=firstname, lastname=lastname)

        mock_read_persons.assert_called_with()
        assert mock_read_persons.call_count == 1
        mock_store_persons.assert_called_with([Person(8, firstname=firstname, lastname=lastname)] + persons)
        assert mock_store_persons.call_count == 1
        mock_print.assert_called_with(f"Create Person {firstname} {lastname}.")
        assert mock_print.call_count == 1

    @patch("builtins.print")
    @patch("pylms.pylms.storage.read_persons")
    @patch("pylms.pylms.storage.store_persons")
    def test_only_firstname_no_existing_person(self, mock_store_persons, mock_read_persons, mock_print):
        firstname = "John"
        mock_read_persons.return_value = []

        store_person(firstname=firstname)

        mock_read_persons.assert_called_with()
        assert mock_read_persons.call_count == 1
        mock_store_persons.assert_called_with([Person(person_id=0, firstname=firstname)])
        assert mock_store_persons.call_count == 1
        mock_print.assert_called_with(f"Create Person {firstname}.")
        assert mock_print.call_count == 1

    @patch("builtins.print")
    @patch("pylms.pylms.storage.read_persons")
    @patch("pylms.pylms.storage.store_persons")
    def test_only_firstname_and_add_to_existing_persons(self, mock_store_persons, mock_read_persons, mock_print):
        firstname = "John"
        persons = [Person(2, "Paul", "Valérie")]

        mock_read_persons.return_value = persons

        store_person(firstname=firstname)

        mock_read_persons.assert_called_with()
        assert mock_read_persons.call_count == 1
        mock_store_persons.assert_called_with([Person(3, firstname=firstname)] + persons)
        assert mock_store_persons.call_count == 1
        mock_print.assert_called_with(f"Create Person {firstname}.")
        assert mock_print.call_count == 1


class TestListPersons:
    @patch("pylms.pylms.ios.list_persons")
    @patch("pylms.pylms.storage.read_relationships")
    @patch("pylms.pylms.storage.read_persons")
    def test_empty_storage(self, mock_read_persons, mock_read_relationships, mock_list_persons):
        mock_read_persons.return_value = []

        list_persons()

        mock_read_persons.assert_called_once_with()
        assert mock_read_relationships.call_count == 0
        mock_list_persons.assert_called_once_with([])

    @patch("pylms.pylms.ios.list_persons")
    @patch("pylms.pylms.storage.read_relationships", return_value=[])
    @patch("pylms.pylms.storage.read_persons")
    def test_persons_but_no_relationships(
        self,
        mock_read_persons,
        mock_read_relationships,
        mock_list_persons,
    ):
        persons = [
            Person(3, "Bob"),
            Person(1, "Seb", "King"),
            Person(2, "Mario", "Bros"),
        ]

        mock_read_persons.return_value = persons

        list_persons()

        mock_read_persons.assert_called_once_with()
        mock_read_relationships.assert_called_once_with(persons)
        mock_list_persons.assert_called_once_with([(person, []) for person in persons])


class TestUpdatePerson:

    @patch("pylms.pylms.storage")
    @patch("pylms.pylms._select_person")
    def test_no_person_selected(self, mock_select, mock_storage):
        mock_select.return_value = None

        update_person("p")

        mock_select.assert_called_once_with("p")
        assert mock_storage.call_count == 0

    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.ios.update_person")
    @patch("pylms.pylms._select_person")
    def test_single_person(self, mock_select, mock_update_person, mock_storage):
        person = Person(1, "foo", "bar")
        updated_person = Person(234, "donut", "acme")
        mock_select.return_value = person
        mock_update_person.return_value = updated_person

        update_person("p")

        mock_select.assert_called_once_with("p")
        mock_update_person.assert_called_once_with(person)
        mock_storage.update_person.assert_called_once_with(updated_person)

    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.ios.update_person")
    @patch("pylms.pylms._select_person")
    def test_out_of_several(self, mock_select, mock_update_person, mock_storage):
        person2 = Person(2, "foo", "bar")
        updated_person = Person(888, "donut", "acme")
        mock_select.return_value = person2
        mock_update_person.return_value = updated_person

        update_person("p")

        mock_select.assert_called_once_with("p")
        mock_update_person.assert_called_once_with(person2)
        mock_storage.update_person.assert_called_once_with(updated_person)


class TestDeletePerson:

    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.events")
    @patch("pylms.pylms._select_person")
    def test_delete_person(self, mock_select, mock_events, mock_storage):
        person1 = Person(1, "foo", "bar")
        person2 = Person(2, "foo", "bar")
        person3 = Person(3, "foo", "bar")
        mock_select.return_value = person3
        mock_storage.read_persons.return_value = [person3, person2, person1]
        mock_storage.read_relationships.return_value = []

        delete_person("p")

        mock_select.assert_called_once_with("p")
        mock_events.deleting_person.assert_called_once_with(person3)
        assert mock_events.deleting_relationship.call_count == 0
        mock_storage.read_persons.assert_called_once_with()
        mock_storage.read_relationships.assert_called_once_with([person3, person2, person1])
        mock_storage.store_persons.assert_called_once_with([person2, person1])
        mock_storage.store_relationships.assert_called_once_with([])

    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.events")
    @patch("pylms.pylms._select_person")
    def test_delete_person_with_relationship(self, mock_select, mock_events, mock_storage):
        person1 = Person(1, "foo", "bar")
        person2 = Person(2, "foo", "bar")
        person3 = Person(3, "foo", "bar")
        rld1 = RelationshipDefinition("rld1")
        rld2 = RelationshipDefinition("rld2")
        rl1 = Relationship(person1, person2, rld1)
        rl2 = Relationship(person2, person1, rld2)
        rl3 = Relationship(person2, person3, rld1)
        rl4 = Relationship(person3, person2, rld2)
        mock_select.return_value = person3
        mock_storage.read_persons.return_value = [person3, person2, person1]
        mock_storage.read_relationships.return_value = [rl4, rl2, rl3, rl1]

        delete_person("p")

        mock_select.assert_called_once_with("p")
        mock_events.deleting_person.assert_called_once_with(person3)
        mock_events.deleting_relationship.has_calls([call(rl4, person3), call(rl3, person3)])
        mock_storage.read_persons.assert_called_once_with()
        mock_storage.read_relationships.assert_called_once_with([person3, person2, person1])
        mock_storage.store_persons.assert_called_once_with([person2, person1])
        mock_storage.store_relationships.assert_called_once_with([rl2, rl1])

    @patch("builtins.print")
    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.events")
    @patch("pylms.pylms.ios.show_person")
    @patch("pylms.pylms._select_person")
    def test_no_person_selected_to_delete(self, mock_select, mock_show_person, mock_events, mock_storage, mock_print):
        mock_select.return_value = None

        delete_person("p")

        mock_select.assert_called_once_with("p")
        assert mock_show_person.call_count == 0
        assert mock_events.deleting_person.call_count == 0
        assert mock_events.deleting_relationship.call_count == 0
        assert mock_storage.call_count == 0
        assert mock_print.call_count == 0


relationship_definition_1 = RelationshipDefinition("22", aliases=[RelationshipAlias("22a")])
person_1 = Person(person_id=1, firstname="Jane")
person_2 = Person(person_id=2, firstname="Tarzan")
person_3 = Person(person_id=3, firstname="Jane2")
person_4 = Person(person_id=4, firstname="Tarzan2")
person_5 = Person(person_id=3, firstname="Jane3")
person_6 = Person(person_id=4, firstname="Tarzan3")


class TestLinkPerson:

    def test_empty_request(self):
        assert link_persons("") is None

    @patch("pylms.pylms._parse_nl_link_request", return_value=None)
    def test_no_relationship_definition_match(self, mock_parse_link_request):
        request = "p"

        assert link_persons(request) is None

        mock_parse_link_request.assert_called_once_with(request)

    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.events")
    @patch.object(
        relationship_definition_1.aliases[0], "to_relationship_definition_direction", return_value=(person_5, person_6)
    )
    @patch.object(relationship_definition_1.aliases[0], "configure_right_person", return_value=person_4)
    @patch.object(relationship_definition_1.aliases[0], "configure_left_person", return_value=person_3)
    @patch("pylms.pylms._select_person", side_effect=[person_1, person_2])
    @patch(
        "pylms.pylms._parse_nl_link_request",
        return_value=LinkRequest(
            left_person_pattern="foo",
            right_person_pattern="bar",
            definition=relationship_definition_1,
            alias=relationship_definition_1.aliases[0],
        ),
    )
    def test_sends_events_and_store_updated_persons(
        self,
        mock_link_request,
        mock_select_person,
        mock_configure_left,
        mock_configure_right,
        mock_to_rld_direction,
        mock_events,
        mock_storage,
    ):
        mock_storage.read_persons.return_value = []

        request = "p"

        assert link_persons(request) is None

        mock_link_request.assert_called_once_with(request)
        mock_select_person.has_calls([call(person_1), call(person_2)])
        mock_configure_left.assert_called_once_with(person_1)
        mock_configure_right.assert_called_once_with(person_2)
        mock_events.configured_from_alias.has_calls([call(person_3), call(person_4)])
        mock_to_rld_direction.assert_called_once_with(left_person=person_3, right_person=person_4)
        mock_events.creating_link.assert_called_once_with(relationship_definition_1, person_5, person_6)
        mock_storage.read_persons.assert_called_once_with()
        mock_storage.read_relationships.assert_called_once_with([])

        class ExpectedRelationship:
            def __eq__(self, other: Relationship):
                return (
                    other.left == person_5 and other.right == person_6 and other.definition == relationship_definition_1
                )

        mock_storage.store_relationships([ExpectedRelationship()])


class TestSearchPersonByWord:

    @patch("pylms.pylms.logger")
    @patch("pylms.pylms._search_persons")
    def test_only_info_log_if_no_match(self, mock_search_persons, mock_logger):
        mock_search_persons.return_value = []
        pattern = "p"

        search_persons(pattern)

        mock_search_persons.assert_called_once_with(pattern)
        mock_logger.info.assert_called_once_with(f'No match for "{pattern}".')

    @patch("pylms.pylms.ios")
    @patch("pylms.pylms.storage")
    @patch("pylms.pylms.logger")
    @patch("pylms.pylms._search_persons")
    def test_list_persons_limited_to_the_person_matching_pattern(
        self,
        mock_search_persons,
        mock_logger,
        mock_storage,
        mock_ios,
    ):
        rls = [
            Relationship(person_1, person_2, relationship_definition_1),
            Relationship(person_2, person_3, relationship_definition_1),
            Relationship(person_2, person_4, relationship_definition_1),
            Relationship(person_3, person_4, relationship_definition_1),
            Relationship(person_3, person_1, relationship_definition_1),
            Relationship(person_4, person_1, relationship_definition_1),
        ]
        persons = [person_1, person_2, person_3, person_4]

        mock_search_persons.return_value = [person_1]
        mock_storage.read_persons.return_value = persons
        mock_storage.read_relationships.return_value = rls
        pattern = "p"

        search_persons(pattern)

        mock_search_persons.assert_called_once_with(pattern)
        assert mock_logger.call_count == 0
        mock_storage.read_persons.assert_called_once_with()
        mock_storage.read_relationships.assert_called_once_with(persons)
        mock_ios.list_persons.assert_called_once_with([(person_1, [rls[0], rls[4], rls[5]])])


class TestSearchPersonByRelationship:
    john = Person(person_id=1, firstname="John")
    peter = Person(person_id=2, firstname="Peter")
    emma = Person(person_id=3, firstname="Emma", sex=FEMALE)
    carine = Person(person_id=4, firstname="Carine")
    tom = Person(person_id=5, firstname="Tom", sex=MALE)
    bill = Person(person_id=6, firstname="Bill")
    dona = Person(person_id=7, firstname="Dona", sex=FEMALE)
    elmer = Person(person_id=8, firstname="Elmer", sex=MALE)
    princess = Person(person_id=9, firstname="Princess", sex=FEMALE)
    persons = [john, peter, emma, carine, tom, bill, dona, elmer, princess]
    relationships = [
        Relationship(person_left=john, person_right=peter, definition=parent_enfant),
        Relationship(person_left=john, person_right=emma, definition=parent_enfant),
        Relationship(person_left=emma, person_right=carine, definition=copain_copine),
        Relationship(person_left=john, person_right=tom, definition=parent_enfant),
        Relationship(person_left=dona, person_right=bill, definition=parent_enfant),
        Relationship(person_left=elmer, person_right=bill, definition=parent_enfant),
        Relationship(person_left=princess, person_right=bill, definition=parent_enfant),
    ]

    @patch("pylms.pylms.ios")
    @patch("pylms.pylms.storage")
    @mark.parametrize(
        ("search_request", "expected"),
        [
            ("parent de emma", [(john, [relationships[0], relationships[1],relationships[3]])]),
            (
                "enfant de John",
                [(peter, [relationships[0]]), (emma, [relationships[1], relationships[2]]), (tom, [relationships[3]])],
            ),
            ("fille de John", [(emma, [relationships[1], relationships[2]])]),
            ("fils de John", [(tom, [relationships[3]])]),
            ("mère de bill", [(dona, [relationships[4]]), (princess, [relationships[6]])]),
            ("père de bill", [(elmer, [relationships[5]])]),
            ("parent de bill", [(dona, [relationships[4]]), (elmer, [relationships[5]]), (princess, [relationships[6]])]),
        ],
    )
    def test_search_successful(self, mock_storage, mock_ios, search_request, expected):
        mock_storage.read_persons.return_value = self.persons
        mock_storage.read_relationships.return_value = self.relationships

        search_persons(search_request)

        # duplicate calls because: 1 for finding the persons, 1 to display them.
        # Could be only one call but this optimization is deemed minor
        mock_storage.read_persons.assert_has_calls([call(), call()])
        mock_storage.read_relationships.assert_has_calls([call(self.persons), call(self.persons)])
        mock_ios.list_persons.assert_called_once_with(expected)

    @patch("pylms.pylms.ios")
    @patch("pylms.pylms.logger")
    @patch("pylms.pylms.storage")
    @mark.parametrize(
        "search_request",
        [
            "père de emma",
            "mère de peter",
            "parent de carine",
            "fils de Elmer",
            "fils de Dona",
            "fils de princess"
        ],
    )
    def test_no_matching_relationship(self, mock_storage, mock_logger, mock_ios, search_request):
        mock_storage.read_persons.return_value = self.persons
        mock_storage.read_relationships.return_value = self.relationships

        search_persons(search_request)

        # 1 call to find the persons
        mock_storage.read_persons.assert_called_once_with()
        mock_storage.read_relationships.assert_called_once_with(self.persons)
        mock_logger.info.assert_called_once_with(f'No match for "{search_request}".')
        assert mock_ios.list_persons.call_count == 0

    @patch("pylms.pylms.ios")
    @patch("pylms.pylms.logger")
    @patch("pylms.pylms.storage")
    @mark.parametrize(
        "search_request",
        [
            "foo bar donut",
            "mere de bill",  # alias is not yet matched regardless of accentuated chars
        ],
    )
    def test_no_relationship_found_in_request(self, mock_storage, mock_logger, mock_ios, search_request):
        mock_storage.read_persons.return_value = self.persons
        mock_storage.read_relationships.return_value = self.relationships

        search_persons(search_request)

        # 1 call to find the persons
        mock_storage.read_persons.assert_called_once_with()
        assert mock_storage.read_relationships.call_count == 0
        mock_logger.info.assert_called_once_with(f'No match for "{search_request}".')
        assert mock_ios.list_persons.call_count == 0
