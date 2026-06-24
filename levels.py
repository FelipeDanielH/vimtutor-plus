import os

_LEVEL_DIR = os.path.join(os.path.dirname(__file__), "levels")


LEVELS = [
    {
        "id": 1,
        "name": "Introducción",
        "instruction": "Cambia la palabra ROJO por AZUL usando ciw",
        "guide": [
            ("h", "Mover izquierda"),
            ("l", "Mover derecha"),
            ("w", "Siguiente palabra"),
            ("ciw", "Cambia palabra interior"),
        ],
        "start_file": os.path.join(_LEVEL_DIR, "01_inicio.txt"),
        "end_file": os.path.join(_LEVEL_DIR, "01_fin.txt"),
        "xp": 50,
        "required_xp": 0,
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
