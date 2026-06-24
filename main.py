#!/usr/bin/env python3
import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Gdk

from state import GameState
from save_manager import JsonSaver
from screens import MainMenu

SAVE_PATH = os.path.expanduser("~/.vimtutor-plus/save.json")


class App:
    def __init__(self):
        self.build_css()

        saver = JsonSaver(SAVE_PATH)
        self.game = GameState(saver)

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

        self.screen_main = MainMenu(self.game, self.on_menu_action)
        self.stack.add_named(self.screen_main, "main_menu")

        self.window.show_all()

    def on_menu_action(self, action):
        if action == "continue":
            pass
        elif action == "new_game":
            self.game.reset()
        elif action == "options":
            pass
        elif action == "quit":
            self.window.destroy()

    def on_window_destroy(self, *args):
        self.game.save()
        Gtk.main_quit()

    def on_key(self, _widget, event):
        if self.screen_main.handle_key(event):
            return True
        return False

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
