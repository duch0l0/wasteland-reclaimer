"""Оружие игрока. Враги описывают своё оружие в data/enemies.json (ai/range)."""

WEAPONS = {
    "melee": {"name": "Лом", "ranged": False, "ap": 3, "range": 1},
    # огнестрел — нужен предмет в рюкзаке и патроны
    "pistol": {"name": "Самопал", "ranged": True, "ap": 4, "range": 7, "damage": 6,
               "item": "самопал", "ammo": "патроны"},
    "pistol10": {"name": "10-мм пистолет", "ranged": True, "ap": 4, "range": 8, "damage": 9,
                 "item": "10-мм пистолет", "ammo": "патроны"},
}
RANGE_PENALTY_PER_TILE = 4  # −4% к попаданию за каждую клетку дальше первой


def weapon_for_item(name):
    """Ключ оружия, которое даёт предмет, или None."""
    return next((k for k, w in WEAPONS.items() if w.get("item") == name), None)


def available(inventory):
    """Оружие, которое сейчас можно взять в руки: лом всегда, огнестрел — если он в рюкзаке."""
    return ["melee"] + [k for k, w in WEAPONS.items() if w.get("item") and inventory.has(w["item"])]
