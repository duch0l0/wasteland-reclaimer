"""Оружие игрока. Враги описывают своё оружие в data/enemies.json (ai/range)."""

WEAPONS = {
    "melee": {"name": "Лом", "ranged": False, "ap": 3, "range": 1},
    # самопал — нужен предмет «самопал» в инвентаре и патроны
    "pistol": {"name": "Самопал", "ranged": True, "ap": 4, "range": 7, "damage": 6,
               "item": "самопал", "ammo": "патроны"},
}
RANGE_PENALTY_PER_TILE = 4  # −4% к попаданию за каждую клетку дальше первой
