from gi.repository import Gtk, Gdk, Pango


GOLD = Gdk.RGBA(0.85, 0.72, 0.31, 1)
GOLD_DIM = Gdk.RGBA(0.55, 0.55, 0.6, 1)
DIM = Gdk.RGBA(0.3, 0.3, 0.35, 1)
SUBTLE = Gdk.RGBA(0.4, 0.4, 0.5, 1)


class MainMenu(Gtk.Box):
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
            self._menu_block.pack_start(lbl, False, False, 0)
            self._menu_labels.append(lbl)

        self.pack_start(self._menu_block, False, False, 0)

        self.pack_start(Gtk.Box(), False, False, 0)

        self._help = Gtk.Label(label="[ j / k ]  navegar    [ Enter ]  seleccionar")
        self._help.override_font(Pango.FontDescription("Sans 10"))
        self._help.override_color(Gtk.StateFlags.NORMAL, DIM)
        self._help.set_halign(Gtk.Align.CENTER)
        self.pack_start(self._help, False, False, 10)

        self._draw()

    def on_show(self):
        has_save = self._gs.xp > 0 or bool(self._gs.completed_levels)
        if has_save:
            self._items = [
                ("CONTINUAR", "continue"),
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

    def _rebuild(self):
        for lbl in self._menu_labels:
            self._menu_block.remove(lbl)
        self._menu_labels.clear()
        for text, action in self._items:
            lbl = Gtk.Label(label=text)
            lbl._action = action
            lbl.override_font(Pango.FontDescription("Sans 18"))
            lbl.set_padding(0, 12)
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
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self.on_action(self._menu_labels[self._index]._action)
            return True
        return False
