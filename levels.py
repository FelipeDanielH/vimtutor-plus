import os

_LEVEL_DIR = os.path.join(os.path.dirname(__file__), "levels")

LEVELS = [
    {
        "id": 1,
        "type": "maze",
        "name": "El Laberinto",
        "instruction": "Usa h j k l para navegar el laberinto y llegar al tesoro",
        "guide": [
            ("h", "← mover"),
            ("j", "↓ mover"),
            ("k", "↑ mover"),
            ("l", "→ mover"),
        ],
        "grid": [
            "#################",
            "#@..............#",
            "#.#.#########.#.#",
            "#.#.........#.#.#",
            "#.#####.###.#.#.#",
            "#.....#.#...#.#.#",
            "#.###.#.#.###.#.#",
            "#.#...#.#...#...#",
            "#.#.#########.#.#",
            "#.#...........#.#",
            "#.###########.#.#",
            "#.............G.#",
            "#################",
        ],
        "xp": 100,
        "required_xp": 0,
    },
]


def evaluate(level_id, user_content, expected_content):
    return user_content.strip() == expected_content.strip()


def get_expected(level_id):
    lv = next(x for x in LEVELS if x["id"] == level_id)
    if lv.get("type") == "maze":
        raise TypeError("maze levels have no expected file")
    with open(lv["end_file"]) as f:
        return f.read()


def get_start(level_id):
    lv = next(x for x in LEVELS if x["id"] == level_id)
    if lv.get("type") == "maze":
        raise TypeError("maze levels have no start file")
    with open(lv["start_file"]) as f:
        return f.read()
