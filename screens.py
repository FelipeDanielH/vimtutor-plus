import os
import json
from gi.repository import Gtk, Gdk, Pango


SLOT_DIR = os.path.expanduser("~/.vimtutor-plus")
GOLD = Gdk.RGBA(0.85, 0.72, 0.31, 1)
GOLD_DIM = Gdk.RGBA(0.55, 0.55, 0.6, 1)
DIM = Gdk.RGBA(0.3, 0.3, 0.35, 1)
SUBTLE = Gdk.RGBA(0.4, 0.4, 0.5, 1)
GREEN = Gdk.RGBA(0.0, 0.8, 0.4, 1)


class BaseScreen(Gtk.Box):
    def handle_key(self, event):
        return False

    def on_show(self):
        pass

    def on_hide(self):
        pass


# ── Main Menu ─────────────────────────────────────────────────────────

class MainMenu(BaseScreen):
    def __init__(self, game_state, on_action):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._gs = game_state
        self.on_action = on_action
        self._items = []
        self._index = 0
        self._menu_labels = []
        self._title_block = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._menu_block = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._build()

    def _build(self):
        self.pack_start(Gtk.Box(), True, True, 0)

        self._title_block.set_halign(Gtk.Align.CENTER)
        t = Gtk.Label(label="VIMTUTOR+")
        t.override_font(Pango.FontDescription("Serif 52"))
        t.override_color(Gtk.StateFlags.NORMAL, GOLD)
        self._title_block.pack_start(t, False, False, 0)

        sep = Gtk.Label(label="━━━━━━━━━━━━━━━━━━━━")
        sep.override_font(Pango.FontDescription("Sans 10"))
        sep.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.85, 0.72, 0.31, 0.3))
        sep.set_halign(Gtk.Align.CENTER)
        self._title_block.pack_start(sep, False, False, 4)

        s = Gtk.Label(label="DOMINA EL EDITOR")
        s.override_font(Pango.FontDescription("Sans 10"))
        s.override_color(Gtk.StateFlags.NORMAL, SUBTLE)
        s.set_halign(Gtk.Align.CENTER)
        self._title_block.pack_start(s, False, False, 0)

        self.pack_start(self._title_block, False, False, 0)
        self.pack_start(Gtk.Box(), True, True, 0)

        self._menu_block.set_halign(Gtk.Align.CENTER)
        self._items = [
            ("NUEVA PARTIDA", "new_game"),
            ("OPCIONES", "options"),
            ("SALIR", "quit"),
        ]
        for text, action in self._items:
            lbl = Gtk.Label(label=text)
            lbl._action = action
            lbl.override_font(Pango.FontDescription("Sans 18"))
            lbl.set_padding(0, 12)
            lbl.show()
            self._menu_block.pack_start(lbl, False, False, 0)
            self._menu_labels.append(lbl)

        self.pack_start(self._menu_block, False, False, 0)
        self.pack_start(Gtk.Box(), False, False, 0)

        self._help = Gtk.Label(label="[ j / k ]  navegar    [ l ]  seleccionar    [ h ]  salir")
        self._help.override_font(Pango.FontDescription("Sans 10"))
        self._help.override_color(Gtk.StateFlags.NORMAL, DIM)
        self._help.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._help, False, False, 10)

        self._draw()

    def on_show(self):
        has_save = self._any_save()
        if has_save:
            self._items = [
                ("CONTINUAR", "continue"),
                ("CARGAR PARTIDA", "load_game"),
                ("NUEVA PARTIDA", "new_game"),
                ("OPCIONES", "options"),
                ("SALIR", "quit"),
            ]
        else:
            self._items = [
                ("NUEVA PARTIDA", "new_game"),
                ("OPCIONES", "options"),
                ("SALIR", "quit"),
            ]
        self._index = 0
        self._rebuild()

    def _any_save(self):
        for i in range(3):
            path = os.path.join(SLOT_DIR, f"slot_{i}.json")
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        d = json.load(f)
                    if d.get("player", {}).get("name", ""):
                        return True
                except (OSError, json.JSONDecodeError):
                    pass
        return False

    def _rebuild(self):
        for lbl in self._menu_labels:
            self._menu_block.remove(lbl)
        self._menu_labels.clear()
        for text, action in self._items:
            lbl = Gtk.Label(label=text)
            lbl._action = action
            lbl.override_font(Pango.FontDescription("Sans 18"))
            lbl.set_padding(0, 12)
            lbl.show()
            self._menu_block.pack_start(lbl, False, False, 0)
            self._menu_labels.append(lbl)
        self._draw()

    def _draw(self):
        for i, lbl in enumerate(self._menu_labels):
            if i == self._index:
                lbl.set_text(f"  ►  {self._items[i][0]}")
                lbl.override_color(Gtk.StateFlags.NORMAL, GOLD)
            else:
                lbl.set_text(f"     {self._items[i][0]}")
                lbl.override_color(Gtk.StateFlags.NORMAL, GOLD_DIM)

    def handle_key(self, event):
        if event.keyval in (Gdk.KEY_j, Gdk.KEY_Down):
            self._index = (self._index + 1) % len(self._menu_labels)
            self._draw()
            return True
        if event.keyval in (Gdk.KEY_k, Gdk.KEY_Up):
            self._index = (self._index - 1) % len(self._menu_labels)
            self._draw()
            return True
        if event.keyval == Gdk.KEY_l:
            self.on_action(self._menu_labels[self._index]._action)
            return True
        if event.keyval == Gdk.KEY_h:
            self.on_action("quit")
            return True
        return False


