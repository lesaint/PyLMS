"""
How to write unit tests for Tkinter was strongly inspired from this test in cpython's repository:
https://github.com/python/cpython/blob/055c739536ad63b55ad7cd0b91ccacc33064fe11/Lib/test/test_ttk/test_widgets.py
"""

import logging
import unittest
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from unittest.mock import patch
from typing import TypeVar, Type
from datetime import datetime
from parameterized import parameterized

import pytest

import pylms.pylms
from pylms.pylms import IOs, EventListener
from pylms.gui import TkApp, GuiIOs, GuiEventListener
from pylms.gui import _main
from pylms.core import Person, Relationship, RelationshipDefinition

# a single TK session is used for all tests in this module
# tests are expected to clean up after themselves with _tear_down()
window: tk.Tk


AnyWidget = TypeVar("AnyWidget", bound=tk.Misc)


def _find_widget(parent: tk.Misc, widget_type: Type[AnyWidget]) -> AnyWidget | None:
    """
    Find the first widget of the specific type, crawling the tree of widgets in sibling-first order
    """
    for c in parent.children.values():
        if isinstance(c, widget_type):
            return c
        if c.children:
            return _find_widget(c, widget_type)

    return None


def _tk_initial_update():
    # force focus on the window (may not be automatically given by the window manager, eg. under xvfb)
    window.focus_force()
    window.update_idletasks()
    window.update()


def _get_text(textarea: tk.Text) -> str:
    # ensure any pending change to the textarea has been processed
    textarea.update()
    return textarea.get("1.0", "end-1c")


def _tear_down():
    """
    Run any leftover action and remove any children before running the next test.
    Intended to be called from TestCases' tearDown() method
    """
    window.update_idletasks()
    for c in list(window.children.values()):
        c.destroy()


def setUpModule():
    """Runs before any test and create the one TK that will be used by all tests"""
    global window
    window = tk.Tk()


def tearDownModule():
    """
    Clean up after all tests have run: run any leftover action and destroy the Tk.
    Safety net before executing tests in other modules.
    """
    global window
    window.update_idletasks()
    window.destroy()
    del window


# mock mainloop to prevent showing the window and blocking until user has interactions with it
@patch("pylms.gui.tk.Tk.mainloop")
class TestMain(unittest.TestCase):
    def tearDown(self):
        _tear_down()

    def test_main_starts_tk_app(self, mock_tk_app_mainloop):
        _main(window)

        mock_tk_app_mainloop.assert_called_once_with()

    def test_main_binds_ios_and_event(self, mock_tk_app_mainloop):
        _main(window)

        assert isinstance(pylms.pylms.ios, GuiIOs)
        assert isinstance(pylms.pylms.events, GuiEventListener)

    @patch("pylms.gui.TkApp.init_ui")
    def test_main_inits_ui(self, mock_init_ui, mock_tk_app_mainloop):
        _main(window)

        mock_init_ui.assert_called_once_with()


class TestEventListener(unittest.TestCase):
    def setUp(self):
        # mock mainloop to prevent showing the window and blocking until user has interactions with it
        with patch("pylms.gui.tk.Tk.mainloop"):
            _main(window)
        _tk_initial_update()

        self._text_area: ScrolledText = _find_widget(window, ScrolledText)
        self._under_test: EventListener = pylms.pylms.events

    def tearDown(self):
        _tear_down()

        del self._under_test
        del self._text_area

    def _get_textarea_text(self) -> str:
        return _get_text(textarea=self._text_area)

    def test_creating_person_prints_to_textarea(self):
        person = Person(person_id=1, firstname="John")

        self._under_test.creating_person(person)
        self._text_area.update()

        assert self._get_textarea_text() == f"Create Person {person}."

    def test_deleting_person_not_supported(self):
        with pytest.raises(RuntimeError, match="deleting_person should not have been called"):
            self._under_test.deleting_person(None)

    def test_creating_link_not_supported(self):
        with pytest.raises(RuntimeError, match="creating_link should not have been called"):
            self._under_test.creating_link(None, None, None)

    def test_configured_from_alias_not_supported(self):
        with pytest.raises(RuntimeError, match="configured_from_alias should not have been called"):
            self._under_test.configured_from_alias(None, None)

    def test_deleting_relationship_not_supported(self):
        with pytest.raises(RuntimeError, match="deleting_relationship should not have been called"):
            self._under_test.deleting_relationship(None, None)


class TestIOs(unittest.TestCase):
    person1 = Person(person_id=12, firstname="Boo", lastname="Bip", created=datetime(2024, 4, 5, 12, 41, 9))
    person2 = Person(person_id=5, firstname="Acme")
    person_with_tags = Person(person_id=119, firstname="Mat", created=datetime(2024, 7, 24, 15, 35, 41))
    person_with_tags.tags = ["toto", "a trooper"]
    rl_definition = RelationshipDefinition(name="related")

    def setUp(self):
        # mock mainloop to prevent showing the window and blocking until user has interactions with it
        with patch("pylms.gui.tk.Tk.mainloop"):
            _main(window)
        _tk_initial_update()

        self._text_area: ScrolledText = _find_widget(window, ScrolledText)
        self._under_test: IOs = pylms.pylms.ios

    def tearDown(self):
        _tear_down()

        del self._under_test
        del self._text_area

    def _get_textarea_text(self) -> str:
        return _get_text(textarea=self._text_area)

    def test_show_person_prints_to_textarea(self):
        self._under_test.show_person(self.person1)

        assert self._get_textarea_text() == "(12)  Boo Bip (2024-4-5 12-41-9)"

    def test_show_person_with_tags_prints_to_textarea(self):
        self._under_test.show_person(self.person_with_tags)

        assert self._get_textarea_text() == "(119)  Mat (2024-7-24 15-35-41)\n     toto, a trooper"

    def test_list_persons_prints_to_textarea(self):
        self._under_test.list_persons([(self.person1, [Relationship(self.person1, self.person2, self.rl_definition)])])

        assert self._get_textarea_text() == "(12)  Boo Bip (2024-4-5 12-41-9)\n    -> related (5) Acme"

    def test_list_persons_prints_tags_to_textarea(self):
        self._under_test.list_persons([(self.person_with_tags, [])])

        assert self._get_textarea_text() == "(119)  Mat (2024-7-24 15-35-41)\n     toto, a trooper"

    def test_select_person_not_supported(self):
        with pytest.raises(RuntimeError, match="select_person should not have been called"):
            self._under_test.select_person(None)

    def test_update_person_not_supported(self):
        with pytest.raises(RuntimeError, match="update_person should not have been called"):
            self._under_test.update_person(None)


