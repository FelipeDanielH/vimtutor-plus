import os

_LEVEL_DIR = os.path.join(os.path.dirname(__file__), "levels")


LEVELS = [
    {
        "id": 1,
        "name": "El Movimiento",
        "instruction": "Cambia la palabra ROJO por AZUL",
        "guide": [
            ("h", "Izquierda"),
            ("j", "Abajo"),
            ("k", "Arriba"),
            ("l", "Derecha"),
            ("w", "Siguiente palabra"),
            ("ciw", "Cambia palabra interior"),
        ],
        "start_file": os.path.join(_LEVEL_DIR, "01_inicio.txt"),
        "end_file": os.path.join(_LEVEL_DIR, "01_fin.txt"),
        "xp": 50,
        "required_xp": 0,
    },
    {
        "id": 2,
        "name": "Inserción",
        "instruction": "Agrega 'Huevos' y 'Jamon' a la lista usando o / i",
        "guide": [
            ("i", "Insertar antes del cursor"),
            ("a", "Insertar después del cursor"),
            ("o", "Insertar línea abajo"),
            ("O", "Insertar línea arriba"),
            ("A", "Insertar al final de la línea"),
        ],
        "start_file": os.path.join(_LEVEL_DIR, "02_inicio.txt"),
        "end_file": os.path.join(_LEVEL_DIR, "02_fin.txt"),
        "xp": 75,
        "required_xp": 40,
    },
    {
        "id": 3,
        "name": "Borrado",
        "instruction": "Borra las líneas que NO tienen [Importante]",
        "guide": [
            ("x", "Borrar carácter"),
            ("dd", "Borrar línea"),
            ("dw", "Borrar palabra"),
            ("d$", "Borrar hasta el final"),
            ("u", "Deshacer"),
        ],
        "start_file": os.path.join(_LEVEL_DIR, "03_inicio.txt"),
        "end_file": os.path.join(_LEVEL_DIR, "03_fin.txt"),
        "xp": 100,
        "required_xp": 100,
    },
]


def evaluate(level_id, user_content, expected_content):
    return user_content.strip() == expected_content.strip()


def get_expected(level_id):
    lv = next(x for x in LEVELS if x["id"] == level_id)
    with open(lv["end_file"]) as f:
        return f.read()


def get_start(level_id):
    lv = next(x for x in LEVELS if x["id"] == level_id)
    with open(lv["start_file"]) as f:
        return f.read()
