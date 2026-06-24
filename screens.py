import os
import json
import shutil
import tempfile
from gi.repository import Gtk, Gdk, Pango, GLib, Vte


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


# ── Intro Screen ────────────────────────────────────────────────────────

class IntroScreen(BaseScreen):
    def __init__(self, game_state, on_continue):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._gs = game_state
        self.on_continue = on_continue
        self._intro_text = ""
        self._char_index = 0
        self._show_prompt = False
        self._timeout_id = None
        self._build()

    def _build(self):
        self.pack_start(Gtk.Box(), True, True, 0)

        self._label = Gtk.Label()
        self._label.override_font(Pango.FontDescription("Sans 16"))
        self._label.override_color(Gtk.StateFlags.NORMAL, GOLD)
        self._label.set_halign(Gtk.Align.CENTER)
        self._label.set_valign(Gtk.Align.CENTER)
        self._label.set_line_wrap(True)
        self._label.set_max_width_chars(44)
        self.pack_start(self._label, True, True, 0)

        self._prompt = Gtk.Label()
        self._prompt.override_font(Pango.FontDescription("Sans 12"))
        self._prompt.override_color(Gtk.StateFlags.NORMAL, GOLD)
        self._prompt.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._prompt, False, False, 24)

        self.pack_start(Gtk.Box(), False, False, 0)

    def on_show(self):
        self._intro_text = (
            "En un mundo de código y terminales…\n\n"
            "un editor se alza como el más poderoso.\n\n"
            "Vim, el editor ancestral,\n"
            "guarda secretos que pocos dominan.\n\n"
            "Tú, elegido por el destino,\n"
            "deberás recorrer el camino del guerrero Vim.\n\n"
            "Aprende sus comandos.\n"
            "Supera sus desafíos.\n"
            "Conviértete en el maestro del editor.\n\n"
            "El viaje comienza ahora."
        )
        self._char_index = 0
        self._show_prompt = False
        self._label.set_text("")
        self._prompt.set_text("")
        self._timeout_id = GLib.timeout_add(40, self._tick)

    def on_hide(self):
        if self._timeout_id:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

    def _tick(self):
        if self._char_index < len(self._intro_text):
            self._char_index += 1
            self._label.set_text(self._intro_text[:self._char_index])
            self._timeout_id = GLib.timeout_add(40, self._tick)
            return False
        GLib.timeout_add(2000, self._show_continue_prompt)
        return False

    def _show_continue_prompt(self):
        self._show_prompt = True
        self._prompt.set_text("PULSE  [  l  ]  PARA CONTINUAR")
        return False

    def handle_key(self, event):
        if self._show_prompt and event.keyval == Gdk.KEY_l:
            self.on_continue()
            return True
        return False


# ── Game Screen ────────────────────────────────────────────────────────

