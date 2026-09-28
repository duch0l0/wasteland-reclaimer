"""Описания предметов (data/items.json): категория, иконка, цена, использование, слот брони и бонусы."""
import json

with open("data/items.json", "r", encoding="utf-8") as f:
    ITEMS = json.load(f)

# вкладки рюкзака: (id, подпись, какие категории показывает)
CATEGORY_TABS = [
    ("all", "Все", None),
    ("weapon", "Оружие", {"weapon", "ammo"}),
    ("armor", "Броня", {"armor"}),
    ("meds", "Лечение", {"meds"}),
    ("resource", "Ресурсы", {"resource"}),
    ("misc", "Разное", {"misc"}),
]
CATEGORY_NAMES = {"weapon": "Оружие", "ammo": "Боеприпасы", "armor": "Броня", "meds": "Лечение",
                  "resource": "Ресурс для крафта", "misc": "Разное"}
# порядок в сетке: сначала полезное в бою
CATEGORY_ORDER = ["weapon", "ammo", "armor", "meds", "resource", "misc"]


def price(name):
    return ITEMS.get(name, {}).get("price", 0)


def category(name):
    return ITEMS.get(name, {}).get("cat", "misc")


def icon_id(name):
    return ITEMS.get(name, {}).get("icon", "misc")


def usable(name):
    return "use" in ITEMS.get(name, {})


SLOTS = ("head", "body")  # броня; оружие — отдельно (player.weapon)
SLOT_NAMES = {"head": "Голова", "body": "Тело"}


def slot(name):
    """Куда надевается: "head", "body" или None."""
    return ITEMS.get(name, {}).get("slot")


def mod(name, stat):
    """Бонус предмета к характеристике: armor_ac (КБ), ap (ОД), guns (стрельба)."""
    return ITEMS.get(name, {}).get(stat, 0)
