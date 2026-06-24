#!/usr/bin/env python3
import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Gdk

from state import GameState
from save_manager import JsonSaver
from screens import MainMenu, CharacterCreate, WelcomeScreen, LevelSelect, LoadSelect, BaseScreen

SLOT_DIR = os.path.expanduser("~/.vimtutor-plus")
SLOT_PATHS = [os.path.join(SLOT_DIR, f"slot_{i}.json") for i in range(3)]


def first_empty_slot() -> int | None:
    for i in range(3):
        if not os.path.exists(SLOT_PATHS[i]):
            return i
    return None


class App:
    def __init__(self):
        os.makedirs(SLOT_DIR, exist_ok=True)

        self.build_css()

        self.game = GameState()
        self._active_slot: int | None = None

        self.window = Gtk.Window()
        self.window.set_title("VimTutor+")
        self.window.set_size_request(900, 600)
        self.window.fullscreen()
        self.window.set_position(Gtk.WindowPosition.CENTER)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(300)
        self.window.add(self.stack)

        self.window.connect("key-press-event", self.on_key)
        self.window.connect("destroy", self.on_window_destroy)

        self._screens: dict[str, BaseScreen] = {}
        self._current: str | None = None
        self.register_screens()
        self.show_screen("main_menu")

        self.window.show_all()

    def register_screens(self):
        s_main = MainMenu(self.game, self.on_menu_action)
        s_create = CharacterCreate(self.game, self.on_name_confirmed, lambda: self.show_screen("main_menu"))
        s_welcome = WelcomeScreen(self.game, lambda: self.show_screen("level_select"), lambda: self.show_screen("main_menu"))
        s_levels = LevelSelect(self.game, lambda: self.show_screen("main_menu"))
        s_load = LoadSelect(self.game, self.on_slot_selected, self.on_slot_deleted, lambda: self.show_screen("main_menu"))

        self._register("main_menu", s_main)
        self._register("character_create", s_create)
        self._register("welcome", s_welcome)
        self._register("level_select", s_levels)
        self._register("load_select", s_load)

    def _register(self, name: str, screen):
        self._screens[name] = screen
        self.stack.add_named(screen, name)

    def show_screen(self, name: str):
        if self._current:
            self._screens[self._current].on_hide()
        self._current = name
        self._screens[name].on_show()
        self.stack.set_visible_child_name(name)

    # ── slot management ────────────────────────────────────────

    def _bind_slot(self, slot_index: int):
        saver = JsonSaver(SLOT_PATHS[slot_index])
        self.game.set_saver(saver)
        self._active_slot = slot_index

    def _delete_slot(self, slot_index: int):
        path = SLOT_PATHS[slot_index]
        if os.path.exists(path):
            os.remove(path)

    # ── navigation callbacks ───────────────────────────────────

    def on_menu_action(self, action):
        if action == "continue":
            self.show_screen("load_select")
        elif action == "new_game":
            idx = first_empty_slot()
            if idx is None:
                self.show_screen("load_select")
            else:
                self._bind_slot(idx)
                self.game.reset()
                self.show_screen("character_create")
        elif action == "options":
            pass
        elif action == "quit":
            self.window.destroy()

    def on_name_confirmed(self):
        self.game.save()
        self.show_screen("welcome")

    def on_slot_selected(self, slot_index: int):
        self._bind_slot(slot_index)
        self.show_screen("level_select")

    def on_slot_deleted(self, slot_index: int):
        self._delete_slot(slot_index)
        if self._active_slot == slot_index:
            self.game = GameState()
            self._active_slot = None

    # ── key dispatch ───────────────────────────────────────────

    def on_key(self, _widget, event):
        screen = self._screens.get(self._current)
        if screen and screen.handle_key(event):
            return True
        return False

    def on_window_destroy(self, *args):
        if self._active_slot is not None:
            self.game.save()
        Gtk.main_quit()

    # ── css ────────────────────────────────────────────────────

    def build_css(self):
        provider = Gtk.CssProvider()
        css = b"""
            window, .background {
                background-color: #0a0a0f;
            }
        """
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def run(self):
        Gtk.main()


if __name__ == "__main__":
    App().run()
