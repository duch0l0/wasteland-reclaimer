"""Оружие игрока — как в Fallout: пять классов, у каждого свой навык (src/skills.py).

  guns      Стрельба          пистолеты, револьверы, винтовки, дробовики, пистолеты-пулемёты, автоматы, Гаусс
  heavy     Тяжёлое оружие    пулемёты, миниган, огнемёт, ракетомёт
  energy    Энергооружие      лазеры и плазма: луч прожигает броню (pierce — доля брони, которая не работает)
  throwing  Метание           ножи и копья в руку; гранаты (G) летят точнее
  melee     Рукопашная        лом, нож, мачете, топор, кувалда, силовой кулак (damage — прибавка к удару)

req — навык, с которым оружие слушается. Ниже порога: −2% к попаданию за каждое недостающее очко,
очередью не выстрелить (отдача рвёт ствол из рук), тяжёлым — ещё и +1 ОД на выстрел. Мощное оружие
можно снять с врага хоть в первом акте, но толк от него — только после прокачки.
tier — ступень (1 — первый акт … 5 — легенда), unique — единственный экземпляр в игре.
Враги описывают своё оружие в data/enemies.json (ai/range).
"""

WEAPONS = {
    # ---------------------------------------------------------------- рукопашная
    "melee": {"name": "Лом", "ranged": False, "skill": "melee", "ap": 3, "range": 1, "tier": 1},
    "knife": {"name": "Боевой нож", "ranged": False, "skill": "melee", "ap": 2, "range": 1, "damage": 1,
              "item": "боевой нож", "tier": 1},
    "machete": {"name": "Мачете", "ranged": False, "skill": "melee", "ap": 3, "range": 1, "damage": 5,
                "item": "мачете", "req": 55, "tier": 2},
    "fire_axe": {"name": "Пожарный топор", "ranged": False, "skill": "melee", "ap": 4, "range": 1, "damage": 10,
                 "item": "пожарный топор", "req": 70, "tier": 2},
    "sledge": {"name": "Кувалда", "ranged": False, "skill": "melee", "ap": 4, "range": 1, "damage": 14,
               "item": "кувалда", "req": 85, "tier": 3},
    "power_fist": {"name": "Силовой кулак", "ranged": False, "skill": "melee", "ap": 3, "range": 1, "damage": 18,
                   "item": "силовой кулак", "req": 105, "tier": 4},
    "boathook": {"name": "Багор Мамаши Кейт", "ranged": False, "skill": "melee", "ap": 3, "range": 1, "damage": 9,
                 "item": "багор Мамаши Кейт", "req": 50, "tier": 2, "unique": True},
    "super_sledge": {"name": "Супер-кувалда", "ranged": False, "skill": "melee", "ap": 4, "range": 1, "damage": 26,
                     "item": "супер-кувалда", "req": 120, "tier": 5, "unique": True},
    # ---------------------------------------------------------------- стрельба (огнестрел)
    "pistol": {"name": "Самопал", "ranged": True, "skill": "guns", "ap": 4, "range": 7, "damage": 6,
               "item": "самопал", "ammo": "патроны", "tier": 1},
    # обрез: дробь в упор, дальше трёх клеток — бесполезен
    "sawedoff": {"name": "Обрез", "ranged": True, "skill": "guns", "ap": 4, "range": 3, "damage": 12,
                 "item": "обрез", "ammo": "дробь", "falloff": 0.25, "close_bonus": 25, "req": 40, "tier": 1},
    "pistol10": {"name": "10-мм пистолет", "ranged": True, "skill": "guns", "ap": 4, "range": 8, "damage": 9,
                 "item": "10-мм пистолет", "ammo": "патроны", "req": 55, "tier": 1},
    "smg": {"name": "Пистолет-пулемёт", "ranged": True, "skill": "guns", "ap": 5, "range": 6, "damage": 5,
            "item": "пистолет-пулемёт", "ammo": "патроны", "burst": 3, "recoil": 10, "aim": False, "req": 60, "tier": 2},
    # дробовик: огромный урон вплотную (+20% к попаданию на 1–2 клетках), дальше дробь рассеивается
    # (−18% урона за клетку после первой); своя дробь; короткая дальность
    "shotgun": {"name": "Дробовик", "ranged": True, "skill": "guns", "ap": 5, "range": 5, "damage": 16,
                "item": "дробовик", "ammo": "дробь", "falloff": 0.18, "close_bonus": 20, "req": 60, "tier": 2},
    "rifle": {"name": "Винтовка", "ranged": True, "skill": "guns", "ap": 5, "range": 10, "damage": 12,
              "item": "охотничья винтовка", "ammo": "патроны", "req": 65, "tier": 2},
    "revolver": {"name": "Револьвер .44", "ranged": True, "skill": "guns", "ap": 5, "range": 8, "damage": 15,
                 "item": "револьвер .44", "ammo": "патроны", "req": 70, "tier": 2},
    # автомат: очередь из трёх пуль, у каждой свой бросок на попадание (отдача −12% за пулю),
    # броня гасит каждую пулю отдельно; жрёт патроны; прицелиться в часть тела нельзя
    "assault": {"name": "Автомат", "ranged": True, "skill": "guns", "ap": 6, "range": 9, "damage": 7,
                "item": "автомат", "ammo": "патроны", "burst": 3, "recoil": 12, "aim": False, "req": 85, "tier": 3},
    "combat_shotgun": {"name": "Боевой дробовик", "ranged": True, "skill": "guns", "ap": 6, "range": 5, "damage": 14,
                       "item": "боевой дробовик", "ammo": "дробь", "burst": 2, "recoil": 10, "aim": False,
                       "falloff": 0.15, "close_bonus": 20, "req": 85, "tier": 3},
    "beauty": {"name": "«Красотка»", "ranged": True, "skill": "guns", "ap": 5, "range": 6, "damage": 18,
               "item": "дробовик «Красотка»", "ammo": "дробь", "burst": 2, "recoil": 6, "aim": False,
               "falloff": 0.12, "close_bonus": 25, "req": 80, "tier": 4, "unique": True},
    "justice": {"name": "«Справедливость»", "ranged": True, "skill": "guns", "ap": 4, "range": 9, "damage": 18,
                "item": "револьвер «Справедливость»", "ammo": "патроны", "req": 70, "tier": 3, "unique": True},
    "voice": {"name": "«Голос пустоши»", "ranged": True, "skill": "guns", "ap": 6, "range": 15, "damage": 26,
              "item": "винтовка «Голос пустоши»", "ammo": "патроны", "req": 95, "tier": 4, "unique": True},
    "sniper": {"name": "Снайперская винтовка", "ranged": True, "skill": "guns", "ap": 6, "range": 14, "damage": 22,
               "item": "снайперская винтовка", "ammo": "патроны", "req": 105, "tier": 4},
    # Гаусс: магнитный ускоритель, игла насквозь через броню. Одна на всю пустошь.
    "gauss": {"name": "Винтовка Гаусса", "ranged": True, "skill": "guns", "ap": 6, "range": 16, "damage": 40,
              "item": "винтовка Гаусса", "ammo": "ЭМ-патрон", "pierce": 0.6, "req": 125, "tier": 5, "unique": True},
    # ---------------------------------------------------------------- тяжёлое оружие
    # огнемёт: струя поджигает цель и соседей (горит три хода), на дальности не работает
    "flamer": {"name": "Огнемёт", "ranged": True, "skill": "heavy", "ap": 6, "range": 4, "damage": 10,
               "item": "огнемёт", "ammo": "топливо", "fire": 4, "req": 45, "tier": 2},
    "lmg": {"name": "Ручной пулемёт", "ranged": True, "skill": "heavy", "ap": 7, "range": 9, "damage": 8,
            "item": "ручной пулемёт", "ammo": "патроны", "burst": 5, "recoil": 8, "aim": False, "req": 60, "tier": 3},
    # ракетомёт: ракета рвётся у цели — задевает всех рядом (как граната, только злее)
    "rocket": {"name": "Ракетомёт", "ranged": True, "skill": "heavy", "ap": 7, "range": 11, "damage": 0,
               "item": "ракетомёт", "ammo": "ракета", "blast": "rocket", "req": 70, "tier": 3},
    "minigun": {"name": "Миниган", "ranged": True, "skill": "heavy", "ap": 8, "range": 8, "damage": 7,
                "item": "миниган", "ammo": "патроны", "burst": 8, "recoil": 5, "aim": False, "req": 90, "tier": 4},
    "mommy": {"name": "«Мамочка»", "ranged": True, "skill": "heavy", "ap": 7, "range": 9, "damage": 9,
              "item": "миниган «Мамочка»", "ammo": "патроны", "burst": 10, "recoil": 4, "aim": False,
              "req": 95, "tier": 5, "unique": True},
    # ---------------------------------------------------------------- энергооружие
    "laser_pistol": {"name": "Лазерный пистолет", "ranged": True, "skill": "energy", "ap": 4, "range": 9, "damage": 10,
                     "item": "лазерный пистолет", "ammo": "энергоячейка", "pierce": 0.5, "req": 35, "tier": 2},
    "plasma_pistol": {"name": "Плазменный пистолет", "ranged": True, "skill": "energy", "ap": 5, "range": 7,
                      "damage": 17, "item": "плазменный пистолет", "ammo": "энергоячейка", "pierce": 0.6,
                      "req": 65, "tier": 3},
    "laser_rifle": {"name": "Лазерная винтовка", "ranged": True, "skill": "energy", "ap": 5, "range": 11, "damage": 16,
                    "item": "лазерная винтовка", "ammo": "ядерный элемент", "pierce": 0.5, "req": 75, "tier": 3},
    "stargazer": {"name": "«Звездочёт»", "ranged": True, "skill": "energy", "ap": 4, "range": 13, "damage": 22,
                  "item": "лазер «Звездочёт»", "ammo": "ядерный элемент", "pierce": 0.6, "req": 90,
                  "tier": 4, "unique": True},
    "alien": {"name": "Инопланетный бластер", "ranged": True, "skill": "energy", "ap": 4, "range": 9, "damage": 32,
              "item": "инопланетный бластер", "ammo": "инопланетная батарея", "pierce": 0.7, "req": 60, "tier": 5,
              "unique": True},
    "plasma": {"name": "Плазменная винтовка", "ranged": True, "skill": "energy", "ap": 5, "range": 9, "damage": 26,
               "item": "плазменная винтовка", "ammo": "ядерный элемент", "pierce": 0.75, "req": 100, "tier": 4},
    # ---------------------------------------------------------------- метание (в руку; гранаты — клавишей G)
    "throw_knife": {"name": "Метательные ножи", "ranged": True, "skill": "throwing", "ap": 3, "range": 6, "damage": 7,
                    "item": "метательный нож", "ammo": "метательный нож", "thrown": True, "tier": 1},
    "spear": {"name": "Копьё", "ranged": True, "skill": "throwing", "ap": 4, "range": 5, "damage": 13,
              "item": "копьё", "ammo": "копьё", "thrown": True, "req": 50, "tier": 2},
}
SKILL_NAMES = {"guns": "Стрельба", "heavy": "Тяжёлое оружие", "energy": "Энергооружие",
               "throwing": "Метание", "melee": "Рукопашная"}
RANGE_PENALTY_PER_TILE = 4  # −4% к попаданию за каждую клетку дальше первой


def weapon_for_item(name):
    """Ключ оружия, которое даёт предмет, или None."""
    return next((k for k, w in WEAPONS.items() if w.get("item") == name), None)


def available(inventory):
    """Оружие, которое сейчас можно взять в руки: лом всегда, огнестрел — если он в рюкзаке."""
    return ["melee"] + [k for k, w in WEAPONS.items() if w.get("item") and inventory.has(w["item"])]


def skill_of(player, key):
    """Навык, которым владеют этим оружием (с перками и бонусами снаряжения)."""
    return player.weapon_skill(WEAPONS[key].get("skill", "guns"))


def shortfall(player, key):
    """Сколько очков навыка не хватает до порога оружия (0 — слушается)."""
    return max(0, WEAPONS[key].get("req", 0) - skill_of(player, key))
