"""
Карта из объектов (data/maps/*.json, собирается tools/build_town.py).

  ground   — строки кодов земли: d земля, a асфальт, h/v разметка, g гравий, c бетонный пол,
             _ пустота (чёрная, непроходимо); свои коды — "floors" {код: [картинки «pk:…»]} и
             "walls" {код: стена набора «pk:<набор>/<стена>»} — стена A4: верх с окантовкой и фасад;
             m стальной пол убежища, w мокрый бетон ливнёвки, x скала/толща стены (непроходимо,
             у края над полом рисуется стена — её вид задаёт style: vault / drain);
  portals  — переходы в другую локацию: {"tiles": [[x, y]...], "to": id, "at": [x, y], "label"};
  decals   — плоские пятна на земле [имя, px, py] (центр в пикселях мира);
  props    — объекты [имя, x, y]: x, y — левая верхняя клетка пятна на земле;
  containers — какие объекты обыскиваются и что в них лежит;
  player, exits, enemies, npcs, pickups — точки появления и выходы.

Объекты рисуются вперемешку с персонажами по нижнему краю пятна (кто ниже —
тот ближе к камере), поэтому за высоким шкафом или палаткой можно спрятаться.
Пятна непроходимы, «высокие» объекты (sight) ещё и закрывают обзор в бою.
"""
import hashlib
import json
import os
import random

import math

import pygame

from . import settings as S
from . import loader
from . import lootfill
from . import props as P
from .tilemap import MapBase

T = S.TILE
GROUND_DIR = os.path.join("assets", "town", "ground")
SHOW_ROOF_SIGNS = False


