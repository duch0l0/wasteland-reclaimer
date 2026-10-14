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
import json
import os
import random

import pygame

from . import settings as S
from . import loader
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
ROOF_TINT = {"brick": (200, 175, 150), "concrete": (225, 222, 215), "metal": (235, 225, 215), "planks": (230, 220, 210)}


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


def _roof_image(r):
    """Крыша по стилю здания, в пиксель-арте 2×2: рубероид с гравием и вентиляцией (кирпич),
    ржавый профнастил (металл), доски (дерево), бетонная плита (бетон). С парапетом."""
    w, h = (r["x1"] - r["x0"] + 1) * T, (r["y1"] - r["y0"]) * T - WALL_LIFT
    rnd = random.Random(r["seed"])
    style = r["style"]
    pal = {"brick": [(118, 94, 78), (124, 100, 82), (112, 89, 74), (130, 106, 88)],
           "concrete": [(118, 116, 110), (124, 122, 116), (110, 108, 104), (130, 127, 120)],
           "metal": [(116, 70, 48), (128, 80, 54), (104, 62, 44), (138, 90, 60)],
           "planks": [(104, 78, 54), (112, 84, 58), (96, 72, 50), (120, 90, 62)]}[style]
    img = pygame.Surface((w, h), pygame.SRCALPHA)
    tex = _roof_texture(style) if style in ("planks", "metal") else None      # плоские крыши — гудрон с гравием, без сетки плиток
    if tex is not None and style in ("planks", "metal"):
        # дранка и кровельный лист: ряды со смещёнными стыками и разбросом тона — без сетки плиток набора
        base = tuple(pygame.transform.average_color(tex[0])[:3])
        pal = [base] * 4
        rowh = 14 if style == "planks" else 24
        sw = 40 if style == "planks" else 22
        for ry, y in enumerate(range(0, h, rowh)):
            off = (ry * 17 + r["seed"]) % sw
            for sx in range(-off, w, sw):
                k = rnd.uniform(0.86, 1.1)
                col = tuple(max(0, min(255, int(c * k))) for c in base)
                img.fill(col, (max(0, sx), y, min(sw, w - max(0, sx)) - (1 if sx >= 0 else 0), rowh - 1))
                if rnd.random() < 0.1:
                    img.fill(tuple(int(c * 0.72) for c in base), (max(0, sx) + 3, y + 3, rnd.choice((6, 9)), 3))
            img.fill(tuple(int(c * 0.62) for c in base), (0, y + rowh - 1, w, 1))
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
    if style in ("planks", "metal"):
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
    if style in ("planks", "metal") and w >= 6 * T:      # большая двускатная крыша: слуховые окна, печные трубы, водосток
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
    # мелочи на крыше: короба вентиляции, люк, хлам
    for _ in range(max(1, (w * h) // (T * T * 14))):
        bw, bh = rnd.choice(((20, 16), (26, 18), (16, 16), (34, 20)))
        x, y = rnd.randrange(10, max(11, w - bw - 10), 2), rnd.randrange(10, max(11, h - bh - 14), 2)
        kind = rnd.random()
        if kind < 0.5:    # вентиляция
            pygame.draw.rect(img, (64, 66, 70), (x, y + 4, bw, bh))
            pygame.draw.rect(img, (140, 142, 146), (x, y, bw, bh))
            for k in range(3, bw - 2, 4):
                img.fill((90, 92, 96), (x + k, y + 3, 2, bh - 6))
        elif kind < 0.75:  # люк
            pygame.draw.rect(img, (50, 44, 38), (x, y, 18, 16))
            pygame.draw.rect(img, (110, 100, 88), (x + 2, y + 2, 14, 12))
            img.fill((70, 62, 54), (x + 2, y + 7, 14, 2))
        else:              # хлам: доска, бочка
            pygame.draw.rect(img, (120, 90, 60), (x, y, 28, 6))
            pygame.draw.circle(img, (80, 90, 70), (x + 36, y + 6), 6)
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


_VOID = None   # пустота за стенами интерьера — чёрная клетка (создаётся в TownMap)


class TownMap(MapBase):
    parallax = False  # земля сплошная — фон под ней не нужен

    def __init__(self, path):
        if isinstance(path, dict):    # готовая карта (случайная встреча)
            d = path
        else:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
        self.width, self.height = d["w"], d["h"]
        self.ground = d["ground"]
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
            self.objects.append({"name": name, "rect": rect, "sort_y": bottom + oy, "foot": foot,
                                 "container": None, "floor": inf["layer"] == "floor"})

        self.containers = []
        for c in d.get("containers", []):
            obj = self.objects[c["prop"]]
            box = {"tile": obj["foot"][0], "tiles": obj["foot"], "name": c["name"], "loot": dict(c["loot"]),
                   "owner": c.get("owner"), "requires": c.get("requires"), "opened": False, "obj": obj,
                   "on_put": c.get("on_put")}
            obj["container"] = box
            self.containers.append(box)

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
            if code in self.wallsets or code in "x_" or not self._tiles.get(code):
                continue
            avg = pygame.transform.average_color(self._tiles[code][0])
            if avg[2] > avg[0] + 25:              # вода — свой берег (_shore), и в подземелье тоже (канал, сток)
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
            tex = self._tiles[c][h % len(self._tiles[c])].copy()
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
            if below != "x":
                return self._face[h % len(self._face)]   # стена, обращённая к нам
            return self._rock[h % len(self._rock)]
        if code in self._tiles and self._tiles[code]:
            variants = self._tiles[code]
        else:
            variants = self._dirt_shades[self._shade(x, y)]
        return variants[h % len(variants)]

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
                surf.blit(P.image(o["name"]), (o["rect"].x - cam_x, o["rect"].y - cam_y))
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
