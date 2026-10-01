"""Оружие игрока. Враги описывают своё оружие в data/enemies.json (ai/range)."""

WEAPONS = {
    "melee": {"name": "Лом", "ranged": False, "ap": 3, "range": 1},
    # огнестрел — нужен предмет в рюкзаке и патроны
    "pistol": {"name": "Самопал", "ranged": True, "ap": 4, "range": 7, "damage": 6,
               "item": "самопал", "ammo": "патроны"},
    "pistol10": {"name": "10-мм пистолет", "ranged": True, "ap": 4, "range": 8, "damage": 9,
                 "item": "10-мм пистолет", "ammo": "патроны"},
    "rifle": {"name": "Винтовка", "ranged": True, "ap": 5, "range": 10, "damage": 12,
              "item": "охотничья винтовка", "ammo": "патроны"},
    # дробовик: огромный урон вплотную (+20% к попаданию на 1–2 клетках), дальше дробь рассеивается
    # (−18% урона за клетку после первой); своя дробь; короткая дальность
    "shotgun": {"name": "Дробовик", "ranged": True, "ap": 5, "range": 5, "damage": 16,
                "item": "дробовик", "ammo": "дробь", "falloff": 0.18, "close_bonus": 20},
    # автомат: очередь из трёх пуль, у каждой свой бросок на попадание (отдача −12% за пулю),
    # броня гасит каждую пулю отдельно; жрёт патроны; прицелиться в часть тела нельзя
    "assault": {"name": "Автомат", "ranged": True, "ap": 6, "range": 9, "damage": 7,
                "item": "автомат", "ammo": "патроны", "burst": 3, "recoil": 12, "aim": False},
}
RANGE_PENALTY_PER_TILE = 4  # −4% к попаданию за каждую клетку дальше первой


def weapon_for_item(name):
    """Ключ оружия, которое даёт предмет, или None."""
    return next((k for k, w in WEAPONS.items() if w.get("item") == name), None)


def available(inventory):
    """Оружие, которое сейчас можно взять в руки: лом всегда, огнестрел — если он в рюкзаке."""
    return ["melee"] + [k for k, w in WEAPONS.items() if w.get("item") and inventory.has(w["item"])]