@patch("pylms.gui.tk.Tk.mainloop")
class TestLogging(unittest.TestCase):

    def setUp(self):
        self._under_test: logging.Logger = logging.getLogger("pylms.pylms")

    def tearDown(self):
        print("in tearDown")
        _tear_down()

        del self._under_test

    @staticmethod
    def _get_textarea_text() -> str:
        return _get_text(textarea=_find_widget(window, ScrolledText))

    @parameterized.expand([logging.INFO, logging.WARN, logging.ERROR, logging.CRITICAL])
    def test_prints_to_textarea_logs_above_info(self, mock_mainloop, level):
        message = f"this is an {logging.getLevelName(level)} log"

        def do_some_log():
            self._under_test.log(level=level, msg=message)

        mock_mainloop.side_effect = do_some_log

        _main(window)
        _tk_initial_update()

        assert TestLogging._get_textarea_text() == message + "\n"

    @parameterized.expand([logging.DEBUG])
    def test_does_not_print_to_textarea_logs_below_info(self, mock_mainloop, level):
        message = f"this is an {logging.getLevelName(level)} log"

        def do_some_log():
            self._under_test.log(level=level, msg=message)

        mock_mainloop.side_effect = do_some_log

        _main(window)
        _tk_initial_update()

        assert len(TestLogging._get_textarea_text()) == 0


class TestGui(unittest.TestCase):
    def setUp(self):
        self._under_test: TkApp = TkApp(window)
        self._under_test.init_ui()
        _tk_initial_update()

        self._entry: tk.Entry = _find_widget(window, tk.Entry)
        self._text_area: ScrolledText = _find_widget(window, ScrolledText)

    def tearDown(self):
        _tear_down()

        del self._entry
        del self._text_area
        del self._under_test

    def _user_writes_to_entry(self, s: str) -> None:
        self._entry.delete(0, tk.END)
        self._entry.insert(0, s)
        self._entry.update()

    def _user_hits_return_on_entry(self):
        # force focus on the entry, otherwise events are not processed  (source https://stackoverflow.com/a/27604905)
        self._entry.focus_set()
        self._entry.update()

        self._entry.event_generate("<Return>")
        self._entry.update()

    def _get_textarea_text(self) -> str:
        return _get_text(textarea=self._text_area)

    def test_creates_entry_and_scrolledtext_and_focus_on_entry(self):
        assert self._entry is not None
        assert self._text_area is not None

    @patch("pylms.gui.list_persons")
    def test_runs_list_when_users_hits_return_on_empty_entry(self, mock_list_persons):
        self._user_hits_return_on_entry()

        assert self._get_textarea_text() == "list_person()..."
        mock_list_persons.assert_called_once_with()

    @patch("pylms.gui.search_persons")
    def test_runs_search_person_when_users_hits_return_with_non_empty_entry(self, mock_search_persons):
        some_text: str = "foo bar 42"
        self._user_writes_to_entry(some_text)
        self._user_hits_return_on_entry()

        assert self._get_textarea_text() == f"search_persons({some_text})..."
        mock_search_persons.assert_called_once_with(some_text)

    @patch("pylms.gui.store_person")
    def test_report_error_for_create_text_alone(self, mock_store_person):
        some_text: str = "create"
        self._user_writes_to_entry(some_text)
        self._user_hits_return_on_entry()

        assert self._get_textarea_text() == f"Too few arguments (0)"
        assert mock_store_person.call_count == 0

    @patch("pylms.gui.store_person")
    def test_report_error_for_create_text_and_3_words(self, mock_store_person):
        some_text: str = "create foo bar 2000"
        self._user_writes_to_entry(some_text)
        self._user_hits_return_on_entry()

        assert self._get_textarea_text() == f"Too many arguments (3)"
        assert mock_store_person.call_count == 0

    @patch("pylms.gui.store_person")
    def test_runs_store_person_for_create_text_and_1_word(self, mock_store_person):
        some_text: str = "create bar"
        self._user_writes_to_entry(some_text)
        self._user_hits_return_on_entry()

        assert self._get_textarea_text() == f"store_person(firstname=bar)"
        mock_store_person.assert_called_once_with(firstname="bar")

    @patch("pylms.gui.store_person")
    def test_runs_store_person_for_create_text_and_2_words(self, mock_store_person):
        some_text: str = "create bar donut"
        self._user_writes_to_entry(some_text)
        self._user_hits_return_on_entry()

        assert self._get_textarea_text() == f"store_person(firstname=bar, lastname=donut)"
        mock_store_person.assert_called_once_with(firstname="bar", lastname="donut")