class GameScreen(BaseScreen):
    def __init__(self, game_state, level_id, on_complete, on_back):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._gs = game_state
        self._level_id = level_id
        self.on_complete = on_complete
        self.on_back = on_back
        self._pid = None
        self._tmp_file = None
        self._phase = "playing"
        self._passed = False
        self._pause_index = 0
        self._pause_items = [
            ("RESUMIR", "resume"),
            ("REINICIAR", "restart"),
            ("IR AL MENÚ", "quit"),
        ]
        self._build()

    def _build(self):
        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        top.set_halign(Gtk.Align.CENTER)
        self.pack_start(top, False, False, 0)

        from levels import LEVELS
        lv = next(x for x in LEVELS if x["id"] == self._level_id)
        self._title = Gtk.Label(label=f"NIVEL {lv['id']}: {lv['name']}")
        self._title.override_font(Pango.FontDescription("Serif 20"))
        self._title.override_color(Gtk.StateFlags.NORMAL, GOLD)
        self._title.set_halign(Gtk.Align.CENTER)
        top.pack_start(self._title, False, False, 4)

        self._inst = Gtk.Label(label=lv["instruction"])
        self._inst.override_font(Pango.FontDescription("Sans 12"))
        self._inst.override_color(Gtk.StateFlags.NORMAL, SUBTLE)
        self._inst.set_halign(Gtk.Align.CENTER)
        top.pack_start(self._inst, False, False, 2)

        guide_text = "  ".join(f"[{k}] {d}" for k, d in lv["guide"])
        self._guide = Gtk.Label(label=guide_text)
        self._guide.override_font(Pango.FontDescription("Sans 10"))
        self._guide.override_color(Gtk.StateFlags.NORMAL, DIM)
        self._guide.set_halign(Gtk.Align.CENTER)
        top.pack_start(self._guide, False, False, 2)

        # ── game area ──────────────────────────────────────────

        self._game_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.pack_start(self._game_box, True, True, 0)

        self._terminal = Vte.Terminal()
        self._terminal.set_size(80, 20)
        self._terminal.set_font(Pango.FontDescription("Monospace 12"))
        self._terminal.override_color(Gtk.StateFlags.NORMAL,
                                       Gdk.RGBA(0.9, 0.9, 0.95, 1))
        self._terminal.override_background_color(Gtk.StateFlags.NORMAL,
                                                  Gdk.RGBA(0.05, 0.05, 0.1, 1))
        self._terminal.connect("child-exited", self._on_vim_exited)
        self._game_box.pack_start(self._terminal, True, True, 0)

        self._result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._result_box.set_halign(Gtk.Align.CENTER)
        self._result_box.set_valign(Gtk.Align.CENTER)
        self._game_box.pack_start(self._result_box, True, True, 0)

        self._result_title = Gtk.Label()
        self._result_title.override_font(Pango.FontDescription("Serif 28"))
        self._result_title.set_halign(Gtk.Align.CENTER)
        self._result_box.pack_start(self._result_title, False, False, 0)

        self._result_xp = Gtk.Label()
        self._result_xp.override_font(Pango.FontDescription("Sans 18"))
        self._result_xp.set_halign(Gtk.Align.CENTER)
        self._result_box.pack_start(self._result_xp, False, False, 10)

        self._result_box.pack_start(Gtk.Box(), True, True, 0)

        # ── pause overlay ──────────────────────────────────────

        self._pause_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._pause_box.set_halign(Gtk.Align.CENTER)
        self._pause_box.set_valign(Gtk.Align.CENTER)
        self._game_box.pack_start(self._pause_box, True, True, 0)

        pause_title = Gtk.Label(label="— P A U S A —")
        pause_title.override_font(Pango.FontDescription("Serif 24"))
        pause_title.override_color(Gtk.StateFlags.NORMAL, GOLD)
        pause_title.set_halign(Gtk.Align.CENTER)
        self._pause_box.pack_start(pause_title, False, False, 0)

        self._pause_box.pack_start(Gtk.Box(), False, True, 0)

        self._pause_labels: list[Gtk.Label] = []
        for text, action in self._pause_items:
            lbl = Gtk.Label(label=text)
            lbl._action = action
            lbl.override_font(Pango.FontDescription("Sans 18"))
            lbl.set_padding(0, 10)
            lbl.set_halign(Gtk.Align.CENTER)
            lbl.show()
            self._pause_box.pack_start(lbl, False, False, 0)
            self._pause_labels.append(lbl)

        self._pause_box.pack_start(Gtk.Box(), True, True, 0)

        self._pause_help = Gtk.Label()
        self._pause_help.override_font(Pango.FontDescription("Sans 10"))
        self._pause_help.set_halign(Gtk.Align.CENTER)
        self._pause_box.pack_start(self._pause_help, False, False, 8)

        self._pause_box.hide()

        # ── help bar ───────────────────────────────────────────

        self._help = Gtk.Label(label="[ F10 ]  pausa")
        self._help.override_font(Pango.FontDescription("Sans 10"))
        self._help.override_color(Gtk.StateFlags.NORMAL, DIM)
        self._help.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._help, False, False, 6)

        self._draw_pause()

    def _draw_pause(self):
        for i, lbl in enumerate(self._pause_labels):
            if i == self._pause_index:
                lbl.set_text(f"  ►  {self._pause_items[i][0]}")
                lbl.override_color(Gtk.StateFlags.NORMAL, GOLD)
            else:
                lbl.set_text(f"     {self._pause_items[i][0]}")
                lbl.override_color(Gtk.StateFlags.NORMAL, GOLD_DIM)
        self._pause_help.set_text("[ j / k ]  navegar    [ l ]  seleccionar    [ h ]  volver")
        self._pause_help.override_color(Gtk.StateFlags.NORMAL, DIM)

    def on_show(self):
        from levels import LEVELS
        lv = next(x for x in LEVELS if x["id"] == self._level_id)
        tmp_dir = os.path.join(tempfile.gettempdir(), "vimtutor")
        os.makedirs(tmp_dir, exist_ok=True)
        self._tmp_file = os.path.join(tmp_dir, f"level_{self._level_id}.txt")
        shutil.copy(lv["start_file"], self._tmp_file)

        self._phase = "playing"
        self._passed = False
        self._pause_index = 0
        self._result_title.set_text("")
        self._result_xp.set_text("")
        self._result_box.hide()
        self._pause_box.hide()
        self._terminal.show()
        self._help.set_text("[ F10 ]  pausa")
        self._launch_vim()
        self._terminal.grab_focus()

    def _launch_vim(self):
        swap = os.path.join(os.path.dirname(self._tmp_file), "." + os.path.basename(self._tmp_file) + ".swp")
        try:
            os.remove(swap)
        except OSError:
            pass
        vim_path = shutil.which("vim") or "/usr/bin/vim"
        ok, pid = self._terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            None,
            [vim_path, "-n", self._tmp_file],
            [],
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            None,
        )
        self._pid = pid if ok else None

    def on_hide(self):
        if self._pid:
            try:
                os.kill(self._pid, 15)
            except OSError:
                pass
            self._pid = None

    def _on_vim_exited(self, terminal, status):
        self._pid = None
        from levels import get_expected, evaluate

        expected = get_expected(self._level_id)
        try:
            with open(self._tmp_file) as f:
                user = f.read()
        except OSError:
            user = ""

        self._passed = evaluate(self._level_id, user, expected)

        self._phase = "result"
        self._terminal.hide()

        if self._passed:
            lv = next(x for x in LEVELS if x["id"] == self._level_id)
            self._result_title.set_text("¡NIVEL COMPLETADO!")
            self._result_title.override_color(Gtk.StateFlags.NORMAL, GREEN)
            self._result_xp.set_text(f"★ ★ ★   XP +{lv['xp']}")
            self._result_xp.override_color(Gtk.StateFlags.NORMAL, GOLD)
            self.on_complete(self._level_id)
        else:
            self._result_title.set_text("INTÉNTALO DE NUEVO")
            self._result_title.override_color(Gtk.StateFlags.NORMAL,
                                               Gdk.RGBA(0.9, 0.3, 0.2, 1))
            self._result_xp.set_text("")
        self._result_box.show()
        self._help.set_text("[ F10 ]  pausa    [ l ]  continuar")

    def handle_key(self, event):
        if self._phase == "playing":
            if event.keyval == Gdk.KEY_F10:
                self._enter_pause()
                return True
            return False
        if self._phase == "pause":
            return self._handle_pause_key(event)
        if self._phase == "result":
            if event.keyval == Gdk.KEY_l:
                self.on_back()
                return True
            return False
        return False

    def _enter_pause(self):
        self._phase = "pause"
        self._pause_index = 0
        self._terminal.hide()
        self._pause_box.show()
        self._draw_pause()

    def _handle_pause_key(self, event):
        if event.keyval in (Gdk.KEY_j, Gdk.KEY_Down):
            self._pause_index = (self._pause_index + 1) % len(self._pause_labels)
            self._draw_pause()
            return True
        if event.keyval in (Gdk.KEY_k, Gdk.KEY_Up):
            self._pause_index = (self._pause_index - 1) % len(self._pause_labels)
            self._draw_pause()
            return True
        if event.keyval == Gdk.KEY_l:
            action = self._pause_labels[self._pause_index]._action
            if action == "resume":
                self._resume_game()
            elif action == "restart":
                self._restart_level()
            elif action == "quit":
                self.on_back()
            return True
        if event.keyval == Gdk.KEY_h:
            self._resume_game()
            return True
        return False

    def _resume_game(self):
        self._phase = "playing"
        self._pause_box.hide()
        self._terminal.show()
        self._help.set_text("[ F10 ]  pausa")

    def _restart_level(self):
        from levels import LEVELS
        if self._pid:
            try:
                os.kill(self._pid, 15)
            except OSError:
                pass
            self._pid = None
        lv = next(x for x in LEVELS if x["id"] == self._level_id)
        shutil.copy(lv["start_file"], self._tmp_file)
        self._phase = "playing"
        self._pause_box.hide()
        self._terminal.show()
        self._launch_vim()


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
