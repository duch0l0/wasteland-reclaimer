"""
Перки — выбор на чётных уровнях (как в Fallout 2 — не на каждом). Предлагаются три
случайных из доступных: у сильных перков есть порог уровня (min_level) и перк-предшественник
(requires), так что набор от игры к игре разный, а лучшее открывается не сразу.

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


def _skill(skill_id, n):
    def apply(p):
        p.skills[skill_id] = p.skill(skill_id) + n
    return apply


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
    # --- новые: под навыки и оружие
    {"id": "medic", "name": "Полевой медик", "max_rank": 1, "apply": _skill("medicine", 10),
     "desc": "+10 к Медицине, бинты и стимуляторы лечат на 50% больше. Шить по живому — тоже искусство."},
    {"id": "hacker", "name": "Хакер", "max_rank": 1, "apply": _skill("science", 10),
     "desc": "+10 к Науке и +2 попытки взлома терминала. RobCo гордилась бы. Или подала бы в суд."},
    {"id": "ranger", "name": "Следопыт", "max_rank": 1, "apply": _skill("survival", 15),
     "desc": "+15 к Выживанию: в пустоши нападают реже, а засаду видно за милю."},
    {"id": "fast_heal", "name": "Быстрое заживление", "max_rank": 1, "apply": None,
     "desc": "Раны вне боя затягиваются вдвое быстрее. Шрамы — тоже."},
    {"id": "point_blank", "name": "В упор", "max_rank": 1, "apply": None, "min_level": 4,
     "desc": "Дробовик вплотную бьёт на 30% сильнее. Разговор на расстоянии вытянутой руки."},
    {"id": "burst_master", "name": "Автоматчик", "max_rank": 1, "apply": None, "min_level": 4,
     "desc": "Очередь из автомата стоит на 1 ОД меньше, отдача вдвое слабее."},
    {"id": "armor_piercer", "name": "Бронебой", "max_rank": 2, "apply": None, "min_level": 6,
     "desc": "Ваши удары и пули игнорируют 3 единицы брони. Роботы начинают вас уважать."},
    {"id": "sniper", "name": "Снайпер", "max_rank": 1, "apply": None, "min_level": 8, "requires": "sharp_eye",
     "desc": "Прицельный выстрел теряет вдвое меньше точности. Глаза, пах, колено — выбирайте."},
    {"id": "lifegiver", "name": "Жизнелюб", "max_rank": 2, "apply": _tough, "min_level": 6, "requires": "tough",
     "desc": "Ещё +12 к максимуму HP и +2 HP за каждый следующий уровень. Упрямство — тоже здоровье."},
]
PERKS_BY_ID = {p["id"]: p for p in PERKS}


def roll_choices(player, n=3):
    """n случайных перков, которые игрок ещё может взять."""
    lvl = player.level_sys.level
    available = [p for p in PERKS if player.perk_rank(p["id"]) < p["max_rank"]
                 and lvl >= p.get("min_level", 1) and (not p.get("requires") or player.perk_rank(p["requires"]))]
    return random.sample(available, min(n, len(available)))


def take(player, perk):
    player.perks[perk["id"]] = player.perk_rank(perk["id"]) + 1
    if perk["apply"]:
        perk["apply"](player)
