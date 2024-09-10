import io
import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Callable

from pylms.core import Person, Relationship, RelationshipAlias, RelationshipDefinition
import pylms.pylms
from pylms.pylms import IOs, EventListener
from pylms.pylms import list_persons, search_persons, store_person


class TkApp:
    def __init__(self, window: tk.Tk):
        super().__init__()

        self._window = window
        self._entry_text: tk.StringVar = tk.StringVar()
        self._entry = tk.Entry(self._window, textvariable=self._entry_text)
        self._text_area: ScrolledText = ScrolledText(self._window)
        self._configure_text_area()

    def init_ui(self):
        self._window.title("PyLMS")

        self._entry.bind("<Return>", self._hit_enter)
        self._entry.focus_set()

        self._entry.pack()
        self._text_area.pack()

    def _configure_text_area(self) -> None:
        self._text_area.configure(state="disabled")

    def _is_empty(self):
        """source: https://stackoverflow.com/a/38541846"""
        return self._text_area.compare("end-1c", "==", "1.0")

    def _execute_text_area_edit_action(self, action: Callable[[tk.Text], None]) -> None:
        """
        Execute any "edit" action on self.textarea after putting it back to normal state, to allow the edit action
        to have effect, and they restore it to "disabled" state
        """
        self._text_area.configure(state="normal")
        action(self._text_area)
        self._text_area.configure(state="disabled")

    def write_line(self, *s: any) -> None:
        prefix = "" if self._is_empty() else "\n"
        self._execute_text_area_edit_action(lambda ta: ta.insert(tk.END, prefix + " ".join(map(str, s))))

    def _clear(self):
        self._execute_text_area_edit_action(lambda ta: ta.delete(1.0, tk.END))

    def _hit_enter(self, *_: any) -> None:
        self._clear()
        text_input = self._entry_text.get().strip()

        if not text_input:
            self.write_line("list_person()...")
            list_persons()
            return

        create_prefix = "create"
        if text_input.startswith(create_prefix):
            args = text_input[len(create_prefix) :].strip().split()
            match len(args):
                case 0:
                    self.write_line("Too few arguments (0)")
                case 1:
                    self.write_line(f"store_person(firstname={args[0]})")
                    store_person(firstname=args[0])
                case 2:
                    self.write_line(f"store_person(firstname={args[0]}, lastname={args[1]})")
                    store_person(firstname=args[0], lastname=args[1])
                case _ as args_count:
                    self.write_line(f"Too many arguments ({args_count})")
        else:
            self.write_line(f"search_persons({text_input})...")
            search_persons(text_input)


class GuiIOs(IOs):
    def __init__(self, gui_manager: TkApp):
        self.gui_manager: TkApp = gui_manager

    def _show_relationship(self, person: Person, relationship: Relationship) -> None:
        other = relationship.right if relationship.left == person else relationship.left
        self.gui_manager.write_line(f"    -> {relationship.repr_for(person)} ({other.person_id}) {other}")

    def show_person(self, person: Person) -> None:
        created = person.created
        self.gui_manager.write_line(
            f"({person.person_id})",
            f" {person.sex.name}" if person.sex is not None else "",
            person,
            f"({created.year}-{created.month}-{created.day} {created.hour}-{created.minute}-{created.second})",
        )
        if person.tags:
            self.gui_manager.write_line("     " + ", ".join(person.tags))

    def list_persons(self, resolved_persons: list[(Person, list[Relationship])]) -> None:
        for person, rls in sorted(resolved_persons, key=lambda t: t[0].person_id):
            self.show_person(person)
            for rl in rls:
                self._show_relationship(person, rl)

    def select_person(self, persons: list[Person]) -> Person | None:
        raise RuntimeError("select_person should not have been called")

    def update_person(self, person_to_update: Person) -> Person:
        raise RuntimeError("update_person should not have been called")


class GuiEventListener(EventListener):
    def __init__(self, tk_app: TkApp):
        self.tk_app: TkApp = tk_app

    def creating_person(self, person: Person) -> None:
        self.tk_app.write_line(f"Create Person {person}.")

    def deleting_person(self, person_to_delete: Person) -> None:
        raise RuntimeError("deleting_person should not have been called")

    def creating_link(self, rl_definition: RelationshipDefinition, person_left: Person, person_right: Person) -> None:
        raise RuntimeError("creating_link should not have been called")

    def configured_from_alias(self, person: Person, alias: RelationshipAlias) -> None:
        raise RuntimeError("configured_from_alias should not have been called")

    def deleting_relationship(self, relationship, person: Person | None) -> None:
        raise RuntimeError("deleting_relationship should not have been called")


class GuiLogger:
    def __init__(self, gui_manager: TkApp):
        self.gui_manager: TkApp = gui_manager
        self._handler: logging.StreamHandler | None = None

    def configure(self):
        class Foo(io.TextIOBase):
            def __init__(self, tk_app: TkApp):
                self.tk_app: TkApp = tk_app

            def write(self, __s):
                self.tk_app.write_line(__s)

        self._handler = logging.StreamHandler(stream=Foo(self.gui_manager))
        self._handler.setLevel(logging.INFO)

        logger = logging.getLogger("pylms.pylms")
        logger.setLevel(logging.INFO)
        logger.addHandler(self._handler)

    def unconfigure(self):
        logger = logging.getLogger("pylms.pylms")
        if self._handler:
            logger.removeHandler(self._handler)
            del self._handler


def _main(window: tk.Tk):
    logging.basicConfig(level=logging.WARN)

    tk_app = TkApp(window)

    pylms.pylms.ios = GuiIOs(tk_app)
    pylms.pylms.events = GuiEventListener(tk_app)
    gui_logger = GuiLogger(tk_app)
    try:
        gui_logger.configure()

        tk_app.init_ui()

        window.mainloop()
    finally:
        # nothing is happening after this line so the cleanup below is useless to the program
        # however, it saves lots of noise in tests where logging with logger "pylms.pylms" fails because the textarea
        # has been destroyed
        gui_logger.unconfigure()


def main():
    _main(tk.Tk())


if __name__ == "__main__":
    main()
