import time

from save_manager import Saver, new_save_data


class GameState:
    def __init__(self, saver: Saver | None = None):
        self._saver = saver
        if saver is not None:
            data = saver.load()
            if data is None:
                data = new_save_data()
            self._d = data
        else:
            self._d = new_save_data()

    def set_saver(self, saver: Saver) -> None:
        self._saver = saver
        data = saver.load()
        if data is not None:
            self._d = data

    def save(self) -> None:
        if self._saver is None:
            return
        self._d["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._saver.save(self._d)

    # -- player --
    @property
    def player_name(self) -> str:
        return self._d["player"].get("name", "")

    @player_name.setter
    def player_name(self, value: str) -> None:
        self._d["player"]["name"] = value

    @property
    def xp(self) -> int:
        return self._d["player"]["xp"]

    @xp.setter
    def xp(self, value: int) -> None:
        self._d["player"]["xp"] = value

    @property
    def hp(self) -> int:
        return self._d["player"]["hp"]

    @hp.setter
    def hp(self, value: int) -> None:
        self._d["player"]["hp"] = max(0, min(value, self._d["player"]["max_hp"]))

    @property
    def max_hp(self) -> int:
        return self._d["player"]["max_hp"]

    def add_xp(self, amount: int) -> None:
        self._d["player"]["xp"] += amount
        self._check_unlocks()

    def lose_hp(self) -> bool:
        self._d["player"]["hp"] -= 1
        self.save()
        return self._d["player"]["hp"] <= 0

    def restore_hp(self) -> None:
        self._d["player"]["hp"] = self._d["player"]["max_hp"]

    def currency(self, key: str, default=0) -> int:
        return self._d["player"]["currency"].get(key, default)

    def add_currency(self, key: str, amount: int) -> None:
        cur = self._d["player"]["currency"]
        cur[key] = cur.get(key, 0) + amount

    # -- progression --
    @property
    def unlocked_levels(self) -> list[int]:
        return self._d["progression"]["unlocked_levels"]

    @property
    def completed_levels(self) -> dict:
        return self._d["progression"]["completed_levels"]

    @property
    def stars(self) -> dict:
        return self._d["progression"]["stars"]

    def complete_level(self, level_id: int, star_count: int, xp_gained: int) -> None:
        self._d["progression"]["completed_levels"][str(level_id)] = True
        old = self._d["progression"]["stars"].get(str(level_id), 0)
        self._d["progression"]["stars"][str(level_id)] = max(old, star_count)
        self._d["player"]["xp"] += xp_gained
        self.restore_hp()
        self._check_unlocks()
        self.save()

    def _check_unlocks(self) -> None:
        from levels import LEVELS
        unlocked = self._d["progression"]["unlocked_levels"]
        for lv in LEVELS:
            if lv["id"] not in unlocked and lv.get("required_xp", 0) <= self._d["player"]["xp"]:
                unlocked.append(lv["id"])

    # -- settings --
    @property
    def settings(self) -> dict:
        return self._d["settings"]

    def reset(self) -> None:
        fresh = new_save_data()
        self._d = fresh
        if self._saver is not None:
            self._saver.save(fresh)
