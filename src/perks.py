"""
Перки — выбор при повышении уровня (как в Fallout 2).

Каждый перк либо сразу меняет характеристики (apply), либо проверяется
в коде боя через player.perk_rank(id). max_rank > 1 — перк можно брать
несколько раз.
"""
import random


def _more_ap(p):
    p.base_ap += 1


def _thick_skin(p):
    p.ac += 10


def _tough(p):
    p.max_hp += 12
    p.hp += 12


PERKS = [
    {"id": "action_boy", "name": "Шило в одном месте", "max_rank": 2, "apply": _more_ap,
     "desc": "+1 ОД в бою. Сидеть на месте вы никогда не умели."},
    {"id": "bonus_move", "name": "Бонус движения", "max_rank": 1, "apply": None,
     "desc": "Первые 2 шага за ход бесплатные. Ноги сами несут — чаще всего прочь."},
    {"id": "thick_skin", "name": "Толстокожий", "max_rank": 1, "apply": _thick_skin,
     "desc": "+10 к классу брони. Кожа как старый ботинок, запах тоже."},
    {"id": "sharp_eye", "name": "Глаз-алмаз", "max_rank": 1, "apply": None,
     "desc": "+10% к шансу крита. Вы видите слабые места. Особенно чужие."},
    {"id": "heavy_hand", "name": "Тяжёлая рука", "max_rank": 2, "apply": None,
     "desc": "+3 к урону в ближнем бою. Рукопожатия теперь тоже опасны."},
    {"id": "steady_hand", "name": "Верная рука", "max_rank": 2, "apply": None,
     "desc": "+15% к навыку стрельбы. Руки перестали дрожать. Почти."},
    {"id": "tough", "name": "Живучий", "max_rank": 2, "apply": _tough,
     "desc": "+12 к максимуму HP. Пустошь пыталась вас убить — и устала."},
    {"id": "looter", "name": "Мародёр", "max_rank": 1, "apply": None,
     "desc": "С врагов падает вдвое больше добычи. Карманы у мертвецов глубже, чем кажется."},
    {"id": "silver_tongue", "name": "Подвешенный язык", "max_rank": 1, "apply": None,
     "desc": "Открывает реплики [Красноречие] в диалогах, торговля выгоднее на 20%. Слова — тоже оружие, и патроны не нужны."},
    {"id": "scavenger", "name": "Падальщик", "max_rank": 1, "apply": None,
     "desc": "Каждое убийство лечит 5 HP. Не спрашивайте, как именно."},
]
PERKS_BY_ID = {p["id"]: p for p in PERKS}


def roll_choices(player, n=3):
    """n случайных перков, которые игрок ещё может взять."""
    available = [p for p in PERKS if player.perk_rank(p["id"]) < p["max_rank"]]
    return random.sample(available, min(n, len(available)))


def take(player, perk):
    player.perks[perk["id"]] = player.perk_rank(perk["id"]) + 1
    if perk["apply"]:
        perk["apply"](player)
