"""
Каталог объектов карт (data/props.json) и их картинки (assets/town/props/).

Размер пятна на земле (foot) считается по картинке, если не задан явно:
ширина — сколько клеток занимает картинка, глубина — 1 клетка.
Им пользуются и игра (src/townmap.py), и генератор карты (tools/build_town.py).
"""
import json
import os

import pygame

from . import settings as S

PROPS_DIR = os.path.join("assets", "town", "props")

with open("data/props.json", "r", encoding="utf-8") as f:
    _DATA = json.load(f)
CATALOG = _DATA["props"]
LOOT_TABLES = _DATA["loot_tables"]

_SIZES = None


def _source_sizes():
    global _SIZES
    if _SIZES is None:
        with open(os.path.join("assets", "town", "index.json"), "r", encoding="utf-8") as f:
            _SIZES = {k: v["size"] for k, v in json.load(f).items()}
    return _SIZES


def explosive(obj):
    """Взрывается ли объект карты (красная бочка). Изометрических тайлов в каталоге нет — не взрываются."""
    return obj.get("name") in CATALOG and bool(CATALOG[obj["name"]].get("explosive"))


def info(name):
    """Описание объекта с вычисленными полями: size (px, с масштабом), foot, block, sight, layer."""
    d = CATALOG[name]
    w, h = _source_sizes()[d["img"]]
    scale = d.get("scale", 1.0)
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    foot = d.get("foot") or [max(1, round(size[0] / S.TILE)), 1]
    return {**d, "name": name, "size": size, "foot": foot, "block": d.get("block", True),
            "sight": d.get("sight", False), "layer": d.get("layer", "obj")}


_IMAGES = {}


def image(name, darken=False):
    """Картинка объекта в игровом масштабе; darken — обысканный контейнер (чуть темнее)."""
    key = (name, darken)
    if key not in _IMAGES:
        d = info(name)
        img = pygame.image.load(os.path.join(PROPS_DIR, d["img"] + ".png")).convert_alpha()
        if img.get_size() != d["size"]:
            img = pygame.transform.smoothscale(img, d["size"])
        if darken:
            img = img.copy()
            img.fill((150, 140, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
        _IMAGES[key] = img
    return _IMAGES[key]