def _dirt_tiles(n=6):
    """Бесшовная земля: пиксельный шум в цветах пятен земли из набора (dirt_patch)."""
    src = pygame.image.load(os.path.join(P.PROPS_DIR, "p1_dirt_patch.png"))
    colors = []
    for y in range(0, src.get_height(), 3):
        for x in range(0, src.get_width(), 3):
            c = src.get_at((x, y))
            if c.a == 255 and 40 < sum(c[:3]) / 3 < 150:
                colors.append(tuple(c[:3]))
    colors.sort(key=sum)
    body = colors[len(colors) // 8: len(colors) * 7 // 8]  # без самых тёмных и светлых пятен
    tiles = []
    rnd = random.Random(11)
    for _ in range(n):
        t = pygame.Surface((T, T))
        for y in range(0, T, 2):  # пиксели 2×2 — в тон пиксель-арту
            for x in range(0, T, 2):
                t.fill(rnd.choice(body), (x, y, 2, 2))
        for _ in range(3):  # пара камешков
            x, y = rnd.randrange(2, T - 4, 2), rnd.randrange(2, T - 4, 2)
            t.fill(colors[-rnd.randrange(1, len(colors) // 10 + 2)], (x, y, 2, 2))
            t.fill(colors[rnd.randrange(0, len(colors) // 10 + 1)], (x, y + 2, 2, 2))
        tiles.append(t)
    return tiles


def _noise_tiles(src, n=6):
    """Бесшовная земля в цветах картинки src: пиксели 2×2 средними тонами, редкие тёмные и светлые крапины."""
    w, h = src.get_size()
    colors = sorted((tuple(src.get_at((x, y))[:3]) for y in range(0, h, 2) for x in range(0, w, 2)
                     if src.get_at((x, y)).a == 255), key=sum)
    body = colors[len(colors) // 5: len(colors) * 4 // 5] or colors
    rnd = random.Random(len(colors))
    out = []
    for _ in range(n):
        t = pygame.Surface((T, T))
        for y in range(0, T, 2):
            for x in range(0, T, 2):
                t.fill(rnd.choice(body), (x, y, 2, 2))
        for _ in range(3):
            x, y = rnd.randrange(2, T - 4, 2), rnd.randrange(2, T - 4, 2)
            t.fill(colors[rnd.randrange(0, max(1, len(colors) // 10))], (x, y, 2, 2))
            t.fill(colors[-rnd.randrange(1, max(2, len(colors) // 10))], (x, y - 2, 2, 2))
        out.append(t.convert())
    return out


def _pixel_tile(palette, seed, detail=None):
    rnd = random.Random(seed)
    t = pygame.Surface((T, T))
    for y in range(0, T, 2):
        for x in range(0, T, 2):
            t.fill(rnd.choice(palette), (x, y, 2, 2))
    if detail:
        detail(t, rnd)
    return t


def _vault_floor():
    """Стальные плиты пола убежища: сетка швов, заклёпки по углам."""
    def plates(t, rnd):
        pygame.draw.rect(t, (52, 58, 66), (0, 0, T, T), 2)
        for cx, cy in ((5, 5), (T - 6, 5), (5, T - 6), (T - 6, T - 6)):
            t.fill((150, 156, 164), (cx, cy, 2, 2))
        if rnd.random() < 0.3:
            t.fill((70, 76, 84), (rnd.randrange(8, T - 16), rnd.randrange(8, T - 8), 10, 2))
    return [_pixel_tile([(96, 102, 110), (100, 106, 114), (92, 98, 106), (104, 110, 118)], s, plates) for s in range(4)]


def _drain_floor():
    """Мокрый бетон ливнёвки: тёмный, с зеленцой и потёками."""
    def wet(t, rnd):
        for _ in range(3):
            x, y = rnd.randrange(0, T - 8, 2), rnd.randrange(0, T - 4, 2)
            t.fill((44, 58, 46), (x, y, rnd.choice((6, 8, 10)), 2))
    return [_pixel_tile([(62, 66, 60), (58, 62, 56), (66, 70, 62), (54, 60, 54)], s, wet) for s in range(4)]


# кромка массивов стиля: (затемнение вглубь, бордюр, блик, тень под бордюром) — в цвет фасадов _wall_faces
SLAB_RIM = {
    "drain": ((88, 88, 80), (112, 112, 102), (150, 150, 136), (40, 40, 37)),
    "vault": ((78, 86, 100), (96, 106, 122), (134, 146, 164), (34, 36, 42)),
}


def _rock_tiles():
    """Толща скалы/стены — почти чёрная, чтобы коридоры читались сверху."""
    return [_pixel_tile([(18, 16, 16), (22, 20, 19), (16, 14, 14), (26, 23, 21)], s) for s in range(3)]


def _wall_faces(style):
    """Лицевая сторона стены над полом (вид три четверти)."""
    out = []
    for seed in range(3):
        rnd = random.Random(seed + 7)
        t = pygame.Surface((T, T))
        if style == "vault":
            t.fill((70, 78, 90))
            pygame.draw.rect(t, (86, 96, 110), (0, 0, T, 14))
            for x in range(0, T, 12):                           # панели с рёбрами
                t.fill((56, 62, 72), (x, 14, 2, T - 14))
            for x in range(0, T, 8):                            # жёлто-синяя полоса Vault-Tec
                t.fill((226, 186, 52) if (x // 8) % 2 == 0 else (44, 80, 150), (x, 30, 8, 5))
            t.fill((30, 32, 38), (0, T - 4, T, 4))
        elif style == "drain":
            t.fill((78, 78, 72))
            for y in range(0, T, 12):                           # бетонные кольца
                t.fill((64, 64, 60), (0, y, T, 2))
            for _ in range(4):
                x = rnd.randrange(0, T - 2, 2)
                t.fill((54, 74, 52), (x, rnd.randrange(16, 30), 2, rnd.randrange(8, 18)))  # тина
            t.fill((34, 34, 32), (0, T - 4, T, 4))
        else:
            t.fill((100, 84, 62))
            t.fill((70, 56, 42), (0, T - 4, T, 4))
        out.append(t)
    return out


_EDGE_MASKS = {}


def _edge_mask(mask, variant):
    """Белая маска с альфой: 255 у сторон клетки из mask (биты: верх, право, низ, лево),
    к центру спадает до 0; кромка неровная. 4 варианта шума на каждую комбинацию сторон."""
    key = (mask, variant)
    if key not in _EDGE_MASKS:
        rnd = random.Random(mask * 31 + variant)
        m = pygame.Surface((T, T), pygame.SRCALPHA)
        depth = 20
        wobble = {}
        for bit in range(4):
            pts = [rnd.uniform(-7, 9) for _ in range(6)]
            wobble[bit] = [pts[i * 5 // T] + (pts[i * 5 // T + 1] - pts[i * 5 // T]) * ((i * 5 / T) % 1) for i in range(T)]
        for py in range(0, T, 2):
            for px in range(0, T, 2):
                a = 0.0
                for bit, (dist, along) in enumerate(((py, px), (T - 1 - px, py), (T - 1 - py, px), (px, py))):
                    if mask & (1 << bit):
                        a = max(a, 1 - dist / max(1.0, depth + wobble[bit][along]))
                a = max(0.0, min(1.0, a * 1.15 + rnd.uniform(-0.12, 0.12)))
                m.fill((255, 255, 255, int(255 * a ** 1.3)), (px, py, 2, 2))
        _EDGE_MASKS[key] = m
    return _EDGE_MASKS[key]


def _crop_frame(img, k=3):
    """Тайл с тёмной каймой по краю (плитка грунта в наборе нарисована «кирпичиком») — без каймы:
    если край заметно темнее середины, берём середину и растягиваем обратно."""
    w, h = img.get_size()
    if w < 24 or h < 24:
        return img
    mid = pygame.transform.average_color(img, (k, k, w - 2 * k, h - 2 * k))[:3]
    edge = [pygame.transform.average_color(img, r)[:3] for r in ((0, 0, w, 2), (0, h - 2, w, 2), (0, 0, 2, h), (w - 2, 0, 2, h))]
    dark = sum(sum(mid) - sum(e) for e in edge) / 4
    if dark < 24:
        return img
    return pygame.transform.scale(img.subsurface((k, k, w - 2 * k, h - 2 * k)), (w, h))


def _even_tone(tiles):
    """Варианты одной земли с разной яркостью (марсианский грунт, плитка) лежат «шахматкой». Каждый вариант
    подтягивается к среднему цвету группы: узор остаётся разным, пятна по сетке пропадают."""
    if len(tiles) < 2:
        return tiles
    avgs = [pygame.transform.average_color(t)[:3] for t in tiles]
    mean = [sum(a[i] for a in avgs) / len(avgs) for i in range(3)]
    out = []
    for t, a in zip(tiles, avgs):
        k = [mean[i] / max(1, a[i]) for i in range(3)]
        if all(abs(x - 1) < 0.03 for x in k):
            out.append(t)
            continue
        t = t.copy()
        if all(x <= 1 for x in k):
            t.fill(tuple(min(255, int(255 * x)) for x in k), special_flags=pygame.BLEND_RGB_MULT)
        else:                                   # светлее нужно: доля прибавкой
            add = tuple(max(0, int(mean[i] - a[i])) for i in range(3))
            sub = tuple(max(0, int(a[i] - mean[i])) for i in range(3))
            t.fill(add, special_flags=pygame.BLEND_RGB_ADD)
            t.fill(sub, special_flags=pygame.BLEND_RGB_SUB)
        out.append(t)
    return out


WALL_LIFT = T   # стены высотой в две клетки: верх стены на клетку выше её основания


_ROOF_TEX = {}
ROOF_TEXTURES = {"planks": ["pk:fishv/p3/9,0,1,1"],
                 "concrete": ["pk:mbase/p1/0,0,1,1", "pk:mbase/p1/1,0,1,1"],
                 "metal": ["pk:mbase/p1/4,0,1,1", "pk:mbase/p1/5,0,1,1"],
                 "brick": ["pk:wrail/p1/2,3,1,1", "pk:wrail/p1/3,3,1,1"]}
ROOF_TINT = {"brick": (200, 175, 150), "concrete": (225, 222, 215), "metal": (255, 245, 236), "planks": (230, 220, 210)}


def _roof_texture(style):
    """Плитки крыши из наборов (src/townmap.py ROOF_TEXTURES); None — нет набора, рисуется шумом."""
    if style not in _ROOF_TEX:
        try:
            out = []
            for ref in ROOF_TEXTURES.get(style, []):
                t = pygame.transform.scale(P.pack_image(ref), (T, T)).convert()
                t.fill(ROOF_TINT.get(style, (255, 255, 255)), special_flags=pygame.BLEND_RGB_MULT)
                out.append(t)
            _ROOF_TEX[style] = out or None
        except Exception:      # набора нет в сборке — шум, как раньше
            _ROOF_TEX[style] = None
    return _ROOF_TEX[style]


ROOF_THEMES = {
    "clinic": ("КЛИНИК", "+"), "sheriff": ("ШЕРИФ", "★", "КОМАНДОВАНИЕ"), "water": ("ВОДА", "КУПАЛЬНИ"),
    "tavern": ("САЛУН", "ТРАПЕЗНАЯ", "ГРЕК", "БЕЗУМНЫЙ"), "motel": ("МОТЕЛЬ", "HOTEL", "ЗАМОК"), "shop": ("MART", "ЛАВКА"),
    "show": ("МИРАЖ", "Ω", "КАЗИНО"), "works": ("ГАРАЖ", "ДЕПО", "FREIGHT", "ЗАПРАВКА", "КОНТОРА", "АНГАР", "РОЙ"),
    "hall": ("СОВЕТ", "ЕДИНСТВО", "КЕЛЬИ")}
THEME_KINDS = {   # что чаще встречается на крыше такого здания (прочее — общее)
    "clinic": ("vent", "vent", "sky", "sky", "ac", "hatch"), "sheriff": ("antenna", "antenna", "solar", "vent", "sandbags"),
    "water": ("tank", "tank", "pipe", "pipe", "hatch"), "tavern": ("chimney", "chimney", "barrel", "barrel", "lights", "crates"),
    "motel": ("ac", "ac", "ac", "vent", "dish", "laundry"), "shop": ("crates", "crates", "tarp", "sky", "ac"),
    "show": ("antenna", "antenna", "sky", "lights", "dish"), "works": ("sky", "sky", "vent", "pipe", "crates", "junk", "ac"),
    "hall": ("sky", "dish", "pots", "vent"),
    "home_a": ("laundry", "pots", "barrel", "dish", "chimney"), "home_b": ("dish", "ac", "pots", "tarp", "antenna"),
    "home_c": ("barrel", "chimney", "crates", "laundry", "vent")}
THEME_SIG = {   # фирменная деталь крыши, ставится один раз
    "clinic": ("cross",), "sheriff": ("flag",), "water": ("tank",), "tavern": ("chimney",), "motel": ("sign_frame",),
    "shop": ("sign_frame",), "show": ("sign_frame",), "works": ("mast",), "hall": ("flag",)}


def _roof_theme(r):
    text = (r.get("sign") or "").upper()
    for th, keys in ROOF_THEMES.items():
        if any(k in text for k in keys):
            return th
    return ("home_a", "home_b", "home_c")[r["seed"] % 3]


def _roof_image(r):
    """Крыша по стилю здания, в пиксель-арте 2×2: рубероид с гравием и вентиляцией (кирпич),
    ржавый профнастил (металл), доски (дерево), бетонная плита (бетон). С парапетом."""
    w, h = (r["x1"] - r["x0"] + 1) * T, (r["y1"] - r["y0"]) * T - WALL_LIFT
    rnd = random.Random(r["seed"])
    style = r["style"]
    pal = {"brick": [(118, 94, 78), (124, 100, 82), (112, 89, 74), (130, 106, 88)],
           "concrete": [(118, 116, 110), (124, 122, 116), (110, 108, 104), (130, 127, 120)],
           "metal": [(132, 96, 74), (142, 104, 80), (122, 88, 68), (152, 112, 86)],
           "planks": [(104, 78, 54), (112, 84, 58), (96, 72, 50), (120, 90, 62)]}[style]
    img = pygame.Surface((w, h), pygame.SRCALPHA)
    tex = _roof_texture(style) if style in ("planks", "metal") else None      # плоские крыши — гудрон с гравием, без сетки плиток
    if tex is not None and style in ("planks", "metal"):
        # дранка и кровельный лист: ряды со смещёнными стыками и разбросом тона — без сетки плиток набора
        base = tuple(pygame.transform.average_color(tex[0])[:3])
        if style == "metal":                                  # профнастил светлее и теплее: ржавая жесть, а не тёмная плита
            base = tuple(min(255, int(c * 1.32) + (12 if i == 0 else 4 if i == 1 else 0)) for i, c in enumerate(base))
        pal = [base] * 4
        img.fill(tuple(int(c * 0.78) for c in base) + (255,))      # подложка: между дранками нет прозрачных щелей
        # плоские крыши: дерево — настил из длинных досок вдоль крыши, металл — листы кровельного железа со швами
        if style == "planks":
            rowh, sw = 12, 90
        else:
            rowh, sw = 60, 60
        for ry, y in enumerate(range(0, h, rowh)):
            off = (ry * 37 + r["seed"]) % sw
            for sx in range(-off, w, sw):
                k = rnd.uniform(0.9, 1.08)
                col = tuple(max(0, min(255, int(c * k))) for c in base)
                img.fill(col, (max(0, sx), y, min(sw, w - max(0, sx)) - (1 if sx >= 0 else 0), rowh - 1))
                if style == "planks" and rnd.random() < 0.08:        # сучок
                    img.fill(tuple(int(c * 0.7) for c in base), (max(0, sx) + rnd.randrange(8, 70), y + 4, 5, 3))
                if style == "metal":                                  # рёбра жёсткости на листе
                    for rx in range(max(0, sx) + 10, min(w, sx + sw) - 4, 12):
                        img.fill(tuple(min(255, int(c * 1.12)) for c in base), (rx, y + 2, 2, rowh - 5))
                        img.fill(tuple(int(c * 0.8) for c in base), (rx + 2, y + 2, 1, rowh - 5))
            img.fill(tuple(int(c * 0.6) for c in base), (0, y + rowh - 1, w, 1))
    elif tex is not None:        # крыша из настоящей текстуры набора (бетонные плиты, гудрон)
        for y in range(0, h, T):
            for x in range(0, w, T):
                img.blit(tex[((x // T) * 7 + (y // T) * 3 + r["seed"]) % len(tex)], (x, y))
        pal = [tuple(pygame.transform.average_color(tex[0])[:3])] * 4
    for y in range(0, h, 2) if tex is None else ():
        for x in range(0, w, 2):
            c = rnd.choice(pal)
            if style == "metal":                      # профнастил: продольные волны
                c = pal[3] if (x // 6) % 2 else pal[2]
                if rnd.random() < 0.05:
                    c = (150, 96, 60)
            elif style == "planks":                   # доски поперёк, со щелями
                if y % 16 in (14,):
                    c = (60, 44, 32)
                elif (x + (y // 16) * 37) % 96 < 2:
                    c = (70, 52, 36)
            img.fill(c, (x, y, 2, 2))
    if style in ("brick", "concrete") and tex is None:   # гравий и пятна
        for _ in range(w * h // 900):
            x, y = rnd.randrange(0, w - 6, 2), rnd.randrange(0, h - 6, 2)
            img.fill(tuple(max(0, v - 18) for v in pal[0]), (x, y, rnd.choice((4, 6, 8)), rnd.choice((2, 4))))
    if style in ("brick", "concrete"):                # рубероид: полосы полотен с нахлёстом, заплаты, тёмные подтёки, швы
        sw = 54
        for k, sx in enumerate(range(0, w, sw)):
            tone = rnd.choice((-6, -3, 0, 4))
            if tone:
                img.fill(tuple(max(0, min(255, c + tone)) for c in pal[0]) + (255,), (sx, 8, sw - 2, h - 16), special_flags=0)
            pygame.draw.line(img, tuple(max(0, c - 38) for c in pal[0]), (sx, 8), (sx, h - 8), 2)
            pygame.draw.line(img, tuple(min(255, c + 22) for c in pal[3]), (sx + 2, 8), (sx + 2, h - 8), 1)
        for _ in range(max(2, w * h // 12000)):        # заплаты чуть темнее/светлее полотна, с прибитой кромкой
            bw, bh = rnd.randrange(30, 64, 2), rnd.randrange(24, 44, 2)
            x, y = rnd.randrange(12, max(13, w - bw - 12), 2), rnd.randrange(12, max(13, h - bh - 12), 2)
            d = rnd.choice((-12, 10))                       # один сдвиг на все каналы — тон, а не цвет
            c = tuple(max(0, min(255, v + d)) for v in pal[0])
            pygame.draw.rect(img, c, (x, y, bw, bh))
            pygame.draw.rect(img, tuple(max(0, v - 26) for v in c), (x, y, bw, bh), 1)
    if style == "metal" and tex is None:              # ржавые потёки
        for _ in range(w // 40):
            x = rnd.randrange(0, w, 2)
            img.fill((90, 48, 32), (x, rnd.randrange(0, h // 2), 2, rnd.randrange(h // 4, h // 2)))
    # объём и износ: двускатная крыша (дерево, металл) — светлый скат и тёмный скат со коньком;
    # плоская (кирпич, бетон) — пятна выцветания и потёки, чтобы плитка не читалась сеткой
    shade = pygame.Surface((w, h), pygame.SRCALPHA)
    if False:
        mid = h // 2
        shade.fill((255, 255, 255, 26), (0, 0, w, mid))
        shade.fill((0, 0, 0, 44), (0, mid, w, h - mid))
        shade.fill((20, 14, 10, 150), (0, mid - 2, w, 4))             # конёк
        shade.fill((255, 235, 200, 70), (0, mid - 4, w, 2))
        for k in range(0, w, T * 2) if style == "metal" else ():         # стыки листов на скатах
            shade.fill((0, 0, 0, 26), (k, 0, 2, h))
    else:
        for _ in range(max(3, w * h // 4000)):
            bw, bh = rnd.randrange(24, 90), rnd.randrange(16, 60)
            x, y = rnd.randrange(0, max(1, w - bw)), rnd.randrange(0, max(1, h - bh))
            pygame.draw.ellipse(shade, (0, 0, 0, rnd.choice((8, 12, 16))) if rnd.random() < 0.6
                                else (255, 255, 255, 8), (x, y, bw, bh))
        for _ in range(max(2, w // 60)):                               # потёки под парапетом
            x = rnd.randrange(8, max(9, w - 8), 2)
            shade.fill((0, 0, 0, 30), (x, 6, 4, rnd.randrange(h // 6, h // 3)))
    img.blit(shade, (0, 0))
    if False:                                             # скатные крыши отключены: все крыши плоские
        mid = h // 2
        ridge = pygame.Surface((w, 8), pygame.SRCALPHA)
        ridge.fill((52, 40, 30, 255))
        pygame.draw.rect(ridge, (150, 122, 92, 255), (0, 0, w, 3))
        pygame.draw.rect(ridge, (96, 74, 54, 255), (0, 3, w, 2))
        img.blit(ridge, (0, mid - 4))
        cast = pygame.Surface((w, 16), pygame.SRCALPHA)
        for yy in range(16):
            cast.fill((0, 0, 0, int(64 * (1 - yy / 16))), (0, yy, w, 1))
        img.blit(cast, (0, mid + 4))                       # тень конька на южном скате
        for _ in range(max(2, w // 70)):                   # потёки ржавчины / тёмные разводы по скату
            x = rnd.randrange(8, max(9, w - 8), 2)
            ln = rnd.randrange(14, 36)
            ys = rnd.randrange(mid + 8, max(mid + 9, h - ln - 6))
            col = (96, 52, 32, 70) if style == "metal" else (30, 22, 16, 60)
            sg = pygame.Surface((3, ln), pygame.SRCALPHA)
            sg.fill(col)
            img.blit(sg, (x, ys))
        for _ in range(max(1, w // 140)):                  # пятна мха на северном, влажном скате
            mx, my = rnd.randrange(12, max(13, w - 40)), rnd.randrange(10, max(11, mid - 18))
            ms = pygame.Surface((rnd.choice((22, 30, 38)), rnd.choice((10, 14))), pygame.SRCALPHA)
            pygame.draw.ellipse(ms, (64, 92, 52, 80), ms.get_rect())
            img.blit(ms, (mx, my))
    if False and style in ("planks", "metal") and w >= 6 * T:      # большая двускатная крыша: слуховые окна, печные трубы, водосток
        mid = h // 2
        for k in range(max(2, w // (4 * T))):
            cx = int((k + 0.5) * w / max(2, w // (4 * T))) + rnd.randrange(-10, 11, 2)
            ytop = mid + 14 + (rnd.randrange(0, 3) * 2)
            if k % 2 == 0:                                   # слуховое окно с козырьком
                pygame.draw.rect(img, (46, 34, 26), (cx - 17, ytop + 3, 34, 30))
                pygame.draw.rect(img, (92, 70, 52), (cx - 17, ytop, 34, 8))
                pygame.draw.rect(img, (28, 30, 38), (cx - 11, ytop + 12, 22, 16))
                img.fill((78, 96, 120), (cx - 9, ytop + 14, 8, 6))
                img.fill((78, 96, 120), (cx + 1, ytop + 14, 8, 6))
                img.fill((60, 42, 30), (cx - 1, ytop + 12, 2, 16))
            else:                                            # кирпичная труба
                pygame.draw.rect(img, (40, 30, 24), (cx - 11, mid - 40, 24, 34))
                pygame.draw.rect(img, (128, 78, 62), (cx - 12, mid - 44, 22, 36))
                for yy in range(mid - 40, mid - 10, 6):
                    img.fill((96, 58, 46), (cx - 12, yy, 22, 1))
                pygame.draw.rect(img, (34, 28, 26), (cx - 14, mid - 48, 28, 6))
        img.fill((34, 26, 20), (6, h - 14, w - 12, 4))        # жёлоб по нижней кромке
        img.fill((120, 98, 76), (6, h - 18, w - 12, 2))
    # оборудование на крыше: кондиционеры, световые люки, баки, солнечные панели, антенны, заплаты, трубы — по площади,
    # без наложения; на скатных крышах (дерево, металл) — только то, что уместно на скате
    pitched = False
    DETAIL_SC = 1.7                                   # детали рисуются на уменьшенном слое и растягиваются — крупнее и читаются
    real_img, real_w, real_h = img, w, h
    w, h = int(real_w / DETAIL_SC), int(real_h / DETAIL_SC)
    img = pygame.Surface((w, h), pygame.SRCALPHA)
    used = []

    def free(x, y, bw, bh):
        r2 = pygame.Rect(x - 8, y - 8, bw + 16, bh + 16)
        if r2.collidelist(used) >= 0:
            return False
        used.append(pygame.Rect(x, y, bw, bh))
        return True

    def shadow(x, y, bw, bh):
        sh = pygame.Surface((bw + 6, bh + 6), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 70))
        img.blit(sh, (x + 3, y + 5))
    theme = _roof_theme(r)
    flat_kinds = THEME_KINDS.get(theme, ()) * 2 + ("ac", "sky", "vent", "hatch", "tarp", "pipe", "antenna", "junk")
    sloped_kinds = flat_kinds
    SIZES = {"ac": (36, 28), "sky": (30, 22), "tank": (30, 30), "solar": (44, 30), "vent": (22, 18), "hatch": (20, 18),
             "pipe": (rnd.choice((60, 84)), 8), "antenna": (14, 14), "junk": (30, 12), "patch": (rnd.choice((28, 40)), 14),
             "tarp": (rnd.choice((40, 54)), rnd.choice((26, 34))), "cross": (40, 40), "flag": (30, 26), "chimney": (22, 22),
             "barrel": (26, 18), "lights": (rnd.choice((90, 120)), 8), "crates": (34, 24), "dish": (24, 24), "laundry": (rnd.choice((70, 96)), 20),
             "pots": (34, 14), "sign_frame": (rnd.choice((70, 90)), 22), "mast": (16, 16), "sandbags": (34, 14)}

    def place(kind):
        bw, bh = SIZES[kind]
        if w < bw + 24 or h < bh + 28:
            return None
        for _try in range(14):
            x, y = rnd.randrange(12, w - bw - 12, 2), rnd.randrange(12, h - bh - 16, 2)
            if free(x, y, bw, bh):
                return x, y, bw, bh
        return None

    todo = [("sig", k) for k in THEME_SIG.get(theme, ())]
    todo += [("rnd", None)] * max(2, (w * h) // (T * T * 3))
    for mode, sigkind in todo:
        kind = sigkind if mode == "sig" else rnd.choice(flat_kinds)
        spot = place(kind)
        if spot is None:
            continue
        x, y, bw, bh = spot
        if kind == "ac":                                          # кондиционер: короб, решётка вентилятора, тень
            shadow(x, y, bw, bh)
            pygame.draw.rect(img, (74, 78, 84), (x, y, bw, bh))
            pygame.draw.rect(img, (156, 160, 166), (x + 1, y + 1, bw - 2, bh - 5))
            pygame.draw.circle(img, (60, 62, 68), (x + bw // 2, y + bh // 2 - 2), 9)
            pygame.draw.circle(img, (110, 114, 120), (x + bw // 2, y + bh // 2 - 2), 7)
            for k in range(-6, 7, 3):
                pygame.draw.line(img, (70, 72, 78), (x + bw // 2 - 6, y + bh // 2 - 2 + k // 2), (x + bw // 2 + 6, y + bh // 2 - 2 - k // 2))
            img.fill((92, 96, 102), (x + 1, y + bh - 4, bw - 2, 3))
        elif kind == "sky":                                       # световой люк: рама и два стекла с бликом
            shadow(x, y, bw, bh)
            pygame.draw.rect(img, (52, 52, 56), (x, y, bw, bh))
            for gx in (x + 3, x + bw // 2 + 1):
                pygame.draw.rect(img, (112, 150, 170), (gx, y + 3, bw // 2 - 4, bh - 6))
                pygame.draw.line(img, (200, 226, 236), (gx + 2, y + bh - 6), (gx + bw // 2 - 6, y + 5))
        elif kind == "tank":                                      # бак: круг с обручами, вид сверху
            shadow(x, y, bw, bh)
            pygame.draw.circle(img, (64, 48, 36), (x + 15, y + 15), 15)
            pygame.draw.circle(img, (122, 94, 66), (x + 15, y + 15), 13)
            pygame.draw.circle(img, (92, 70, 50), (x + 15, y + 15), 9, 2)
            pygame.draw.circle(img, (60, 62, 66), (x + 15, y + 15), 3)
        elif kind == "solar":                                     # солнечные панели: синяя сетка на каркасе
            shadow(x, y, bw, bh)
            pygame.draw.rect(img, (50, 52, 58), (x, y, bw, bh))
            for gx in range(x + 2, x + bw - 4, 14):
                pygame.draw.rect(img, (46, 72, 120), (gx, y + 2, 12, bh - 4))
                pygame.draw.line(img, (110, 144, 190), (gx + 1, y + 3), (gx + 10, y + 3))
                pygame.draw.line(img, (28, 44, 80), (gx + 6, y + 2), (gx + 6, y + bh - 3))
                pygame.draw.line(img, (28, 44, 80), (gx, y + bh // 2), (gx + 11, y + bh // 2))
        elif kind == "vent":                                      # короб вентиляции
            shadow(x, y, bw, bh)
            pygame.draw.rect(img, (64, 66, 70), (x, y + 4, bw, bh - 4))
            pygame.draw.rect(img, (140, 142, 146), (x, y, bw, bh - 4))
            for k in range(3, bw - 2, 4):
                img.fill((90, 92, 96), (x + k, y + 3, 2, bh - 10))
        elif kind == "hatch":                                     # люк
            pygame.draw.rect(img, (50, 44, 38), (x, y, bw, bh))
            pygame.draw.rect(img, (110, 100, 88), (x + 2, y + 2, bw - 4, bh - 4))
            img.fill((70, 62, 54), (x + 2, y + bh // 2 - 1, bw - 4, 2))
        elif kind == "tarp":                                      # брезент заплатой, прижат кирпичами
            c = rnd.choice(((78, 86, 88), (84, 88, 70), (104, 82, 68), (92, 80, 72)))
            pygame.draw.rect(img, tuple(max(0, v - 30) for v in c), (x, y, bw, bh))
            pygame.draw.rect(img, c, (x + 1, y + 1, bw - 2, bh - 3))
            for k in range(6, bw - 4, 9):
                pygame.draw.line(img, tuple(max(0, v - 18) for v in c), (x + k, y + 2), (x + k - 3, y + bh - 4))
            for cx2, cy2 in ((x + 3, y + 3), (x + bw - 7, y + 3), (x + 3, y + bh - 7), (x + bw - 7, y + bh - 7)):
                pygame.draw.rect(img, (138, 98, 78), (cx2, cy2, 5, 4))
        elif kind == "pipe":                                      # труба с коленом и хомутами
            pygame.draw.rect(img, (50, 52, 56), (x, y + 2, bw, 7))
            pygame.draw.rect(img, (136, 138, 142), (x, y, bw, 6))
            img.fill((190, 192, 196), (x, y + 1, bw, 1))
            for k in range(8, bw - 4, 18):
                img.fill((70, 72, 76), (x + k, y - 1, 3, 9))
        elif kind == "antenna":                                   # антенна: основание и растяжки
            shadow(x, y, 8, 8)
            pygame.draw.rect(img, (70, 70, 74), (x + 3, y + 3, 8, 8))
            pygame.draw.line(img, (190, 192, 196), (x + 7, y + 7), (x + 7, y - 6), 2)
            pygame.draw.line(img, (150, 152, 156), (x + 2, y - 2), (x + 12, y - 2))
            for ex, ey in ((x - 6, y + 14), (x + 20, y + 14), (x + 7, y + 22)):
                pygame.draw.line(img, (110, 112, 116), (x + 7, y + 7), (ex, ey))
        elif kind == "patch":                                     # заплата из других листов/дранки на скате
            c = tuple(min(255, int(v * rnd.choice((0.72, 1.16)))) for v in pal[0])
            pygame.draw.rect(img, c, (x, y, bw, bh))
            pygame.draw.rect(img, tuple(max(0, v - 30) for v in c), (x, y, bw, bh), 1)
        elif kind == "cross":                                     # красный крест на белой плите — «здесь клиника»
            pygame.draw.rect(img, (214, 210, 200), (x, y, bw, bh))
            pygame.draw.rect(img, (120, 116, 110), (x, y, bw, bh), 2)
            pygame.draw.rect(img, (196, 40, 36), (x + 15, y + 6, 10, 28))
            pygame.draw.rect(img, (196, 40, 36), (x + 6, y + 15, 28, 10))
        elif kind == "flag":                                      # флагшток: тень полотна и полотно со звездой/полосой
            shadow(x, y, bw, bh)
            pygame.draw.line(img, (60, 50, 40), (x + 2, y + 2), (x + 2, y + bh), 2)
            pygame.draw.polygon(img, (176, 48, 44), [(x + 4, y + 2), (x + bw, y + 6), (x + bw - 3, y + 16), (x + 4, y + 14)])
            pygame.draw.rect(img, (236, 228, 200), (x + 8, y + 5, 8, 6))
        elif kind == "chimney":                                   # кирпичная труба с дымом (тёмное пятно)
            shadow(x, y, bw, bh)
            pygame.draw.rect(img, (84, 56, 46), (x, y, bw, bh))
            pygame.draw.rect(img, (132, 84, 66), (x + 1, y + 1, bw - 2, bh - 3))
            for ry in range(y + 5, y + bh - 2, 5):
                pygame.draw.line(img, (98, 62, 50), (x + 1, ry), (x + bw - 2, ry))
            pygame.draw.rect(img, (28, 24, 22), (x + 5, y + 5, bw - 10, bh - 10))
            sm = pygame.Surface((26, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(sm, (50, 48, 46, 70), sm.get_rect())
            img.blit(sm, (x - 2, y - 14))
        elif kind == "barrel":                                    # бочки с водой, вид сверху
            for k2 in range(2):
                cx2 = x + 7 + k2 * 13
                pygame.draw.circle(img, (46, 52, 60), (cx2 + 1, y + 10), 8)
                pygame.draw.circle(img, (88, 104, 124), (cx2, y + 9), 7)
                pygame.draw.circle(img, (120, 150, 176), (cx2, y + 9), 4)
        elif kind == "lights":                                    # гирлянда лампочек поперёк крыши
            pygame.draw.line(img, (40, 34, 30), (x, y + 4), (x + bw, y + 4))
            for lx in range(x + 4, x + bw - 2, 12):
                pygame.draw.circle(img, rnd.choice(((255, 214, 120), (255, 160, 110), (180, 230, 255))), (lx, y + 5), 3)
        elif kind == "crates":                                    # штабель ящиков под брезентом
            shadow(x, y, bw, bh)
            for k2, (cx2, cy2) in enumerate(((0, 0), (17, 2), (8, 12))):
                pygame.draw.rect(img, (66, 46, 30), (x + cx2, y + cy2, 16, 12))
                pygame.draw.rect(img, (140, 104, 70), (x + cx2 + 1, y + cy2 + 1, 14, 9))
                pygame.draw.line(img, (96, 70, 46), (x + cx2 + 1, y + cy2 + 5), (x + cx2 + 14, y + cy2 + 5))
        elif kind == "dish":                                      # тарелка спутниковой антенны
            shadow(x, y, bw, bh)
            pygame.draw.circle(img, (80, 84, 90), (x + 12, y + 12), 11)
            pygame.draw.circle(img, (188, 192, 198), (x + 12, y + 11), 10)
            pygame.draw.circle(img, (140, 144, 150), (x + 12, y + 11), 5)
            pygame.draw.line(img, (60, 62, 66), (x + 12, y + 11), (x + 19, y + 3), 2)
        elif kind == "laundry":                                   # бельё на верёвке: цветные прямоугольники
            pygame.draw.line(img, (60, 52, 44), (x, y + 3), (x + bw, y + 3))
            xx = x + 4
            while xx < x + bw - 10:
                cw = rnd.choice((8, 10, 12))
                pygame.draw.rect(img, rnd.choice(((214, 206, 190), (150, 80, 70), (84, 110, 150), (186, 164, 96), (96, 120, 88))), (xx, y + 4, cw, rnd.choice((10, 14))))
                xx += cw + 5
        elif kind == "pots":                                      # горшки с зеленью
            for k2 in range(3):
                cx2 = x + 6 + k2 * 11
                pygame.draw.circle(img, (84, 52, 38), (cx2, y + 8), 5)
                pygame.draw.circle(img, (70, 120, 64), (cx2, y + 6), 5)
                pygame.draw.circle(img, (96, 150, 84), (cx2 - 1, y + 5), 2)
        elif kind == "sign_frame":                                # крышный щит-вывеска: рама на опорах, цветные «неоновые» полосы
            c = rnd.choice(((255, 90, 170), (90, 220, 255), (255, 190, 80), (120, 255, 150)))
            shadow(x, y, bw, bh)
            pygame.draw.rect(img, (44, 40, 40), (x, y, bw, bh))
            pygame.draw.rect(img, (74, 70, 70), (x + 2, y + 2, bw - 4, bh - 4))
            pygame.draw.line(img, c, (x + 6, y + 8), (x + bw - 6, y + 8), 2)
            pygame.draw.line(img, tuple(int(v * 0.7) for v in c), (x + 6, y + 14), (x + bw - 14, y + 14), 2)
            for lx in range(x + 8, x + bw - 6, 14):
                pygame.draw.circle(img, (240, 236, 200), (lx, y + 3), 2)
        elif kind == "mast":                                      # мачта с растяжками
            shadow(x, y, 10, 10)
            pygame.draw.rect(img, (70, 70, 74), (x + 4, y + 4, 8, 8))
            pygame.draw.line(img, (200, 202, 206), (x + 8, y + 8), (x + 8, y - 8), 2)
            for ex, ey in ((x - 8, y + 18), (x + 24, y + 18), (x + 8, y + 26), (x + 8, y - 12)):
                pygame.draw.line(img, (110, 112, 116), (x + 8, y + 8), (ex, ey))
        elif kind == "sandbags":                                  # мешки с песком — позиция на крыше
            for k2 in range(5):
                pygame.draw.ellipse(img, (126, 108, 74), (x + k2 * 6, y + (k2 % 2) * 4, 12, 8))
                pygame.draw.ellipse(img, (160, 142, 98), (x + k2 * 6 + 1, y + (k2 % 2) * 4, 10, 5))
        else:                                                     # хлам: доска, бочка
            pygame.draw.rect(img, (120, 90, 60), (x, y, 28, 6))
            pygame.draw.circle(img, (80, 90, 70), (x + 36, y + 6), 6)
    layer = img
    w, h, img = real_w, real_h, real_img
    img.blit(pygame.transform.scale(layer, (w, h)), (0, 0))
    # надписи на крышах выключены: где что — подсказывают жители в диалогах
    # (поле sign в картах оставлено, вернуть — SHOW_ROOF_SIGNS = True)
    if SHOW_ROOF_SIGNS and r.get("sign"):
        text = r["sign"]
        mark = text[0] if text[0] in "+★" else None
        text = text[1:] if mark else text
        font = pygame.font.Font(None, max(22, min(56, int(w / max(4, len(text)) * 1.5))))
        paint = (228, 222, 204) if style != "concrete" else (190, 40, 36)
        t = font.render(text, False, paint)
        t.set_alpha(170)
        tx, ty = (w - t.get_width()) // 2, (h - t.get_height()) // 2 + (10 if mark else 0)
        img.blit(t, (tx, ty))
        if mark == "+":
            cx, cy = w // 2, ty - 18
            img.fill((200, 36, 36), (cx - 4, cy - 12, 8, 24))
            img.fill((200, 36, 36), (cx - 12, cy - 4, 24, 8))
        elif mark == "★":
            import math
            cx, cy, R = w // 2, ty - 16, 13
            pts = [(cx + (R if k % 2 == 0 else R * 0.45) * math.sin(k * math.pi / 5),
                    cy - (R if k % 2 == 0 else R * 0.45) * math.cos(k * math.pi / 5)) for k in range(10)]
            pygame.draw.polygon(img, (226, 190, 70), pts)
    # парапет: тёмная кайма, светлый край сверху и слева, тень снизу
    edge = tuple(max(0, v - 28) for v in pal[0])
    pygame.draw.rect(img, edge, (0, 0, w, h), 8)
    img.fill(tuple(min(255, v + 34) for v in pal[3]), (0, 0, w, 2))
    img.fill(tuple(min(255, v + 20) for v in pal[3]), (0, 0, 2, h))
    img.fill((30, 24, 20), (0, h - 3, w, 3))
    img.fill((40, 32, 26), (w - 3, 0, 3, h))
    return img


_DOOR_FRAMES = {}
_DOOR_SPILL = {}


def door_frame(k):
    """Дверь здания, открытая на долю k (0..1): за створкой — глубина с тёплым полом у порога, створка поворачивается
    наружу и сужается к петлям, на косяке — тень от неё; верхняя часть проёма темнее (потолок), к низу — свет внутри."""
    q = round(k * 8)
    if q not in _DOOR_FRAMES:
        base = P.image("x_door")
        out = base.copy()
        if q:
            f = q / 8
            inner = pygame.Rect(7, 7, base.get_width() - 14, base.get_height() - 12)
            leaf = base.subsurface(inner).copy()
            for i in range(inner.h):                                   # глубина: потолок тёмный, ближе к порогу — тёплый свет
                a = (i / inner.h) ** 1.6
                out.fill((int(22 + 70 * a * f), int(16 + 52 * a * f), int(12 + 26 * a * f), 255),
                         (inner.x, inner.y + i, inner.w, 1))
            for j in range(6):                                          # внутренняя тень у правого косяка и сверху
                sh = pygame.Surface((2, inner.h), pygame.SRCALPHA)
                sh.fill((0, 0, 0, 90 - j * 15))
                out.blit(sh, (inner.right - 2 - j * 2, inner.y))
                sh2 = pygame.Surface((inner.w, 2), pygame.SRCALPHA)
                sh2.fill((0, 0, 0, 80 - j * 12))
                out.blit(sh2, (inner.x, inner.y + j * 2))
            w = max(5, int(inner.w * (1 - 0.88 * f)))
            sq = pygame.Surface((w, inner.h), pygame.SRCALPHA)
            sq.blit(pygame.transform.scale(leaf, (w, inner.h)), (0, 0))
            for i in range(inner.h):                                    # перспектива: свободный край створки ниже и толще
                pass
            shade = pygame.Surface((w, inner.h), pygame.SRCALPHA)
            shade.fill((0, 0, 0, int(24 + 40 * f)))
            sq.blit(shade, (0, 0))
            edge = pygame.Surface((2, inner.h), pygame.SRCALPHA)
            edge.fill((255, 226, 170, 120))                              # блик на торце створки
            sq.blit(edge, (w - 2, 0))
            out.blit(sq, (inner.x, inner.y))
            cast = pygame.Surface((int(10 * f) + 2, inner.h), pygame.SRCALPHA)   # тень створки на проёме
            cast.fill((0, 0, 0, int(70 * f)))
            out.blit(cast, (inner.x + w, inner.y))
        _DOOR_FRAMES[q] = out
    return _DOOR_FRAMES[q]


def door_spill(k):
    """Тёплое пятно света на земле перед открытой дверью: трапеция, расширяющаяся от порога, и тень створки сбоку."""
    q = round(k * 8)
    if q not in _DOOR_SPILL:
        w, h = T, T + 12
        sp = pygame.Surface((w, h), pygame.SRCALPHA)
        f = q / 8
        for y in range(h):
            t = y / h
            half = int(w * (0.30 + 0.20 * t))
            a = int(90 * f * (1 - t) ** 1.5)
            if a > 0:
                sp.fill((255, 200, 120, a), (w // 2 - half, y, half * 2, 1))
        lean = pygame.Surface((10, 26), pygame.SRCALPHA)               # тень створки на земле у петель
        pygame.draw.polygon(lean, (0, 0, 0, int(80 * f)), [(0, 0), (4, 0), (9, 24), (3, 24)])
        sp.blit(lean, (2, 0))
        _DOOR_SPILL[q] = sp
    return _DOOR_SPILL[q]


_VOID = None   # пустота за стенами интерьера — чёрная клетка (создаётся в TownMap)


class TownMap(MapBase):
    parallax = False  # земля сплошная — фон под ней не нужен

    def __init__(self, path):
        if isinstance(path, dict):    # готовая карта (случайная встреча)
            d = path
        else:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            d = json.loads(raw)
        # отпечаток карты: сейв, сделанный до пересборки, не должен расставлять жителей по старым клеткам
        self.map_sig = None if isinstance(path, dict) else hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
        self.width, self.height = d["w"], d["h"]
        self.ground = d["ground"]
        self.floor_src = dict(d.get("floors") or {})   # код → картинки: по имени решается звук шага (src/stepsound.py)
        self.style = d.get("style", "town")
        self.dark = d.get("dark", False)          # под землёй: тьма по краям экрана
        self.night = d.get("night")               # ночь: цвет темноты, свет — src/lighting.py
        self.lights = d.get("lights", [])         # отдельные источники света [x, y, радиус, цвет, мерцание]
        self.blocked, self.sight = set(), set()
        # стены из наборов (автотайл A4, как в RPG Maker): {код: "pk:<набор>/<стена>"} — непроходимы
        self.wallsets = dict(d.get("walls", {}))
        solid = {"x", "_"} | set(self.wallsets)
        for y, row in enumerate(self.ground):
            for x, code in enumerate(row):
                if code in solid:
                    self.blocked.add((x, y))
                    self.sight.add((x, y))
        self.blocked.update(tuple(t) for t in d.get("blocked", []))   # вода в штампах наборов — не пройти
        self.portals = []
        for p in d.get("portals", []):
            self.portals.append({"tiles": {tuple(t) for t in p["tiles"]}, "to": p["to"],
                                 "at": tuple(p["at"]), "label": p.get("label", ""), "requires": p.get("requires")})
        self.exits = {tuple(t) for t in d.get("exits", [])}
        self.doors = []
        self.pickups = []
        self.player_spawn = (d["player"][0] * T, d["player"][1] * T)
        self.enemy_spawns = [((e[1] * T, e[2] * T), e[0], e[3] if len(e) > 3 else None) for e in d.get("enemies", [])]
        self.npc_spawns = [((x * T, y * T), nid) for nid, x, y in d.get("npcs", [])]
        # места жителей массовки по ролям (src/ambient.py): ключ анкеты -> [x, y], «critter:<вид>» -> [[x, y], …]
        self.folk_spots = d.get("folk_spots", {})
        # рабочие зоны: житель ходит только по своему месту (шериф — между столом и шкафами) — src/wander.py
        self.walk_zones = d.get("walk_zones", {})
        for item, count, x, y in d.get("pickups", []):
            self.add_pickup((x * T, y * T), item, count)

        self.decals = []  # (картинка, rect в мире)
        for name, px, py in d.get("decals", []):
            img = P.image(name)
            self.decals.append((name, img.get_rect(center=(px, py))))

        self.objects = []  # dict(name, rect картинки в мире, sort_y, container)
        for entry in d["props"]:
            name, x, y = entry[:3]
            ox, oy = entry[3:5] if len(entry) >= 5 else (0, 0)   # сдвиг картинки травы/кустов в пикселях
            inf = P.info(name)
            fw, fh = inf["foot"]
            foot = [(x + i, y + j) for i in range(fw) for j in range(fh)]
            if inf["block"]:
                self.blocked.update(foot)
            if inf["sight"]:
                self.sight.update(foot)
            bottom = (y + fh) * T
            rect = pygame.Rect(0, 0, *inf["size"])
            rect.midbottom = ((x + fw / 2) * T + ox, bottom + oy)
            # 6-й элемент — поправка порядка: вещь на столе поднята (oy < 0), но рисуется после стола
            z = entry[5] if len(entry) >= 6 else 0
            self.objects.append({"name": name, "rect": rect, "sort_y": bottom + oy + z, "foot": foot,
                                 "container": None, "floor": inf["layer"] == "floor"})

        self.containers = []
        for c in d.get("containers", []):
            obj = self.objects[c["prop"]]
            box = {"tile": obj["foot"][0], "tiles": obj["foot"], "name": c["name"], "loot": dict(c["loot"]),
                   "owner": c.get("owner"), "requires": c.get("requires"), "opened": False, "obj": obj,
                   "on_put": c.get("on_put")}
            obj["container"] = box
            self.containers.append(box)
        self.map_id = os.path.basename(path)[:-5] if isinstance(path, str) else None
        if self.map_id:                      # пустые ящики получают хлам (src/lootfill.py)
            lootfill.fill(self.map_id, self.containers, d.get("style"))

        self._dirt = _dirt_tiles()
        self._tiles = {"a": [], "g": []}
        for f in sorted(os.listdir(GROUND_DIR)):
            if f.startswith("asphalt_") and f[8:-4].isdigit():
                self._tiles["a"].append(pygame.image.load(os.path.join(GROUND_DIR, f)).convert())
            elif f.startswith("gravel_"):
                self._tiles["g"].append(pygame.image.load(os.path.join(GROUND_DIR, f)).convert())
        # бетонный пол в зданиях — асфальт, чуть светлее и теплее
        self._tiles["c"] = []
        for t in self._tiles["a"]:
            c = t.copy()
            c.fill((235, 222, 205), special_flags=pygame.BLEND_RGB_MULT)
            c.fill((18, 14, 8), special_flags=pygame.BLEND_RGB_ADD)
            self._tiles["c"].append(c)
        # земля пятнами: три оттенка, участки выбираются плавным шумом
        self._dirt_shades = []
        tint = d.get("tint")   # оттенок земли карты: Бейкер — песок пожелтее
        for mul in ((236, 232, 226), (245, 242, 237), (255, 255, 255), (255, 250, 243), (255, 245, 232)):
            shade = []
            for t in self._dirt:
                c = t.copy()
                c.fill(mul, special_flags=pygame.BLEND_RGB_MULT)
                if tint:
                    c.fill(tuple(tint), special_flags=pygame.BLEND_RGB_MULT)
                shade.append(c)
            self._dirt_shades.append(shade)
        self._tiles["m"] = _vault_floor()
        self._tiles["w"] = _drain_floor()
        self._rock = _rock_tiles()
        self._cave_rock = None
        if self.style == "cave":                  # скалы пещеры — фасады из набора gcave (верхняя и нижняя половины стены)
            try:
                # скальные фасады Goblin Cave, приглушённые под серо-бурую землю Dragon Cave: высокие валуны, а не тонкий карниз
                def _mute(i, row):
                    t = pygame.transform.scale(P.pack_image(f"pk:gcave/p1/{i},{row},1,1"), (T, T)).convert()
                    g = pygame.transform.grayscale(t)
                    out = pygame.Surface((T, T))
                    out.blit(t, (0, 0))
                    g.set_alpha(150)
                    out.blit(g, (0, 0))
                    out.fill((222, 206, 214), special_flags=pygame.BLEND_RGB_MULT)       # лёгкий сиреневый оттенок земли
                    return out
                top = [_mute(i, 0) for i in range(1, 8)]
                face = [_mute(i, 1) for i in range(1, 8)]
                self._cave_rock = {"top": top, "face": face}
            except Exception:
                self._cave_rock = None
        elif self.style == "cliff":               # каньон: валуны песчаника по кромке, внутри — песчаное плато (как верх обрыва в наборе)
            try:
                piece = P.pack_image("pk:desnat/p1/10,14,2,2")
                face_src = piece.subsurface((16, 56, 48, 34)).copy()
                face = []
                for k in range(4):
                    t = pygame.transform.scale(face_src, (T, T)).convert()
                    if k % 2:
                        t = pygame.transform.flip(t, True, False)
                    face.append(t)
                self._cave_rock = {"face": face, "top": face}
                sand = _noise_tiles(P.pack_image("pk:desnat/p1/0,0,1,1"))
                plateau = []
                for t in sand:
                    t = t.copy()
                    t.fill((255, 250, 238), special_flags=pygame.BLEND_RGB_MULT)       # плато — тот же песок, что и дно, чуть суше
                    plateau.append(t)
                self._rock = plateau
            except Exception:
                self._cave_rock = None
        self._edge_cache = {}
        self._face = _wall_faces(self.style)
        # полы из наборов: {код: ["pk:…", …]} — варианты клетки 48×48 (заливки A2, куски страниц)
        outdoor = not any("_" in row for row in d.get("ground", []))
        for code, imgs in d.get("floors", {}).items():
            if imgs and imgs[0].startswith("noise:"):   # бесшовный шум в цветах тайла набора (грунт без «кирпичиков»)
                self._tiles[code] = _noise_tiles(P.pack_image(imgs[0][6:]))
                continue
            raw = [P.pack_image(i) for i in imgs]
            if outdoor:                      # улица: тёмная рамка, нарисованная в тайле, даёт сетку — срезать
                raw = [_crop_frame(r) for r in raw]
            self._tiles[code] = _even_tone([pygame.transform.scale(r, (T, T)).convert() for r in raw])
        # улица (без пустоты «_», как у интерьеров): края участков земли размываются в соседнюю землю
        self._feather = {}
        self.ring_spot = tuple(d["ring_spot"]) if d.get("ring_spot") else None   # центр ринга (src/game/ring.py)
        self._piers = set(d.get("piers", []))      # доски причала: лежат поверх воды, берег у них не рисуется
        self._water = set()                       # коды воды на улице: берег рисуется слоями (мелководье, пена, мокрый песок)
        from collections import Counter
        counts = Counter(c for row in self.ground for c in row)
        outdoor = not any("_" in row for row in self.ground) and not d.get("crisp")   # crisp — мощёный город
        for code, n in counts.items():
            # 'd' — процедурная земля без своих тайлов (рисуется оттенками _dirt_shades): её кромки тоже размываем
            if code in self.wallsets or code in "x_" or not (self._tiles.get(code) or code == "d"):
                continue
            avg = pygame.transform.average_color((self._tiles.get(code) or self._dirt_shades[2])[0])
            if avg[2] > avg[0] + 25 and code not in d.get("not_water", ()):              # вода — свой берег (_shore), и в подземелье тоже (канал, сток)
                self._water.add(code)
                continue
            if code in self._piers:               # причал стоит над водой — без берега и размытия
                continue
            if outdoor:
                self._feather[code] = n
        self._indoor_water = not outdoor and any("_" in row for row in self.ground)   # канал в подземелье — ровная кладка
        self._water_land = {c for c in counts if c not in self._water and c not in self.wallsets
                            and c not in "x_" and self._tiles.get(c)}
        global _VOID
        if _VOID is None:
            _VOID = pygame.Surface((T, T))
            _VOID.fill((8, 6, 6))
        self._walls_img = {code: (P.pack_image(w + "_top"), P.pack_image(w + "_face"))
                           for code, w in self.wallsets.items()}
        self._wall_cache = {}
        line = pygame.image.load(os.path.join(GROUND_DIR, "asphalt_line.png")).convert()
        self._tiles["v"] = [line]
        self._tiles["h"] = [pygame.transform.rotate(line, 90)]

        # гермодвери: объект-дверь, закрытый, пока не поставлен флаг (ключ-карта или терминал)
        self.gates = []
        for g in d.get("gates", []):
            obj = self.objects[g["prop"]]
            gate = {"tiles": list(obj["foot"]), "flag": g["flag"], "key": g.get("key"), "msg": g.get("msg", ""),
                    "open_msg": g.get("open_msg"), "pry": g.get("pry", False),
                    "obj": obj, "open": False}
            obj["gate"] = gate
            self.gates.append(gate)
            self.doors += gate["tiles"]

        # крыши: рисуются между зданием и тем, что перед ним; когда герой внутри — тают
        self.roofs = []
        for r in d.get("roofs", []):
            # сверху из-под крыши виден верх северной стены (с проёмом двери, если он там),
            # снизу — фасад южной стены целиком
            rect = pygame.Rect(r["x0"] * T, r["y0"] * T, (r["x1"] - r["x0"] + 1) * T,
                               (r["y1"] - r["y0"]) * T - WALL_LIFT)
            self.roofs.append({**r, "rect": rect, "alpha": 255.0, "img": None,
                               "sort_y": (r["y1"] + 1) * T + 1})

        self.terminals = []
        for t in d.get("terminals", []):
            obj = self.objects[t["prop"]]
            term = {"id": t["id"], "tiles": obj["foot"], "obj": obj}
            obj["terminal"] = term
            self.terminals.append(term)

    # ------------------------------------------------------------ клетки
    def is_wall(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return (x, y) in self.blocked

    def blocks_sight(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or (x, y) in self.sight

    def is_exit(self, x, y):
        return (x, y) in self.exits

    def roof_over(self, tile):
        """Крыша, под которой клетка (внутри здания, включая стены и проёмы)."""
        x, y = tile
        return next((r for r in self.roofs if r["x0"] <= x <= r["x1"] and r["y0"] <= y <= r["y1"]), None)

    def update_roofs(self, player_tile, dt_ms):
        """Крыша здания, где стоит герой, плавно исчезает; остальные — на месте."""
        inside = self.roof_over(player_tile)
        px, py = player_tile
        for o in self.objects:             # двери зданий открываются перед героем и закрываются за ним
            if o["name"] == "x_door":
                tx, ty = o["foot"][0]
                near = abs(px - tx) <= 1 and abs(py - ty) <= 1
                k = o.get("open", 0.0)
                o["open"] = min(1.0, k + dt_ms / 180) if near else max(0.0, k - dt_ms / 260)
        for r in self.roofs:
            target = 0.0 if r is inside else 255.0
            step = dt_ms * 1.4
            r["alpha"] = min(target, r["alpha"] + step) if r["alpha"] < target else max(target, r["alpha"] - step)

    def gate_at(self, tile):
        return next((g for g in self.gates if tuple(tile) in g["tiles"]), None)

    def open_door(self, tile):
        gate = self.gate_at(tile)
        if gate:
            self.open_gate(gate)

    def remove_object(self, obj):
        """Объект исчез (взорвалась бочка): не рисуется и не мешает."""
        obj["hidden"] = True
        for t in obj["foot"]:
            self.blocked.discard(t)
            self.sight.discard(t)

    def open_gate(self, gate):
        gate["open"] = True
        gate["obj"]["hidden"] = True
        for t in gate["tiles"]:
            self.blocked.discard(t)
            self.sight.discard(t)
            if t in self.doors:
                self.doors.remove(t)

    def portal_at(self, x, y):
        return next((p for p in self.portals if (x, y) in p["tiles"]), None)

    def tile_at(self, x, y):
        return "#" if self.is_wall(x, y) else "."

    # ------------------------------------------------------------ контейнеры
    def terminal_sprite_at(self, world_pos):
        for o in sorted(self.objects, key=lambda o: -o["sort_y"]):
            if o.get("terminal") and o["rect"].collidepoint(world_pos):
                img = P.image(o["name"])
                if img.get_at((world_pos[0] - o["rect"].x, world_pos[1] - o["rect"].y)).a > 40:
                    return o["terminal"]
        return None

    def container_sprite_at(self, world_pos):
        """Закрытый контейнер, по картинке которого пришёлся клик (передний первым)."""
        hits = [o for o in self.objects if o["container"]
                and o["rect"].collidepoint(world_pos)]
        for o in sorted(hits, key=lambda o: -o["sort_y"]):
            img = P.image(o["name"])
            if img.get_at((world_pos[0] - o["rect"].x, world_pos[1] - o["rect"].y)).a > 40:
                return o["container"]
        return None

    # ------------------------------------------------------------ отрисовка
    def _ground_tile(self, x, y):
        if self.style in ("cave", "cliff") and self._cave_rock:
            tile = self._cave_edge(x, y)
            if tile is not None:
                return tile
        return self._ground_tile_base(x, y)

    # ------------------------------------------------------------ округлые края пещер
    def _cave_class(self, x, y, walls_as_floor):
        """1 — пол (и фасады стен, когда walls_as_floor), 0 — тёмная скала."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        c = self.ground[y][x]
        if c not in "x_" and c not in self.wallsets:
            return 1
        if c == "x" and walls_as_floor:
            below = self.ground[y + 1][x] if y + 1 < self.height else "x"
            below2 = self.ground[y + 2][x] if y + 2 < self.height else "x"
            if below != "x" or below2 != "x":
                return 1
        return 0

    def _cave_is_dark(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.ground[y][x] == "x"            # вся скала (и южные фасады) идёт через общий сглаженный контур

    def _cave_edge(self, x, y):
        """Граница «пол — тёмная скала» рисуется по сглаженному полю (как берег): контур гротов — плавные дуги, а не клетки."""
        c = self.ground[y][x]
        dark = self._cave_is_dark(x, y)
        floor = c not in "x_" and c not in self.wallsets            # вода у скалы тоже получает контур
        if not (dark or floor):
            return None
        near = False
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-2, -1, 0, 1, 2):
                nx, ny = x + dx, y + dy
                if dark and self._cave_class(nx, ny, False):
                    near = True
                if floor and abs(dx) <= 1 and abs(dy) <= 1 and self._cave_is_dark(nx, ny):
                    near = True
        if not near:
            return None
        key = ("ce", x, y)
        if key in self._edge_cache:
            return self._edge_cache[key]
        wf = False                                        # стены — скала для всех: фасады и боковые края сходятся одной дугой
        f = {(i, j): self._cave_class(x + i, y + j, wf) for i in (-1, 0, 1) for j in (-1, 0, 1)}
        N = 24
        mask = pygame.Surface((N, N))
        G = {}
        for j in (-1, 0, 1, 2):                         # поле «доля пола» в узлах: считаем один раз, не на каждый пиксель
            for i in (-1, 0, 1, 2):
                tot = n = 0
                for ddy in (-1, 0, 1):
                    for ddx in (-1, 0, 1):
                        w = 2 if ddx == 0 and ddy == 0 else 1
                        tot += w
                        n += w * self._cave_class(x + i + ddx, y + j + ddy, wf)
                G[(i, j)] = n / tot
        for py in range(N):
            for px in range(N):
                u, v = (px + 0.5) / N - 0.5, (py + 0.5) / N - 0.5
                i0, j0 = (-1 if u < 0 else 0), (-1 if v < 0 else 0)
                fu, fv = u - i0, v - j0
                val = (G[(i0, j0)] * (1 - fu) * (1 - fv) + G[(i0 + 1, j0)] * fu * (1 - fv)
                       + G[(i0, j0 + 1)] * (1 - fu) * fv + G[(i0 + 1, j0 + 1)] * fu * fv)
                m = max(0, min(255, int(255 * val)))
                mask.set_at((px, py), (m, m, m))
        mask = pygame.transform.smoothscale(mask, (T, T))
        h = (x * 73856093) ^ (y * 19349663)
        if not hasattr(self, "_cave_floor_code"):
            from collections import Counter
            cnt = Counter(c for row in self.ground for c in row if c not in "x_" and c not in self.wallsets
                          and c not in self._water and self._tiles.get(c))
            self._cave_floor_code = [cnt.most_common(1)[0][0]] if cnt else []
        fl_codes = self._cave_floor_code
        if floor:
            fl_tile = self._ground_tile_base(x, y)
        else:                                       # у скалы пол «просачивается» из соседней клетки пола — его земля, а не любая
            fl_tile = None
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self._cave_class(nx, ny, False):
                    fl_tile = self._ground_tile_base(nx, ny)
                    break
            if fl_tile is None and fl_codes:
                fl_tile = self._tiles[fl_codes[0]][h % len(self._tiles[fl_codes[0]])]
        rock_tile = self._rock[h % len(self._rock)]
        if fl_tile is None:
            return None
        out = pygame.Surface((T, T))
        lip, hi = ((36, 28, 24), (118, 98, 80)) if self.style == "cave" else ((92, 64, 42), (244, 226, 176))
        # толщина скалы у края — валуны той же фактуры, что и южные фасады, а не тонкая линия: стена читается по всему контуру
        boul = self._cave_rock["face"][(h // 7) % len(self._cave_rock["face"])]
        for py in range(T):
            for px in range(T):
                m = mask.get_at((px, py))[0]
                if m >= 136:                                   # пол; у кромки — тень
                    c = fl_tile.get_at((px, py))[:3]
                    if m < 176:
                        k = 0.55 + 0.45 * (m - 136) / 40
                        c = (int(c[0] * k), int(c[1] * k), int(c[2] * k))
                    elif m < 214:
                        k = 0.82 + 0.18 * (m - 176) / 38
                        c = (int(c[0] * k), int(c[1] * k), int(c[2] * k))
                elif m >= 124:                                 # светлая верхняя грань скола
                    c = hi
                elif m >= 112:                                 # тёмный контур
                    c = lip
                elif m >= 14:                                  # тело стены: валуны, к глубине темнее
                    c = boul.get_at((px, py))[:3]
                    k = (0.62 + 0.38 * min(1.0, (m - 14) / 70)) if self.style == "cave" else (0.82 + 0.18 * min(1.0, (m - 14) / 70))
                    c = (int(c[0] * k), int(c[1] * k), int(c[2] * k))
                else:
                    c = rock_tile.get_at((px, py))[:3]
                out.set_at((px, py), c)
        self._edge_cache[key] = out
        return out

    def _ground_tile_base(self, x, y):
        """Клетка земли; у асфальта и гравия, граничащих с землёй, край размыт рваной кромкой."""
        code = self.ground[y][x]
        if code in "aghv":
            mask = 0
            for bit, (dx, dy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.ground[ny][nx] == "d":
                    mask |= 1 << bit
            if mask:
                key = (x, y)
                tile = self._edge_cache.get(key)
                if tile is None:
                    tile = self._edge_cache[key] = self._blend_edge(x, y, self._raw_tile(x, y), mask)
                return tile
        if self._water and self._near_shore(x, y, code):
            return self._shore(x, y, code)
        if code in self._water:                    # мелководье и глубина сходятся плавно
            near = {self.ground[ny][nx] for ny in range(max(0, y - 2), min(self.height, y + 3))
                    for nx in range(max(0, x - 2), min(self.width, x + 3))} & self._water
            if len(near) > 1:
                key = ("ww", x, y)
                if key not in self._edge_cache:
                    self._edge_cache[key] = self._blend_codes(x, y, sorted(near), (x * 73856093) ^ (y * 19349663), soft=True)
                return self._edge_cache[key]
        if code in self._feather:
            return self._feathered(x, y, code)
        return self._raw_tile(x, y)

    # ------------------------------------------------------------ берег
    def _near_shore(self, x, y, code):
        """Клетка у кромки воды: вода рядом с сушей или суша рядом с водой (окно 3×3)."""
        wet = code in self._water
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    c = self.ground[ny][nx]
                    if (c in self._water) != wet and (c in self._water_land or c in self._water) \
                            and c not in self._piers and code not in self._piers:
                        return True
        return False

    def _water_field(self, x, y):
        """Доля воды вокруг (окно 5×5 с весами) — шире окно, плавнее и круглее берег. Причал считается водой."""
        n = tot = 0
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = min(self.width - 1, max(0, x + dx)), min(self.height - 1, max(0, y + dy))
                w = (3 - abs(dx)) * (3 - abs(dy))
                tot += w
                c = self.ground[ny][nx]
                n += w * (c in self._water or c in self._piers)
        return n / tot

    def _shore(self, x, y, code):
        """Берег как в наборе seaside: кромка идёт по сглаженному полю воды с волной вдоль берега
        (непрерывной через клетки), у кромки — светлое мелководье, линия пены и полоса мокрого песка."""
        import math
        key = ("w", x, y)
        tile = self._edge_cache.get(key)
        if tile is not None:
            return tile
        h = (x * 73856093) ^ (y * 19349663)
        # вода и суша этой клетки: ближайшие коды в окне 3×3
        wc = code if code in self._water else next(
            (self.ground[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
             if 0 <= x + dx < self.width and 0 <= y + dy < self.height and self.ground[y + dy][x + dx] in self._water), code)
        lc = code if code not in self._water else next(
            (self.ground[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
             if 0 <= x + dx < self.width and 0 <= y + dy < self.height and self.ground[y + dy][x + dx] in self._water_land), code)
        water = self._tiles[wc][h % len(self._tiles[wc])]
        land = self._feathered(x, y, lc) if code not in self._water and lc in self._feather else \
            self._tiles[lc][h % len(self._tiles[lc])] if self._tiles.get(lc) else self._raw_tile(x, y)
        f = {(i, j): self._water_field(x + i, y + j) for i in (-1, 0, 1) for j in (-1, 0, 1)}
        out = land.copy()
        B = 2
        for py in range(0, T, B):
            for px in range(0, T, B):
                u, v = (px + 1) / T - 0.5, (py + 1) / T - 0.5
                i0, j0 = (-1 if u < 0 else 0), (-1 if v < 0 else 0)
                fu, fv = u - i0, v - j0
                val = (f[(i0, j0)] * (1 - fu) * (1 - fv) + f[(i0 + 1, j0)] * fu * (1 - fv)
                       + f[(i0, j0 + 1)] * (1 - fu) * fv + f[(i0 + 1, j0 + 1)] * fu * fv)
                wx, wy = x * T + px, y * T + py
                if self._indoor_water:                          # канал: прямая каменная кромка, без пены и песка
                    cell = self.ground[min(self.height - 1, max(0, (wy) // T))][min(self.width - 1, max(0, wx // T))]
                    if cell in self._water:
                        edge = min(abs(((wx // T) - x) * T + px - (0 if (x - 1, y) else 0)), 99)
                        c = water.get_at((px, py))
                        near_land = any(self.ground[ny][nx] not in self._water
                                        for nx, ny in ((wx // T + dx, wy // T + dy) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
                                        if 0 <= nx < self.width and 0 <= ny < self.height)
                        out.fill(c, (px, py, B, B))
                        lx, ly = px, py
                        dl = min([lx if (x - 1 >= 0 and self.ground[y][x - 1] not in self._water) else 99,
                                  T - 1 - lx if (x + 1 < self.width and self.ground[y][x + 1] not in self._water) else 99,
                                  ly if (y - 1 >= 0 and self.ground[y - 1][x] not in self._water) else 99,
                                  T - 1 - ly if (y + 1 < self.height and self.ground[y + 1][x] not in self._water) else 99])
                        if dl < 4:
                            out.fill((52, 50, 48), (px, py, B, B))           # кромка кладки
                        elif dl < 10:
                            out.fill((int(c[0] * 0.7), int(c[1] * 0.75), int(c[2] * 0.85)), (px, py, B, B))   # тень у стенки
                    continue
                val += 0.05 * math.sin(wx * 0.11 + wy * 0.05) + 0.035 * math.sin(wx * 0.043 - wy * 0.13) \
                    + 0.02 * math.sin((wx + 2 * wy) * 0.29)
                if val >= 0.5:                                  # вода
                    c = water.get_at((px, py))
                    if val < 0.58:                              # мелководье — светлее, бирюзовее
                        k = (0.58 - val) / 0.08
                        c = (min(255, int(c[0] + 50 * k)), min(255, int(c[1] + 60 * k)), min(255, int(c[2] + 40 * k)))
                    out.fill(c, (px, py, B, B))
                    if val < 0.525:                             # пена у кромки
                        out.fill((232, 240, 236), (px, py, B, B))
                elif val > 0.42:                                # мокрый песок
                    c = land.get_at((px, py))
                    k = 0.78 + 0.22 * (0.5 - val) / 0.08
                    out.fill((min(255, int(c[0] * k)), min(255, int(c[1] * k)), min(255, int(c[2] * k * 1.03))), (px, py, B, B))
        self._edge_cache[key] = out
        return out

    def _patch_field(self, x, y, p):
        """Доля клеток «пятна» p в окрестности 3×3 клетки (x, y): 1 — глубоко внутри, 0 — снаружи."""
        n = tot = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = min(self.width - 1, max(0, x + dx)), min(self.height - 1, max(0, y + dy))
                w = 2 if dx == 0 and dy == 0 else 1
                tot += w
                n += w * (self.ground[ny][nx] == p)
        return n / tot

    def _blend_codes(self, x, y, codes, h, soft=False):
        """Смесь земель: вес каждой — по сглаженному полю (непрерывно через границы клеток), веса нормируются,
        текстуры складываются. Соседние клетки сходятся без шва, сколько бы земель ни встречалось."""
        N = 12
        fields = {c: {(i, j): self._patch_field(x + i, y + j, c) for i in (-1, 0, 1) for j in (-1, 0, 1)} for c in codes}
        rnd = random.Random(h)
        grid = {c: [[0.0] * N for _ in range(N)] for c in codes}
        for py in range(N):
            for px in range(N):
                u, v = (px + 0.5) / N - 0.5, (py + 0.5) / N - 0.5
                i0, j0 = (-1 if u < 0 else 0), (-1 if v < 0 else 0)
                fu, fv = u - i0, v - j0
                jit = rnd.uniform(-0.05, 0.05)
                ws, raw = {}, {}
                for c in codes:
                    f = fields[c]
                    val = (f[(i0, j0)] * (1 - fu) * (1 - fv) + f[(i0 + 1, j0)] * fu * (1 - fv)
                           + f[(i0, j0 + 1)] * (1 - fu) * fv + f[(i0 + 1, j0 + 1)] * fu * fv)
                    ws[c] = (max(0.0, min(1.0, (val + jit - 0.3) / 0.4)) ** 2 if not soft
                             else max(0.0, min(1.0, val)) ** 1.5)                # вода — широкий мягкий переход
                    raw[c] = val
                if sum(ws.values()) < 1e-6:                  # ни одна земля не набрала веса (стык трёх) — берём сильнейшую, не чёрный пиксель
                    ws[max(raw, key=raw.get)] = 1.0
                tot = sum(ws.values()) or 1.0
                for c in codes:
                    grid[c][py][px] = ws[c] / tot
        out = pygame.Surface((T, T))
        out.fill((0, 0, 0))
        for c in codes:
            small = pygame.Surface((N, N))
            for py in range(N):
                for px in range(N):
                    g = int(255 * grid[c][py][px] + 0.5)
                    small.set_at((px, py), (g, g, g))
            if not any(grid[c][py][px] for py in range(N) for px in range(N)):
                continue
            variants = self._tiles.get(c) or self._dirt_shades[self._shade(x, y)]
            tex = variants[h % len(variants)].copy()
            tex.blit(pygame.transform.smoothscale(small, (T, T)), (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            out.blit(tex, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return out

    def _patch_overlay(self, x, y, patch, h):
        """Картинка земли patch, прозрачная там, где по сглаженному полю её нет (мягкая неровная кромка)."""
        over = self._tiles[patch][h % len(self._tiles[patch])].convert_alpha()
        f = {(i, j): self._patch_field(x + i, y + j, patch) for i in (-1, 0, 1) for j in (-1, 0, 1)}
        rnd = random.Random(h ^ (ord(patch[0]) * 7919))
        N = 12                                         # маска считается на сетке 12×12 и плавно растягивается
        small = pygame.Surface((N, N), pygame.SRCALPHA)
        for py in range(N):
            for px in range(N):
                u, v = (px + 0.5) / N - 0.5, (py + 0.5) / N - 0.5
                i0, j0 = (-1 if u < 0 else 0), (-1 if v < 0 else 0)
                fu, fv = u - i0, v - j0
                val = (f[(i0, j0)] * (1 - fu) * (1 - fv) + f[(i0 + 1, j0)] * fu * (1 - fv)
                       + f[(i0, j0 + 1)] * (1 - fu) * fv + f[(i0 + 1, j0 + 1)] * fu * fv)
                val += rnd.uniform(-0.05, 0.05)
                a = max(0.0, min(1.0, (val - 0.3) / 0.4))
                small.set_at((px, py), (255, 255, 255, int(255 * a)))
        over.blit(pygame.transform.smoothscale(small, (T, T)), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return over

    def _feathered(self, x, y, code):
        """Граница двух земель (город и песок, дорога и пустырь): рисуется по сглаженному полю, а не по сетке —
        край идёт плавной неровной линией, углы скруглены, ступенек нет."""
        key = ("f", x, y)
        tile = self._edge_cache.get(key)
        if tile is not None:
            return tile
        near = {}
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    nc = self.ground[ny][nx]
                    if nc != code and nc in self._feather:
                        near[nc] = near.get(nc, 0) + 1
        if not near:
            tile = self._edge_cache[key] = self._raw_tile(x, y)
            return tile
        codes = {code}                               # все земли, чьё поле дотягивается до клетки (окно 5×5)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = min(self.width - 1, max(0, x + dx)), min(self.height - 1, max(0, y + dy))
                if self.ground[ny][nx] in self._feather:
                    codes.add(self.ground[ny][nx])
        h = (x * 73856093) ^ (y * 19349663)
        tile = self._blend_codes(x, y, sorted(codes), h)
        self._edge_cache[key] = tile
        return tile

    def _blend_edge(self, x, y, base, mask):
        """Поверх клетки — земля, прозрачность которой плавно спадает от граничащих сторон
        (маска с неровной кромкой, как стёртая обочина)."""
        dirt = self._dirt_shades[self._shade(x, y)][((x * 131) ^ (y * 71)) % len(self._dirt)]
        over = dirt.convert_alpha()
        over.blit(_edge_mask(mask, (x * 7 + y * 13) % 4), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        out = base.copy()
        out.blit(over, (0, 0))
        return out

    def _raw_tile(self, x, y):
        code = self.ground[y][x]
        h = (x * 73856093) ^ (y * 19349663)  # один и тот же вариант клетки при каждом кадре
        if code in self.wallsets:
            return self._wall_tile(x, y, code)
        if code == "_":
            return _VOID
        if code == "x":
            below = self.ground[y + 1][x] if y + 1 < self.height else "x"
            if self.style in ("cave", "cliff") and self._cave_rock:
                return self._rock[h % len(self._rock)]          # у пещер вся скала рисуется общим контуром (_cave_edge)
                if below != "x":
                    return self._cave_rock["face"][h % len(self._cave_rock["face"])]   # скальный фасад над полом
                below2 = self.ground[y + 2][x] if y + 2 < self.height else "x"
                if below2 != "x":
                    return self._cave_rock["top"][h % len(self._cave_rock["top"])]     # верхняя половина двухклеточной стены
                return self._rock_rim(x, y, h)
            if below != "x":
                return self._face[h % len(self._face)]   # стена, обращённая к нам
            if self.style in SLAB_RIM:
                return self._slab_rim(x, y, h)
            return self._rock[h % len(self._rock)]
        if code in self._tiles and self._tiles[code]:
            variants = self._tiles[code]
        else:
            variants = self._dirt_shades[self._shade(x, y)]
        return variants[h % len(variants)]

    def _rock_rim(self, x, y, h):
        """Толща скалы пещеры с кромкой там, где рядом пол: тёмный уступ и светлый скол — край читается, а не обрывается в чёрное."""
        sides = []
        for name, dx, dy in (("n", 0, -1), ("w", -1, 0), ("e", 1, 0)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and self.ground[ny][nx] not in "x_" \
                    and self.ground[ny][nx] not in self.wallsets:
                sides.append(name)
        base = self._rock[h % len(self._rock)]
        if not sides:
            return base
        key = ("rim", h % len(self._rock), tuple(sides))
        if key in self._edge_cache:
            return self._edge_cache[key]
        t = base.copy()
        lip, hi = (58, 44, 34), (104, 82, 60)
        for name in sides:
            if name == "n":
                t.fill(lip, (0, 0, T, 10)); t.fill(hi, (0, 0, T, 3))
            elif name == "w":
                t.fill(lip, (0, 0, 10, T)); t.fill(hi, (0, 0, 3, T))
            else:
                t.fill(lip, (T - 10, 0, 10, T)); t.fill(hi, (T - 3, 0, 3, T))
        self._edge_cache[key] = t
        return t

    def _slab_rim(self, x, y, h, depth=3):
        """Толща стены (бетон коллектора, сталь убежища): у прохода — бордюр-кромка, дальше вглубь плавно
        темнеет до черноты, чтобы массив между коридорами читался как стена, а не как дыра в карте."""
        def gap(dx, dy):           # через сколько клеток в эту сторону пол (0 — дальше depth)
            for k in range(1, depth + 1):
                nx, ny = x + dx * k, y + dy * k
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    return 0
                if self.ground[ny][nx] not in "x_" and self.ground[ny][nx] not in self.wallsets:
                    return k
            return 0
        sides = (gap(0, -1), gap(-1, 0), gap(1, 0))
        base = self._rock[h % len(self._rock)]
        if not any(sides):
            return base
        key = ("slab", h % len(self._rock), sides)
        if key in self._edge_cache:
            return self._edge_cache[key]
        t = base.copy()
        fade, lip, hi, gap_c = SLAB_RIM[self.style]
        reach = depth * T * 0.8
        shade = pygame.Surface((T, T), pygame.SRCALPHA)
        for py in range(T):
            for px in range(T):
                d = min([(k - 1) * T + off for k, off in zip(sides, (py, px, T - 1 - px)) if k] or [reach])
                a = max(0.0, 1 - d / reach) ** 1.6
                if a > 0:
                    shade.set_at((px, py), (*fade, int(250 * a)))
        t.blit(shade, (0, 0))
        kn, kw, ke = sides
        if kn == 1:
            t.fill(lip, (0, 0, T, 10)); t.fill(hi, (0, 0, T, 3)); t.fill(gap_c, (0, 10, T, 2))
        if kw == 1:
            t.fill(lip, (0, 0, 7, T)); t.fill(hi, (0, 0, 2, T))
        if ke == 1:
            t.fill(lip, (T - 7, 0, 7, T)); t.fill(hi, (T - 2, 0, 2, T))
        self._edge_cache[key] = t
        return t

    # ------------------------------------------------------------ стены A4 (как в RPG Maker)
    def _is_wall(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height) or self.ground[y][x] in self.wallsets \
            or self.ground[y][x] in "x_"

    def _face_row(self, x, y):
        """Фасад стены — две нижние клетки вертикального ряда стены: 2 — нижняя, 1 — верхняя, 0 — не фасад."""
        if not self._is_wall(x, y + 1):
            return 2
        if not self._is_wall(x, y + 2) and y + 1 < self.height and self.ground[y + 1][x] in self.wallsets:
            return 1
        return 0

    def _wall_tile(self, x, y, code):
        key = (x, y)
        t = self._wall_cache.get(key)
        if t is not None:
            return t
        top, face = self._walls_img[code]
        t = pygame.Surface((T, T))
        fr = self._face_row(x, y)
        if fr:   # фасад 96×96 = 2×2 клетки: половина по чётности столбца, верх/низ — по ряду
            t.blit(face, (0, 0), ((x % 2) * T, (fr - 1) * T, T, T))
        else:    # верх стены — автотайл из четвертинок 24×24 (как у RPG Maker)
            def ceil(cx, cy):
                return self._is_wall(cx, cy) and not self._face_row(cx, cy)
            q = T // 2
            for qx in (0, 1):
                for qy in (0, 1):
                    sx, sy = (1 if qx else -1), (1 if qy else -1)
                    hside, vside = ceil(x + sx, y), ceil(x, y + sy)
                    diag = ceil(x + sx, y + sy)
                    if hside and vside and not diag:          # внутренний угол — из верхнего правого блока
                        src = (T + qx * q, qy * q)
                    else:
                        col = (1 if qx == 0 else 2) if hside else (0 if qx == 0 else 3)
                        row = (1 if qy == 0 else 2) if vside else (0 if qy == 0 else 3)
                        src = (col * q, T + row * q)
                    t.blit(top, (qx * q, qy * q), (*src, q, q))
        self._wall_cache[key] = t
        return t

    @staticmethod
    def _noise(x, y):
        h = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
        h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
        return (h & 0xFFFF) / 0xFFFF

    def _shade(self, x, y):
        """Плавный шум по крупной сетке 6×6 клеток: участки земли чуть светлее/темнее (5 ступеней)."""
        gx, gy = x / 6, y / 6
        ix, iy = int(gx), int(gy)
        fx, fy = gx - ix, gy - iy
        n = (self._noise(ix, iy) * (1 - fx) * (1 - fy) + self._noise(ix + 1, iy) * fx * (1 - fy)
             + self._noise(ix, iy + 1) * (1 - fx) * fy + self._noise(ix + 1, iy + 1) * fx * fy)
        return min(4, int(n * 5))

    def draw(self, surf, cam):
        cam_x, cam_y = int(cam.x), int(cam.y)
        sw, sh = surf.get_size()
        view = pygame.Rect(cam_x, cam_y, sw, sh)
        x0, y0 = max(0, cam_x // T), max(0, cam_y // T)
        x1 = min(self.width, (cam_x + sw) // T + 1)
        y1 = min(self.height, (cam_y + sh) // T + 1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                surf.blit(self._ground_tile(x, y), (x * T - cam_x, y * T - cam_y))
        for name, rect in self.decals:
            if rect.colliderect(view):
                surf.blit(P.image(name), (rect.x - cam_x, rect.y - cam_y))
        for o in self.objects:
            if o["floor"] and o["rect"].colliderect(view) and not o.get("hidden"):
                if o["name"] == "x_door":
                    kk = o.get("open", 0.0)
                    img = door_frame(kk)
                    if kk > 0.04:
                        surf.blit(door_spill(kk), (o["rect"].x - cam_x, o["rect"].bottom - cam_y))
                else:
                    img = P.image(o["name"])
                surf.blit(img, (o["rect"].x - cam_x, o["rect"].y - cam_y))
        if not self.night:   # ночью стрелки рисуются поверх темноты (draw_arrows из render)
            self.draw_arrows(surf, cam)
        self.draw_pickups(surf, cam)

    _GREEN = None

    def draw_arrows(self, surf, cam):
        """Стрелки на краях карты: жёлтые — выход на карту мира, зелёные — в соседний район."""
        cam_x, cam_y = int(cam.x), int(cam.y)
        sw, sh = surf.get_size()
        x0, y0 = max(0, cam_x // T), max(0, cam_y // T)
        x1, y1 = min(self.width, (cam_x + sw) // T + 1), min(self.height, (cam_y + sh) // T + 1)
        for (x, y) in self.exits:
            if x0 <= x < x1 and y0 <= y < y1:
                surf.blit(self._exit_arrow(x, y), (x * T - cam_x, y * T - cam_y))
        for p in self.portals:
            for (x, y) in p["tiles"]:
                if (x in (0, self.width - 1) or y in (0, self.height - 1)) and x0 <= x < x1 and y0 <= y < y1:
                    surf.blit(self._exit_arrow(x, y, green=True), (x * T - cam_x, y * T - cam_y))
        # вход посреди карты (убежище, шахта, двор здания) — те же зелёные стрелки, что у переходов на краю:
        # по одной на каждую клетку прохода, на клетке перед ним, смотрят внутрь. Люки и лестницы — без стрелок.
        for p in self.portals:
            if p.get("_door") is None:
                p["_door"] = self._door_arrow_spots(p)
            for (ax, ay), key in p["_door"]:
                if x0 <= ax < x1 and y0 <= ay < y1:
                    surf.blit(self._door_arrow(key), (ax * T - cam_x, ay * T - cam_y))

    def _door_arrow_spots(self, p):
        """[(клетка перед входом, направление внутрь)]; пусто — люк, лестница или край карты."""
        tiles = {tuple(t) for t in p["tiles"]}
        if any(x in (0, self.width - 1) or y in (0, self.height - 1) for x, y in tiles):
            return []
        hatch = {tuple(t) for o in self.objects if o["name"] in ("x_manhole", "x_ladder") for t in o["foot"]}
        if tiles & hatch:
            return []
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):        # сторона, откуда подходят
            spots = [((x + dx, y + dy), (-dx, -dy)) for x, y in sorted(tiles)
                     if (x + dx, y + dy) not in tiles and not self.is_wall(x + dx, y + dy)]
            if len(spots) == len(tiles):
                return spots
        return []

    def _door_arrow(self, key):
        """Зелёная стрелка перехода (как на краю карты), повёрнутая внутрь входа."""
        if TownMap._GREEN is None:
            self._exit_arrow(0, 1, green=True)
        angle = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): -90}[key]
        return pygame.transform.rotate(TownMap._GREEN, angle)

    def _exit_arrow(self, x, y, green=False):
        """Стрелки выхода смотрят наружу, к краю карты. Жёлтые — на карту мира,
        зелёные — в соседний район той же локации."""
        arrow = loader.special_tile(">")
        if green:
            if TownMap._GREEN is None:
                g = arrow.copy()
                g.fill((90, 255, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
                TownMap._GREEN = g
            arrow = TownMap._GREEN
        if x == 0:
            return pygame.transform.flip(arrow, True, False)
        if y == self.height - 1:
            return pygame.transform.rotate(arrow, -90)
        if y == 0:
            return pygame.transform.rotate(arrow, 90)
        return arrow

    def drawables(self, cam, size=(S.SCREEN_W, S.SCREEN_H)):
        cam_x, cam_y = int(cam.x), int(cam.y)
        view = pygame.Rect(cam_x, cam_y, *size)
        out = []
        for o in self.objects:
            if o["floor"] or o.get("hidden") or not o["rect"].colliderect(view):
                continue
            c = o["container"]
            opened = c is not None and c["opened"] and not c["loot"]  # пустой — темнее
            if c is not None and lootfill.looks_empty(c):            # пустой — вскрытый проп
                v = lootfill.open_variant(o["name"])
                if v:
                    img = P.image(v)
                    out.append((o["sort_y"], img, (o["rect"].centerx - img.get_width() // 2 - cam_x,
                                                   o["rect"].bottom - img.get_height() - cam_y)))
                    continue
            out.append((o["sort_y"], P.image(o["name"], darken=opened), (o["rect"].x - cam_x, o["rect"].y - cam_y)))
        for r in self.roofs:
            if r["alpha"] <= 1 or not r["rect"].colliderect(view):
                continue
            if r["img"] is None:
                r["img"] = _roof_image(r)
            img = r["img"]
            if r["alpha"] < 255:
                img = img.copy()
                img.set_alpha(int(r["alpha"]))
            out.append((r["sort_y"], img, (r["rect"].x - cam_x, r["rect"].y - cam_y)))
        return out
