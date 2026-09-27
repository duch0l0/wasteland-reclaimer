"""Описания предметов (data/items.json): цена, использование, броня."""
import json

with open("data/items.json", "r", encoding="utf-8") as f:
    ITEMS = json.load(f)


def price(name):
    return ITEMS.get(name, {}).get("price", 0)


def usable(name):
    return "use" in ITEMS.get(name, {})


def armor_ac(inventory):
    """КБ от надетой брони: лучшая из того, что есть в рюкзаке."""
    return max((d.get("armor_ac", 0) for n, d in ITEMS.items() if inventory.has(n)), default=0)
