"""
Каталог объектов карт (data/props.json и data/props/<город>.json) и их картинки: assets/town/props/
(набор «wasteland town» и свои x_*), assets/ruins/props/ (набор «War ruins», r<стр>_<номер>) и
наборы Cute SCKR — assets/packs/<набор>/ (картинки «pk:…», см. pack_image).

Размер пятна на земле (foot) считается по картинке, если не задан явно:
ширина — сколько клеток занимает картинка, глубина — 1 клетка.
Им пользуются и игра (src/townmap.py), и генератор карты (tools/build_town.py).
"""
import json
import os

import pygame

from . import settings as S

PROPS_DIR = os.path.join("assets", "town", "props")
RUINS_DIR = os.path.join("assets", "ruins", "props")

with open("data/props.json", "r", encoding="utf-8") as f:
    _DATA = json.load(f)
CATALOG = _DATA["props"]
LOOT_TABLES = _DATA["loot_tables"]
# объекты городов из наборов Cute SCKR — свой файл на город: data/props/<город>.json ({"props": {...}})
PACK_DIR = os.path.join("assets", "packs")
if os.path.isdir(os.path.join("data", "props")):
    for _fn in sorted(os.listdir(os.path.join("data", "props"))):
        if _fn.endswith(".json"):
            with open(os.path.join("data", "props", _fn), "r", encoding="utf-8") as f:
                CATALOG.update(json.load(f).get("props", {}))

_SIZES = None


def _source_sizes():
    global _SIZES
    if _SIZES is None:
        _SIZES = {}
        for index in (os.path.join("assets", "town", "index.json"), os.path.join("assets", "ruins", "index.json")):
            if os.path.isfile(index):
                with open(index, "r", encoding="utf-8") as f:
                    _SIZES.update({k: v["size"] for k, v in json.load(f).items()})
    return _SIZES


def _img_path(img):
    ruins = img[0] == "r" and img[1:2].isdigit()
    return os.path.join(RUINS_DIR if ruins else PROPS_DIR, img + ".png")


# ------------------------------------------------------------ картинки из наборов (tools/packs.py)
#   pk:<набор>/<имя>             — вырезанный объект, пол или стена (props/, floor/, walls/)
#   pk:<набор>/p<N>/<x>,<y>,<ш>,<в> — кусок страницы N по клеткам 48 (композиции: озеро, дорожка, дом)
_PACK_INDEX = {}
_PAGES = {}


def _pack_index(short):
    if short not in _PACK_INDEX:
        with open(os.path.join(PACK_DIR, short, "index.json"), "r", encoding="utf-8") as f:
            _PACK_INDEX[short] = json.load(f)["items"]
    return _PACK_INDEX[short]


def pack_size(img):
    short, rest = img[3:].split("/", 1)
    if "/" in rest:
        x, y, w, h = (int(v) for v in rest.split("/")[1].split(","))
        return [w * S.TILE, h * S.TILE]
    return _pack_index(short)[rest]["size"]


def pack_image(img):
    """Картинка набора (без масштаба). Страницы кэшируются — куски режутся из них."""
    short, rest = img[3:].split("/", 1)
    if "/" in rest:
        page, cells = rest.split("/")
        key = (short, page)
        if key not in _PAGES:
            _PAGES[key] = pygame.image.load(os.path.join(PACK_DIR, short, "pages", page + ".png")).convert_alpha()
        x, y, w, h = (int(v) for v in cells.split(","))
        return _PAGES[key].subsurface((x * S.TILE, y * S.TILE, w * S.TILE, h * S.TILE)).copy()
    d = _pack_index(short)[rest]
    return pygame.image.load(os.path.join(PACK_DIR, short, d["dir"], rest + ".png")).convert_alpha()


def explosive(obj):
    """Взрывается ли объект карты (красная бочка). Изометрических тайлов в каталоге нет — не взрываются."""
    return obj.get("name") in CATALOG and bool(CATALOG[obj["name"]].get("explosive"))


def info(name):
    """Описание объекта с вычисленными полями: size (px, с масштабом), foot, block, sight, layer."""
    d = CATALOG[name]
    w, h = pack_size(d["img"]) if d["img"].startswith("pk:") else _source_sizes()[d["img"]]
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
        img = pack_image(d["img"]) if d["img"].startswith("pk:") else \
            pygame.image.load(_img_path(d["img"])).convert_alpha()
        if img.get_size() != d["size"]:
            img = pygame.transform.smoothscale(img, d["size"])
        if darken:
            img = img.copy()
            img.fill((150, 140, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
        _IMAGES[key] = img
    return _IMAGES[key]
