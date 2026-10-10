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


def soft_edges(img, depth=22):
    """Края картинки растворяются: альфа спадает к краю неровной кромкой (шум по краю), углы скруглены."""
    import math
    import random as _r
    w, h = img.get_size()
    out = img.convert_alpha().copy()
    rnd = _r.Random(w * 31 + h)
    wob = [rnd.uniform(-0.35, 0.35) for _ in range(16)]

    def noise(t):                       # плавный шум вдоль периметра
        x = t * 15
        i = int(x) % 15
        f = x - int(x)
        return wob[i] * (1 - f) + wob[i + 1] * f
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    B = 3
    for py in range(0, h, B):
        for px in range(0, w, B):
            dx, dy = min(px, w - 1 - px), min(py, h - 1 - py)
            if dx >= depth * 1.4 and dy >= depth * 1.4:
                a = 1.0
            else:
                # расстояние до края со скруглёнными углами
                if dx < depth and dy < depth:
                    dist = depth - math.hypot(depth - dx, depth - dy)
                else:
                    dist = min(dx, dy)
                per = (px / w if dy < dx else py / h)
                a = max(0.0, min(1.0, dist / (depth * (1 + noise(per)))))
                a = a * a * (3 - 2 * a)
            mask.fill((255, 255, 255, int(255 * a)), (px, py, B, B))
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def pond_mask(w, h, seed=0, inset=30):
    """Неровное «пятно» пруда: суперэллипс с шумом по краю, отступ от краёв картинки inset px.
    Возвращает функцию (x, y) -> расстояние до берега в px (>0 — внутри воды)."""
    import math
    import random as _r
    rnd = _r.Random(seed)
    k = [rnd.uniform(0, 6.28) for _ in range(4)]
    amp = [rnd.uniform(0.03, 0.07) for _ in range(4)]
    cx, cy = w / 2, h / 2
    rx, ry = w / 2 - inset, h / 2 - inset

    def dist(x, y):
        dx, dy = (x - cx) / rx, (y - cy) / ry
        a = math.atan2(dy, dx)
        wob = 1 + sum(amp[i] * math.sin((i + 2) * a + k[i]) for i in range(4))
        r = (abs(dx) ** 4 + abs(dy) ** 4) ** 0.25          # суперэллипс: прямые берега, круглые углы
        return (wob - r) * min(rx, ry)
    return dist


def pond_edges(img):
    """Вода из куска страницы — как пруд: снаружи пятна прозрачно (видна своя земля), у кромки — полоса
    мокрого песка и тёмная линия берега. Так оазис и озеро не обрываются прямоугольником."""
    w, h = img.get_size()
    out = img.convert_alpha().copy()
    dist = pond_mask(w, h, seed=w * 7 + h)
    B = 3
    sand = (232, 205, 140)
    for py in range(0, h, B):
        for px in range(0, w, B):
            d = dist(px + B / 2, py + B / 2)
            if d <= 0:
                out.fill((0, 0, 0, 0), (px, py, B, B))
            elif d < 6:
                out.fill(sand + (255,), (px, py, B, B))           # песчаный берег
            elif d < 9:
                out.fill((176, 150, 96, 255), (px, py, B, B))     # кромка воды
    return out


def explosive(obj):
    """Взрывается ли объект карты (красная бочка). Изометрических тайлов в каталоге нет — не взрываются."""
    return obj.get("name") in CATALOG and bool(CATALOG[obj["name"]].get("explosive"))


_WORLD_SCALE = None
_KEEP_FOOT = set()


def world_scale(name):
    """Множитель из data/prop_scale.json: декорации в масштабе героя (машины, фасады, лачуги, башни)."""
    global _WORLD_SCALE
    if _WORLD_SCALE is None:
        _WORLD_SCALE = {}
        try:
            with open(os.path.join("data", "prop_scale.json"), encoding="utf-8") as f:
                for k, grp in json.load(f).items():
                    if not k.startswith("_"):
                        for n in grp["names"]:
                            _WORLD_SCALE[n] = grp["scale"]
                            if grp.get("keep_foot"):
                                _KEEP_FOOT.add(n)
        except FileNotFoundError:
            pass
    return _WORLD_SCALE.get(name, 1)


def info(name):
    """Описание объекта с вычисленными полями: size (px, с масштабом), foot, block, sight, layer."""
    d = CATALOG[name]
    w, h = pack_size(d["img"]) if d["img"].startswith("pk:") else _source_sizes()[d["img"]]
    ws = world_scale(name)
    scale = d.get("scale", 1.0) * ws
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    foot = d.get("foot")
    keep = name in _KEEP_FOOT                  # пальма, фонарь: картинка выше, ствол — та же клетка
    if foot and ws != 1 and not keep:          # пятно растёт вместе с картинкой
        foot = [max(1, round(foot[0] * ws)), max(1, round(foot[1] * ws))]
    foot = foot or [max(1, round((size[0] / ws if keep else size[0]) / S.TILE)), 1]
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
            sc = d.get("scale", 1.0) * world_scale(name)   # целый множитель — по пикселям (пиксель-арт не мылится)
            img = pygame.transform.scale(img, d["size"]) if float(sc).is_integer() else \
                pygame.transform.smoothscale(img, d["size"])
        if d.get("soft") == "pond":    # водоём на улице: свой берег, без прямоугольника
            img = pond_edges(img)
        elif d.get("soft"):            # вставка на улице (пятно травы, воронка): края тают в землю
            img = soft_edges(img, d["soft"] if type(d["soft"]) is int else 30)
        if darken:
            img = img.copy()
            img.fill((150, 140, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
        _IMAGES[key] = img
    return _IMAGES[key]