# ── Character Create ──────────────────────────────────────────────────

class CharacterCreate(BaseScreen):
    def __init__(self, game_state, on_confirm, on_back):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._gs = game_state
        self.on_confirm = on_confirm
        self.on_back = on_back
        self._name = ""
        self._mode = "normal"
        self._build()

    def _build(self):
        self.pack_start(Gtk.Box(), True, True, 0)

        t = Gtk.Label(label="CREA TU PERSONAJE")
        t.override_font(Pango.FontDescription("Serif 28"))
        t.override_color(Gtk.StateFlags.NORMAL, GOLD)
        t.set_halign(Gtk.Align.CENTER)
        self.pack_start(t, False, False, 0)

        self.pack_start(Gtk.Box(), False, True, 0)

        prompt = Gtk.Label(label="INGRESA TU NOMBRE:")
        prompt.override_font(Pango.FontDescription("Sans 14"))
        prompt.override_color(Gtk.StateFlags.NORMAL, SUBTLE)
        prompt.set_halign(Gtk.Align.CENTER)
        self.pack_start(prompt, False, False, 10)

        self._name_label = Gtk.Label(label="")
        self._name_label.override_font(Pango.FontDescription("Sans 24"))
        self._name_label.override_color(Gtk.StateFlags.NORMAL, GOLD)
        self._name_label.set_halign(Gtk.Align.CENTER)
        self._name_label.set_padding(0, 10)
        self.pack_start(self._name_label, False, False, 0)

        self._mode_label = Gtk.Label(label="")
        self._mode_label.override_font(Pango.FontDescription("Sans 11"))
        self._mode_label.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._mode_label, False, False, 4)

        self.pack_start(Gtk.Box(), True, True, 0)

        self._help = Gtk.Label()
        self._help.override_font(Pango.FontDescription("Sans 10"))
        self._help.override_color(Gtk.StateFlags.NORMAL, DIM)
        self._help.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._help, False, False, 10)

        self._draw()

    def on_show(self):
        self._name = ""
        self._mode = "normal"
        self._draw()

    def _draw(self):
        cursor = "█" if self._mode == "insert" else ""
        display = self._name + cursor if cursor or self._name else "█"
        self._name_label.set_text(display)
        if self._mode == "normal":
            self._mode_label.set_text("-- NORMAL --")
            self._mode_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.4, 0.4, 0.5, 1))
            self._help.set_text("[ i ]  escribir    [ l ]  confirmar   [ h ]  volver")
        else:
            self._mode_label.set_text("-- INSERT --")
            self._mode_label.override_color(Gtk.StateFlags.NORMAL, GREEN)
            self._help.set_text("[ Esc ]  salir del modo insert    [ Backspace ]  borrar")

    def handle_key(self, event):
        if event.keyval == Gdk.KEY_BackSpace and self._mode == "insert":
            self._name = self._name[:-1]
            self._draw()
            return True
        if self._mode == "normal":
            if event.keyval == Gdk.KEY_i:
                self._mode = "insert"
                self._draw()
                return True
            if event.keyval == Gdk.KEY_l and self._name:
                self._gs.player_name = self._name
                self._gs.save()
                self.on_confirm()
                return True
            if event.keyval == Gdk.KEY_h:
                self.on_back()
                return True
        else:
            if event.keyval == Gdk.KEY_Escape:
                self._mode = "normal"
                self._draw()
                return True
            char = chr(Gdk.keyval_to_unicode(event.keyval))
            if char.isprintable() and char != "":
                self._name += char
                self._draw()
                return True
        return False


# ── Welcome Screen ────────────────────────────────────────────────────

class WelcomeScreen(BaseScreen):
    def __init__(self, game_state, on_back):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._gs = game_state
        self.on_back = on_back
        self._build()

    def _build(self):
        self.pack_start(Gtk.Box(), True, True, 0)

        self._welcome = Gtk.Label()
        self._welcome.override_font(Pango.FontDescription("Serif 32"))
        self._welcome.override_color(Gtk.StateFlags.NORMAL, GOLD)
        self._welcome.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._welcome, False, False, 0)

        self.pack_start(Gtk.Box(), True, True, 0)

        h = Gtk.Label(label="[ l / h ]  volver al menú")
        h.override_font(Pango.FontDescription("Sans 10"))
        h.override_color(Gtk.StateFlags.NORMAL, DIM)
        h.set_halign(Gtk.Align.CENTER)
        self.pack_start(h, False, False, 10)

    def on_show(self):
        self._welcome.set_text(f"BIENVENIDO, {self._gs.player_name}!")

    def handle_key(self, event):
        if event.keyval in (Gdk.KEY_l, Gdk.KEY_h):
            self.on_back()
            return True
        return False


