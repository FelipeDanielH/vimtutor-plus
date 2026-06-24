#!/usr/bin/env python3
import os
import json
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Gdk

from state import GameState
from save_manager import JsonSaver
from screens import MainMenu, CharacterCreate, IntroScreen, GameScreen, LoadSelect, BaseScreen

SLOT_DIR = os.path.expanduser("~/.vimtutor-plus")
SLOT_PATHS = [os.path.join(SLOT_DIR, f"slot_{i}.json") for i in range(3)]
LAST_SLOT_PATH = os.path.join(SLOT_DIR, "last_slot.txt")


def first_empty_slot() -> int | None:
    for i in range(3):
        if not os.path.exists(SLOT_PATHS[i]):
            return i
    return None


def _read_last_slot() -> int | None:
    try:
        with open(LAST_SLOT_PATH) as f:
            val = int(f.read().strip())
            if 0 <= val < 3:
                return val
    except (OSError, ValueError):
        pass
    return None


def _write_last_slot(index: int):
    with open(LAST_SLOT_PATH, "w") as f:
        f.write(str(index))


def _slot_has_name(index: int) -> bool:
    path = SLOT_PATHS[index]
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            return bool(json.load(f).get("player", {}).get("name", ""))
    except (OSError, json.JSONDecodeError):
        return False


class App:
    def __init__(self):
        os.makedirs(SLOT_DIR, exist_ok=True)
        self._clean_empty_slots()

        self.build_css()

        self.game = GameState()
        self._active_slot: int | None = None
        self._pending_slot: int | None = None

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

    def _clean_empty_slots(self):
        for path in SLOT_PATHS:
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        d = json.load(f)
                    if not d.get("player", {}).get("name", ""):
                        os.remove(path)
                except (OSError, json.JSONDecodeError):
                    os.remove(path)

    def register_screens(self):
        s_main = MainMenu(self.game, self.on_menu_action)
        s_create = CharacterCreate(self.game, self.on_name_confirmed, self._on_create_back)
        s_intro = IntroScreen(self.game, self._on_intro_done)
        s_load = LoadSelect(self.game, self.on_slot_selected, self.on_slot_deleted, lambda: self.show_screen("main_menu"))
        s_game = GameScreen(self.game, 1, self.on_level_complete, lambda: self.show_screen("main_menu"))

        self._register("main_menu", s_main)
        self._register("character_create", s_create)
        self._register("intro", s_intro)
        self._register("load_select", s_load)
        self._register("game_screen", s_game)

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

    def _on_create_back(self):
        self._pending_slot = None
        self.show_screen("main_menu")

    def _delete_slot(self, slot_index: int):
        path = SLOT_PATHS[slot_index]
        if os.path.exists(path):
            os.remove(path)

    # ── navigation callbacks ───────────────────────────────────

    def on_menu_action(self, action):
        if action == "continue":
            last = _read_last_slot()
            if last is not None and _slot_has_name(last):
                self._bind_slot(last)
                self._show_intro_or_skip()
            else:
                self.show_screen("load_select")
        elif action == "load_game":
            self.show_screen("load_select")
        elif action == "new_game":
            idx = first_empty_slot()
            if idx is None:
                self.show_screen("load_select")
            else:
                self._pending_slot = idx
                self.game = GameState()
                self._screens["character_create"]._gs = self.game
                self.show_screen("character_create")
        elif action == "options":
            pass
        elif action == "quit":
            self.window.destroy()

    def _on_intro_done(self):
        self.game.intro_seen = True
        self.game.save()
        self.show_screen("game_screen")

    def _show_intro_or_skip(self):
        if self.game.intro_seen:
            self.show_screen("game_screen")
        else:
            self.show_screen("intro")

    def on_name_confirmed(self):
        saver = JsonSaver(SLOT_PATHS[self._pending_slot])
        self.game.set_saver(saver)
        self.game.save()
        self._active_slot = self._pending_slot
        self._pending_slot = None
        _write_last_slot(self._active_slot)
        self.show_screen("intro")

    def on_slot_selected(self, slot_index: int):
        self._bind_slot(slot_index)
        _write_last_slot(slot_index)
        self._show_intro_or_skip()

    def on_slot_deleted(self, slot_index: int):
        self._delete_slot(slot_index)
        last = _read_last_slot()
        if last == slot_index:
            try:
                os.remove(LAST_SLOT_PATH)
            except OSError:
                pass
        if self._active_slot == slot_index:
            self.game = GameState()
            self._active_slot = None

    def on_level_complete(self, level_id: int):
        from levels import LEVELS
        lv = next(x for x in LEVELS if x["id"] == level_id)
        stars = 3
        self.game.complete_level(level_id, stars, lv["xp"])

    # ── key dispatch ───────────────────────────────────────────

    def on_key(self, _widget, event):
        screen = self._screens.get(self._current)
        if screen and screen.handle_key(event):
            return True
        return False

    def on_window_destroy(self, *args):
        if self._active_slot is not None:
            self.game.save()
            _write_last_slot(self._active_slot)
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