# ── Load Select ───────────────────────────────────────────────────────

SLOT_LABELS = ["PRIMERA", "SEGUNDA", "TERCERA"]


class LoadSelect(BaseScreen):
    def __init__(self, game_state, on_select, on_delete, on_back):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._gs = game_state
        self.on_select = on_select
        self.on_delete = on_delete
        self.on_back = on_back
        self._index = 0
        self._slots: list[dict] = [{"name": "", "exists": False} for _ in range(3)]
        self._confirm_delete = False
        self._build()

    def _build(self):
        self.pack_start(Gtk.Box(), True, True, 0)

        t = Gtk.Label(label="CARGAR PARTIDA")
        t.override_font(Pango.FontDescription("Serif 28"))
        t.override_color(Gtk.StateFlags.NORMAL, GOLD)
        t.set_halign(Gtk.Align.CENTER)
        self.pack_start(t, False, False, 0)

        self.pack_start(Gtk.Box(), False, True, 0)

        self._slot_labels: list[Gtk.Label] = []
        for i in range(3):
            lbl = Gtk.Label()
            lbl.override_font(Pango.FontDescription("Sans 16"))
            lbl.set_halign(Gtk.Align.CENTER)
            lbl.set_padding(0, 10)
            lbl.show()
            self.pack_start(lbl, False, False, 0)
            self._slot_labels.append(lbl)

        self._confirm_label = Gtk.Label()
        self._confirm_label.override_font(Pango.FontDescription("Sans 14"))
        self._confirm_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.85, 0.72, 0.31, 1))
        self._confirm_label.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._confirm_label, False, False, 10)

        self.pack_start(Gtk.Box(), True, True, 0)

        h = Gtk.Label(label="[ j / k ]  navegar    [ l ]  cargar    [ d ]  eliminar    [ h ]  volver")
        h.override_font(Pango.FontDescription("Sans 10"))
        h.override_color(Gtk.StateFlags.NORMAL, DIM)
        h.set_halign(Gtk.Align.CENTER)
        self.pack_start(h, False, False, 10)

        self._refresh()

    def on_show(self):
        self._confirm_delete = False
        self._index = 0
        self._refresh()

    def _refresh(self):
        for i in range(3):
            path = os.path.join(SLOT_DIR, f"slot_{i}.json")
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        d = json.load(f)
                    p = d.get("player", {})
                    self._slots[i] = {
                        "name": p.get("name", ""),
                        "xp": p.get("xp", 0),
                        "hp": p.get("hp", 3),
                        "max_hp": p.get("max_hp", 5),
                        "exists": True,
                    }
                except (OSError, json.JSONDecodeError):
                    self._slots[i] = {"name": "", "exists": False}
            else:
                self._slots[i] = {"name": "", "exists": False}
        self._draw()

    def _draw(self):
        for i, lbl in enumerate(self._slot_labels):
            s = self._slots[i]
            if s["exists"] and s["name"]:
                bar = "❤️" * s["hp"] + "🖤" * (s["max_hp"] - s["hp"])
                text = f"{SLOT_LABELS[i]}  —  {s['name']}  XP:{s['xp']}  {bar}"
            elif s["exists"]:
                text = f"{SLOT_LABELS[i]}  —  VACÍA"
            else:
                text = f"{SLOT_LABELS[i]}  —  VACÍA"
            if i == self._index:
                lbl.set_text(f"  ►  {text}")
                lbl.override_color(Gtk.StateFlags.NORMAL, GOLD)
            else:
                lbl.set_text(f"     {text}")
                lbl.override_color(Gtk.StateFlags.NORMAL, GOLD_DIM if s["name"] else DIM)

        if self._confirm_delete:
            self._confirm_label.set_text("¿ELIMINAR PARTIDA?  [ l ]  sí  [ h ]  no")
        else:
            self._confirm_label.set_text("")

    def handle_key(self, event):
        if self._confirm_delete:
            if event.keyval == Gdk.KEY_l:
                idx = self._index
                s = self._slots[idx]
                if s["exists"] and s["name"]:
                    self.on_delete(idx)
                self._confirm_delete = False
                self._refresh()
                return True
            if event.keyval == Gdk.KEY_h:
                self._confirm_delete = False
                self._draw()
                return True
            return False

        if event.keyval in (Gdk.KEY_j, Gdk.KEY_Down):
            self._index = (self._index + 1) % 3
            self._draw()
            return True
        if event.keyval in (Gdk.KEY_k, Gdk.KEY_Up):
            self._index = (self._index - 1) % 3
            self._draw()
            return True
        if event.keyval == Gdk.KEY_l:
            s = self._slots[self._index]
            if s["exists"] and s["name"]:
                self.on_select(self._index)
            return True
        if event.keyval == Gdk.KEY_d:
            s = self._slots[self._index]
            if s["exists"] and s["name"]:
                self._confirm_delete = True
                self._draw()
            return True
        if event.keyval == Gdk.KEY_h:
            self.on_back()
            return True
        return False
