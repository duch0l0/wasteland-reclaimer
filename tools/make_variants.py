"""
Новые персонажи, дорисованные на основе уже нарезанных (assets/sprites/<id>/):

  raider      — рейдер: из Панка. Красный ирокез, бандана на лице, наплечник
                с шипами, пыльные штаны, ржавые ботинки;
  gang        — бандит Бензо-банды: из героя. Противогаз с янтарными линзами
                и фильтром, промасленная кожанка с жёлтой полосой, джинса;
  boss        — Шрам, главарь Бензо-банды: из Панка. Бритый череп, шрам через
                всё лицо, светящийся глаз, красная кожанка, два наплечника;
  beetle      — панцирный жук: из пса. Хитин с отливом, шов по панцирю,
                усики, жвалы, лишняя пара лап, светящиеся глазки.

Кадры пиксельные (игра увеличивает их вдвое), лежат как у остальных:
assets/sprites/<id>/{down,left,right,up}/0..3.png. Игра подхватывает их сама
(src/location.py → loader.load_directional_animations).

Запуск из папки game_project (после tools/slice_sprites.py):
    .venv/bin/python tools/make_variants.py            — сделать кадры
    .venv/bin/python tools/make_variants.py preview    — ещё и превью в assets/_preview_variants.png
"""
import os
import shutil
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "assets", "sprites")
DIRS = ("down", "right", "up", "left")

INK = (9, 12, 13)                   # контур у листов персонажей
SKIN = {(249, 197, 164), (187, 135, 94), (168, 112, 76), (248, 203, 160), (216, 153, 63)}
MOHAWK = [(155, 250, 4), (114, 209, 3), (99, 174, 2), (73, 126, 20)]


# ---------------------------------------------------------------- инструменты

def load(sid):
    out = {}
    for d in DIRS:
        folder = os.path.join(SPRITES, sid, d)
        names = sorted(os.listdir(folder), key=lambda n: int(n.split(".")[0]))
        out[d] = [pygame.image.load(os.path.join(folder, n)).convert_alpha() for n in names]
    return out


def save(sid, frames):
    dst = os.path.join(SPRITES, sid)
    shutil.rmtree(dst, ignore_errors=True)
    for d, lst in frames.items():
        os.makedirs(os.path.join(dst, d), exist_ok=True)
        for i, img in enumerate(lst):
            pygame.image.save(img, os.path.join(dst, d, f"{i}.png"))


def rgb(img, x, y):
    c = img.get_at((x, y))
    return None if c.a < 10 else (c.r, c.g, c.b)


def put(img, x, y, color):
    if 0 <= x < img.get_width() and 0 <= y < img.get_height():
        img.set_at((x, y), color)


def top_row(img):
    return img.get_bounding_rect(min_alpha=10).top


def row_span(img, y):
    xs = [x for x in range(img.get_width()) if rgb(img, x, y)]
    return (xs[0], xs[-1]) if xs else None


def recolor(img, mapping, rows=None):
    """Замена цветов палитры (точное совпадение); rows — только в этих строках."""
    h = img.get_height()
    for y in (rows if rows is not None else range(h)):
        if not 0 <= y < h:
            continue
        for x in range(img.get_width()):
            c = rgb(img, x, y)
            if c in mapping:
                img.set_at((x, y), (*mapping[c], img.get_at((x, y)).a))


def ramp(src_colors, dst_colors):
    return dict(zip(src_colors, dst_colors))


def pad(img, dx, dy=0, w=None, h=None):
    """Кадр побольше (под детали, выходящие за силуэт); персонаж — по центру, ноги внизу."""
    w = w or img.get_width() + 2 * dx
    h = h or img.get_height() + dy
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(img, ((w - img.get_width()) // 2, h - img.get_height()))
    return out


def outline_px(img, pts, color, edge=INK):
    """Нарисовать пиксели и обвести их контуром там, где рядом пусто."""
    for x, y in pts:
        put(img, x, y, color)
    s = set(pts)
    for x, y in pts:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in s or not (0 <= nx < img.get_width() and 0 <= ny < img.get_height()):
                continue
            if rgb(img, nx, ny) is None:
                img.set_at((nx, ny), edge)


# ---------------------------------------------------------------- люди

METAL = [(58, 60, 66), (112, 114, 120), (176, 178, 182)]


def shoulder_pad(img, x0, y0, flip=False):
    """Наплечник из покрышки/жести с двумя шипами. x0,y0 — левый верх пластины."""
    dark, mid, hi = METAL
    plate = [(x0 + i, y0 + j) for i in range(4) for j in range(3)]
    outline_px(img, plate, mid)
    for i in range(4):
        put(img, x0 + i, y0, hi)
    put(img, x0 + (3 if flip else 0), y0 + 2, dark)
    for sx in ((x0 + 1, x0 + 3) if not flip else (x0, x0 + 2)):
        outline_px(img, [(sx, y0 - 1), (sx, y0 - 2)], hi)
        put(img, sx, y0 - 1, mid)


def face_rows(img, top, first, last):
    return range(top + first, top + last + 1)


def cover_skin(img, rows, colors, x_range=None):
    """Закрыть кожу в строках (бандана, маска). colors — по строкам, по кругу."""
    for k, y in enumerate(rows):
        for x in range(img.get_width()):
            if x_range and not x_range[0] <= x <= x_range[1]:
                continue
            if rgb(img, x, y) in SKIN:
                img.set_at((x, y), colors[k % len(colors)])


PANTS_BLUE = [(35, 47, 68), (97, 110, 131), (198, 207, 229)]


def make_raider():
    base = load("loner")
    out = {}
    red_hawk = [(255, 96, 40), (222, 62, 30), (178, 40, 26), (112, 26, 22)]
    rust = [(170, 96, 44), (140, 70, 34), (120, 58, 30), (84, 40, 24)]
    khaki = [(74, 60, 40), (128, 104, 70), (184, 160, 116)]
    bandana = [(176, 36, 36), (132, 24, 28)]
    for d, frames in base.items():
        out[d] = []
        for f in frames:
            img = pad(f, 2, 2)
            t = top_row(img)
            recolor(img, ramp(MOHAWK, red_hawk), range(0, t + 9))
            recolor(img, ramp(MOHAWK, rust), range(t + 9, img.get_height()))
            recolor(img, ramp(PANTS_BLUE, khaki))
            recolor(img, {(53, 61, 47): (78, 52, 36)})  # куртка — выгоревшая кожа
            if d == "down":
                cover_skin(img, face_rows(img, t, 13, 15), bandana)
                sp = row_span(img, t + 18)
                shoulder_pad(img, sp[0], t + 17)
            elif d == "up":
                sp = row_span(img, t + 18)
                shoulder_pad(img, sp[1] - 3, t + 17, flip=True)
                for y in (t + 13, t + 14):   # узел банданы на затылке
                    xs = row_span(img, y)
                    put(img, (xs[0] + xs[1]) // 2, y, bandana[0])
                    put(img, (xs[0] + xs[1]) // 2 + 1, y, bandana[1])
            else:
                cover_skin(img, face_rows(img, t, 15, 17), bandana)
                sp = row_span(img, t + 19)
                back = sp[0] + 1 if d == "right" else sp[1] - 4
                shoulder_pad(img, back, t + 18, flip=d == "left")
            out[d].append(img)
    return out


def make_gang():
    base = load("player")
    out = {}
    jacket = {(60, 66, 77): (58, 42, 30), (77, 82, 81): (74, 54, 36), (88, 95, 91): (92, 68, 44),
              (108, 115, 113): (116, 86, 54)}
    pants = {(180, 171, 128): (70, 84, 112), (153, 152, 127): (52, 64, 90), (210, 190, 143): (96, 112, 140),
             (135, 137, 121): (44, 54, 76), (190, 185, 153): (110, 124, 150)}
    mask, mask_hi = (78, 84, 76), (122, 130, 116)
    lens, lens_hi = (255, 168, 36), (255, 236, 150)
    for d, frames in base.items():
        out[d] = []
        for f in frames:
            img = pad(f, 2, 1)
            t = top_row(img)
            recolor(img, jacket)
            recolor(img, pants)
            # жёлтая полоса «Бензо» поперёк куртки
            for x in range(img.get_width()):
                y = t + 20
                if rgb(img, x, y) not in (None, INK, (12, 13, 40)):
                    img.set_at((x, y), (230, 190, 40) if x % 3 else (40, 34, 20))
            if d == "up":   # ремни маски на затылке
                sp = row_span(img, t + 9)
                for x in range(sp[0] + 1, sp[1]):
                    put(img, x, t + 9, (40, 36, 30))
                out[d].append(img)
                continue
            skin = [(x, y) for y in range(t + 7, t + 14) for x in range(img.get_width())
                    if rgb(img, x, y) in SKIN]
            if not skin:
                out[d].append(img)
                continue
            x0, x1 = min(p[0] for p in skin), max(p[0] for p in skin)
            y0, y1 = min(p[1] for p in skin), max(p[1] for p in skin)
            for x, y in skin:
                img.set_at((x, y), mask)
            for x in range(x0, x1 + 1):
                if rgb(img, x, y0) == mask:
                    img.set_at((x, y0), mask_hi)
            if d == "down":
                cx = (x0 + x1) // 2
                for lx in (cx - 2, cx + 2):   # линзы
                    outline_px(img, [(lx, y0 + 1)], lens)
                    put(img, lx, y0 + 1, lens_hi if lx < cx else lens)
                can = [(cx - 1, y1 + 1), (cx, y1 + 1), (cx + 1, y1 + 1), (cx - 1, y1 + 2), (cx, y1 + 2), (cx + 1, y1 + 2)]
                outline_px(img, can, (60, 64, 58))
                put(img, cx, y1 + 1, (150, 156, 140))
                put(img, cx, y1 + 2, (30, 30, 30))
            else:
                fwd = 1 if d == "right" else -1
                front = x1 if d == "right" else x0
                put(img, front - fwd, y0 + 1, lens)
                put(img, front, y0 + 1, lens_hi)
                can = [(front + fwd, y1), (front + 2 * fwd, y1), (front + fwd, y1 + 1), (front + 2 * fwd, y1 + 1)]
                outline_px(img, can, (60, 64, 58))
                put(img, front + 2 * fwd, y1, (150, 156, 140))
            out[d].append(img)
    return out


def make_boss():
    base = load("loner")
    out = {}
    coat = {(53, 61, 47): (120, 26, 26)}
    pants = ramp(PANTS_BLUE, [(26, 24, 28), (58, 54, 60), (104, 98, 104)])
    scar, scar_hi = (150, 40, 50), (214, 112, 112)
    for d, frames in base.items():
        out[d] = []
        for f in frames:
            img = pad(f, 2, 2)
            t = top_row(img)
            # бритый череп: ирокез долой, на его месте — щетина по коже
            for y in range(0, t + 9):
                for x in range(img.get_width()):
                    if rgb(img, x, y) in MOHAWK:
                        below = rgb(img, x, y + 1)
                        img.set_at((x, y), (150, 110, 84) if below in SKIN else (0, 0, 0, 0))
            for _ in range(2):   # ободок ирокеза, повисший в воздухе
                for y in range(0, t + 9):
                    for x in range(img.get_width()):
                        c = rgb(img, x, y)
                        if c in ((129, 77, 57), (94, 46, 29), INK) and not any(
                                rgb(img, x + dx, y + 1) in SKIN | {(150, 110, 84)} for dx in (-1, 0, 1)):
                            img.set_at((x, y), (0, 0, 0, 0))
            recolor(img, ramp(MOHAWK, [(90, 30, 24), (70, 24, 20), (60, 20, 18), (40, 14, 12)]))
            recolor(img, coat)
            recolor(img, pants)
            if d != "up":
                skin = [(x, y) for y in range(t, t + 17) for x in range(img.get_width()) if rgb(img, x, y) in SKIN]
                if skin:
                    x0, x1 = min(p[0] for p in skin), max(p[0] for p in skin)
                    y0 = min(p[1] for p in skin)
                    # шрам — по диагонали через лицо, с розовым краем
                    sx, ex = (x0 + 1, x1 - 1) if d != "left" else (x1 - 1, x0 + 1)
                    n = abs(ex - sx) + 1
                    for i in range(n):
                        x = sx + (i if ex >= sx else -i)
                        y = y0 + 3 + i * 9 // max(1, n)
                        if rgb(img, x, y) in SKIN or rgb(img, x, y) == INK:
                            img.set_at((x, y), scar)
                            if rgb(img, x, y - 1) in SKIN:
                                img.set_at((x, y - 1), scar_hi)
                # глаз под шрамом светится
                eyes = [(x, y) for y in range(t + 10, t + 16) for x in range(img.get_width())
                        if rgb(img, x, y) in ((254, 254, 254), INK) and rgb(img, x, y - 1) in SKIN | {scar, scar_hi}]
                if eyes:
                    ex_, ey_ = min(eyes) if d != "left" else max(eyes)
                    put(img, ex_, ey_, (255, 60, 40))
            if d in ("down", "up"):
                sp = row_span(img, t + 18)
                shoulder_pad(img, sp[0] - 1, t + 17)
                shoulder_pad(img, sp[1] - 2, t + 17, flip=True)
            else:
                sp = row_span(img, t + 19)
                shoulder_pad(img, sp[0] + 1 if d == "right" else sp[1] - 4, t + 18, flip=d == "left")
            # патронташ через грудь
            if d == "down":
                for i in range(7):
                    x, y = sp[0] + 3 + i, t + 19 + i
                    if rgb(img, x, y):
                        img.set_at((x, y), (200, 160, 60) if i % 2 else (90, 60, 30))
            out[d].append(img)
    return out


# ---------------------------------------------------------------- жук из пса

CHITIN = [(14, 18, 24), (26, 40, 48), (38, 62, 66), (52, 90, 84), (82, 128, 102), (150, 206, 140)]
GLOW = (190, 255, 120)
SHELL = [(30, 34, 58), (44, 58, 86), (58, 92, 104), (84, 132, 118), (132, 186, 150), (196, 236, 190)]


def make_beetle(height=32):
    base = load("dog")
    out = {}
    for d, frames in base.items():
        out[d] = []
        for i, f in enumerate(frames):
            w, h = f.get_size()
            small = pygame.transform.smoothscale(f, (w * height // h, height))
            img = pad(small, 5, 4)
            # хитин: цвет по яркости, полупрозрачная тень пса — долой
            for y in range(img.get_height()):
                for x in range(img.get_width()):
                    c = img.get_at((x, y))
                    if c.a < 150:
                        img.set_at((x, y), (0, 0, 0, 0))
                        continue
                    lum = (c.r * 3 + c.g * 5 + c.b) / 9 / 255
                    k = min(len(CHITIN) - 1, int(lum ** 1.4 * (len(CHITIN) + 0.6)))
                    img.set_at((x, y), (*CHITIN[k], 255))
            bb = img.get_bounding_rect(min_alpha=10)
            # тёмный контур по краю силуэта
            edge = [(x, y) for y in range(bb.top, bb.bottom) for x in range(bb.left, bb.right)
                    if rgb(img, x, y) and any(rgb(img, nx, ny) is None for nx, ny in
                                              ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))]
            for x, y in edge:
                img.set_at((x, y), CHITIN[0])
            step = 1 if i % 2 == 0 else -1    # лапы переставляются на каждом шаге
            leg = CHITIN[1]
            cx = bb.centerx
            if d in ("down", "up"):
                head_y = bb.top + (4 if d == "down" else 0)
                # шов по спине — надкрылья
                if d == "up":
                    for y in range(bb.top + 5, bb.bottom - 2):
                        if rgb(img, cx, y):
                            img.set_at((cx, y), CHITIN[0])
                            put(img, cx - 1, y, CHITIN[4] if y % 3 == 0 else rgb(img, cx - 1, y) or CHITIN[2])
                # лишние лапы по бокам: две пары, сгиб наружу
                mid = bb.top + bb.h * 5 // 9
                for side in (-1, 1):
                    xe = bb.left if side < 0 else bb.right - 1
                    for j, yy in enumerate((mid - 3, mid + 2)):
                        s = step if j == 0 else -step
                        pts = [(xe + side, yy), (xe + 2 * side, yy - 1 + s), (xe + 3 * side, yy + s),
                               (xe + 3 * side, yy + 1 + s)]
                        for p in pts:
                            put(img, *p, leg)
                # усики
                for side in (-1, 1):
                    for k in range(5):
                        put(img, cx + side * (2 + k // 2 + k // 4), head_y - 1 - k, CHITIN[0 if k < 4 else 4])
                if d == "down":
                    # жвалы и глазки
                    my = bb.top + 12
                    for side in (-1, 1):
                        for p in ((cx + side * 2, my), (cx + side * 3, my + 1), (cx + side * 2, my + 2),
                                  (cx + side, my + 3)):
                            put(img, *p, CHITIN[0])
                        put(img, cx + side * 2, my + 1, CHITIN[4])
                        put(img, cx + side * 3, bb.top + 7, GLOW)
            else:
                fwd = 1 if d == "right" else -1
                front = bb.right - 1 if d == "right" else bb.left
                head_top = bb.top
                # надкрылья: купол от затылка до хвоста, поверх собачьей спины
                rear = bb.left if d == "right" else bb.right - 1
                x_a, x_b = sorted((rear, front - 8 * fwd))
                ex, ey = (x_a + x_b) / 2, bb.top + 11
                rx, ry = (x_b - x_a) / 2 + 1, 7
                dome = [(x, y) for y in range(bb.top, bb.bottom) for x in range(x_a - 1, x_b + 2)
                        if ((x - ex) / rx) ** 2 + ((y - ey) / ry) ** 2 <= 1 and y <= ey + 2]
                ys = [p[1] for p in dome]
                for x, y in dome:
                    k = (y - min(ys)) / max(1, max(ys) - min(ys))
                    img.set_at((x, y), SHELL[min(len(SHELL) - 1, int((1 - k) * len(SHELL)))])
                for x, y in dome:
                    if any((nx, ny) not in set(dome) for nx, ny in ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1))):
                        img.set_at((x, y), CHITIN[0])
                for x in range(x_a + 2, x_b - 1):   # блик и шов надкрылий
                    top_y = min(y for xx, y in dome if xx == x)
                    put(img, x, top_y + 1, SHELL[-1] if (x - x_a) % 5 else SHELL[-2])
                    put(img, x, int(ey + 1), CHITIN[0])
                # две лишние лапы под брюхом
                foot = bb.bottom - 1
                for j, lx in enumerate((cx - 3 * fwd, cx + 1 * fwd)):
                    s = step if j == 0 else -step
                    for k, p in enumerate(((lx, foot - 4), (lx + s, foot - 2), (lx + s, foot - 1), (lx + s + fwd, foot))):
                        put(img, *p, leg if k < 3 else CHITIN[0])
                # усики — вперёд-вверх от головы
                for k in range(7):
                    put(img, front - 3 * fwd + fwd * (k // 2 + k // 5), head_top - 1 - k + k // 4, CHITIN[0 if k < 6 else 4])
                # жвалы
                my = bb.top + 11
                for p in ((front + fwd, my), (front + 2 * fwd, my + 1), (front + fwd, my + 2), (front + 2 * fwd, my + 3)):
                    put(img, *p, CHITIN[0])
                put(img, front - 3 * fwd, bb.top + 6, GLOW)
            out[d].append(img)
    return out


# ---------------------------------------------------------------- жители Пятнадцатой

BLONDE = [(212, 188, 63), (141, 119, 31), (248, 252, 148), (85, 68, 23), (194, 171, 53)]
BLONDIE_TOP = [(67, 31, 25), (69, 52, 29), (147, 68, 61), (175, 89, 87), (180, 60, 60), (213, 110, 134),
               (252, 135, 111)]
HERO_HAIR = [(12, 13, 40), (32, 37, 58), (60, 66, 77), (86, 43, 45), (46, 27, 34)]
HERO_CLOTHES = [(60, 66, 77), (77, 82, 81), (88, 95, 91), (108, 115, 113)]
HERO_PANTS = [(180, 171, 128), (153, 152, 127), (210, 190, 143), (135, 137, 121), (190, 185, 153)]
LONER_SKIN = [(249, 197, 164), (187, 135, 94), (168, 112, 76), (129, 77, 57), (94, 46, 29)]


def variant(base_id, fn, dx=2, dy=2):
    """Кадры base_id, пропущенные через fn(img, direction, top)."""
    out = {}
    for d, frames in load(base_id).items():
        out[d] = []
        for f in frames:
            img = pad(f, dx, dy)
            fn(img, d, top_row(img))
            out[d].append(img)
    return out


def rows_from(t, a, b=None):
    return range(t + a, t + b if b is not None else 200)


def shave(img, t):
    """Ирокез Панка долой — бритая голова со щетиной (как у Шрама)."""
    for y in range(0, t + 9):
        for x in range(img.get_width()):
            if rgb(img, x, y) in MOHAWK:
                below = rgb(img, x, y + 1)
                img.set_at((x, y), (150, 110, 84) if below in SKIN else (0, 0, 0, 0))
    for _ in range(2):
        for y in range(0, t + 9):
            for x in range(img.get_width()):
                c = rgb(img, x, y)
                if c in ((129, 77, 57), (94, 46, 29), INK) and not any(
                        rgb(img, x + dx, y + 1) in SKIN | {(150, 110, 84)} for dx in (-1, 0, 1)):
                    img.set_at((x, y), (0, 0, 0, 0))


def hat(img, t, d, crown=((70, 46, 30), (104, 70, 44)), band=(40, 28, 20)):
    """Шляпа с полями поверх волос героя."""
    hair = row_span(img, t + 3)
    if not hair:
        return
    x0, x1 = hair
    for y in range(t - 2, t + 4):          # тулья
        for x in range(x0 + 2, x1 - 1):
            put(img, x, y, crown[1] if y < t + 1 else crown[0])
    for x in range(x0 + 2, x1 - 1):
        put(img, x, t - 3, INK)
        put(img, x, t + 2, band)
    for x in range(x0 - 2, x1 + 3):        # поля
        put(img, x, t + 4, crown[0])
        put(img, x, t + 5, INK)
    put(img, x0 - 3, t + 4, INK)
    put(img, x1 + 3, t + 4, INK)


def make_ada():
    """Смотрительница Ада Кросс: седые волосы, комбинезон Vault-Tec — синий с жёлтым."""
    def fn(img, d, t):
        recolor(img, ramp(BLONDE, [(196, 198, 206), (120, 122, 134), (236, 238, 244), (74, 76, 88), (166, 168, 180)]))
        recolor(img, ramp(BLONDIE_TOP, [(24, 44, 96), (30, 54, 112), (44, 80, 156), (60, 104, 190), (226, 190, 60),
                                        (232, 198, 70), (244, 214, 96)]), rows_from(t, 12))
        recolor(img, {(38, 40, 59): (22, 34, 74), (61, 66, 92): (40, 70, 140), (86, 100, 111): (52, 88, 168),
                      (117, 134, 159): (70, 110, 196)})
        # жёлтая полоса на поясе и цифры «57» не влезут — хватит полосы
        y = t + 21
        sp = row_span(img, y)
        if sp:
            for x in range(sp[0] + 1, sp[1]):
                if rgb(img, x, y) not in (None, (13, 13, 26)):
                    img.set_at((x, y), (232, 200, 64))
    return variant("blondie", fn)


def make_doc():
    """Док Мира Сол: тёмные волосы, белый халат с красным крестом."""
    def fn(img, d, t):
        recolor(img, ramp(BLONDE, [(92, 58, 42), (58, 36, 26), (134, 90, 62), (38, 24, 18), (78, 50, 36)]))
        recolor(img, ramp(BLONDIE_TOP, [(150, 152, 162), (170, 172, 180), (212, 214, 222), (236, 238, 242),
                                        (204, 40, 40), (220, 60, 60), (236, 236, 240)]), rows_from(t, 12))
        recolor(img, {(38, 40, 59): (178, 180, 190), (61, 66, 92): (206, 208, 216)}, rows_from(t, 14, 27))
        if d == "down":
            sp = row_span(img, t + 17)
            if sp:
                cx = sp[0] + 3
                for p in ((cx, t + 16), (cx - 1, t + 17), (cx, t + 17), (cx + 1, t + 17), (cx, t + 18)):
                    put(img, *p, (210, 36, 36))
    return variant("blondie", fn)


def make_sheriff():
    """Шериф Коул Брэддок: шляпа, пыльник, звезда на груди."""
    def fn(img, d, t):
        recolor(img, ramp(HERO_CLOTHES, [(118, 88, 54), (136, 104, 64), (156, 120, 78), (184, 148, 98)]),
                rows_from(t, 12))
        hat(img, t, d)
        if d in ("down", "right", "left"):
            sp = row_span(img, t + 17)
            if sp:
                x = sp[0] + 4 if d != "left" else sp[1] - 4
                if d == "right":
                    x = (sp[0] + sp[1]) // 2 + 1
                put(img, x, t + 16, (255, 220, 80))
                put(img, x, t + 17, (200, 160, 40))
    return variant("player", fn, dy=4)


def make_silas():
    """Брат Сайлас: балахон «Детей Единства» с капюшоном."""
    robe = [(110, 104, 92), (150, 142, 124), (182, 174, 154), (212, 204, 184)]
    def fn(img, d, t):
        recolor(img, ramp(HERO_HAIR[1:3], [robe[0], robe[1]]), rows_from(t, 0, 13))    # капюшон
        recolor(img, ramp(HERO_CLOTHES, robe), rows_from(t, 12))
        recolor(img, ramp(HERO_PANTS, [robe[2], robe[1], robe[3], robe[0], robe[2]]))
        recolor(img, {(32, 37, 58): robe[0]}, rows_from(t, 13))
        if d == "down":   # знак Единства — круг на груди
            sp = row_span(img, t + 18)
            if sp:
                cx = (sp[0] + sp[1]) // 2
                for p in ((cx, t + 17), (cx - 1, t + 18), (cx + 1, t + 18), (cx, t + 19)):
                    put(img, *p, (200, 150, 60))
    return variant("player", fn)


def make_mo():
    """Мо «Ведро», хозяин салуна: бритый, борода, фартук поверх рубахи."""
    def fn(img, d, t):
        shave(img, t)
        recolor(img, {(53, 61, 47): (104, 34, 30)})
        recolor(img, ramp(PANTS_BLUE, [(150, 146, 136), (206, 202, 190), (236, 234, 226)]))
        if d != "up":
            cover_skin(img, face_rows(img, t, 14 if d == "down" else 16, 17), [(110, 66, 36), (86, 50, 28)])
    return variant("loner", fn)


def make_lenny():
    """Пьяница Лен: лохматый рыжий, зелёная куртка, красный нос."""
    def fn(img, d, t):
        recolor(img, ramp(MOHAWK, [(214, 120, 50), (180, 90, 40), (150, 70, 30), (100, 48, 24)]), range(0, t + 9))
        recolor(img, ramp(MOHAWK, [(90, 60, 30), (70, 46, 24), (60, 40, 20), (40, 28, 16)]), rows_from(t, 9))
        recolor(img, {(53, 61, 47): (64, 84, 40)})
        recolor(img, ramp(PANTS_BLUE, [(62, 46, 34), (104, 80, 56), (150, 120, 86)]))
        if d == "down":
            sp = row_span(img, t + 13)
            if sp:
                put(img, (sp[0] + sp[1]) // 2, t + 13, (220, 70, 60))
    return variant("loner", fn)


def make_folk_a():
    """Жительница: рыжие волосы, зелёное платье."""
    def fn(img, d, t):
        recolor(img, ramp(BLONDE, [(190, 90, 40), (130, 56, 24), (230, 140, 70), (80, 34, 16), (170, 76, 34)]))
        recolor(img, ramp(BLONDIE_TOP, [(36, 60, 30), (44, 72, 36), (70, 110, 56), (96, 140, 74), (180, 60, 60),
                                        (120, 160, 90), (150, 190, 110)]), rows_from(t, 12))
    return variant("blondie", fn)


def make_folk_b():
    """Житель: светлые волосы, коричневая куртка, серые штаны."""
    def fn(img, d, t):
        recolor(img, ramp(HERO_HAIR[1:3], [(170, 140, 70), (220, 190, 110)]), rows_from(t, 0, 13))
        recolor(img, ramp(HERO_CLOTHES, [(80, 56, 36), (96, 68, 44), (112, 82, 54), (134, 100, 66)]), rows_from(t, 12))
        recolor(img, ramp(HERO_PANTS, [(110, 110, 116), (88, 88, 96), (136, 136, 142), (70, 70, 78), (150, 150, 156)]))
    return variant("player", fn)


def make_merc():
    """Наёмник Дэкс: каска, куртка хаки, тёмные штаны, ремень винтовки через грудь
    (тот самый выживший, за которого играешь в Барстоу)."""
    helmet = [(62, 72, 48), (86, 98, 64), (110, 124, 82)]
    def fn(img, d, t):
        recolor(img, ramp(HERO_CLOTHES, [(112, 98, 66), (128, 112, 76), (146, 128, 88), (168, 150, 104)]),
                rows_from(t, 12))
        recolor(img, ramp(HERO_PANTS, [(64, 66, 56), (54, 56, 48), (80, 82, 70), (46, 48, 40), (90, 92, 78)]))
        hair = row_span(img, t + 4)
        if hair:   # каска: купол поверх волос
            x0, x1 = hair
            for y in range(t - 1, t + 6):
                w = min(y - t + 3, 4)
                for x in range(x0 + 3 - w, x1 - 2 + w):
                    put(img, x, y, helmet[1] if y < t + 2 else helmet[0])
            for x in range(x0 - 1, x1 + 2):
                put(img, x, t + 6, helmet[0])
                put(img, x, t + 7, INK)
            for x in range(x0 + 2, x1 - 1):
                put(img, x, t - 2, INK)
            put(img, (x0 + x1) // 2 - 2, t + 1, helmet[2])
        if d in ("down", "up"):   # ремень винтовки через грудь (спину)
            for i in range(9):
                x, y = (row_span(img, t + 15) or (0, 0))[0] + 2 + i, t + 15 + i
                if rgb(img, x, y) not in (None, INK):
                    img.set_at((x, y), (60, 40, 26))
        else:                     # ствол за плечом
            sp = row_span(img, t + 14)
            if sp:
                bx = sp[0] + 1 if d == "right" else sp[1] - 1
                for k in range(10):
                    put(img, bx - (k // 3 if d == "right" else -(k // 3)), t + 6 + k, (40, 40, 44))
    return variant("player", fn, dy=3)


# ---------------------------------------------------------------- новые враги

def make_feral():
    """Дикий гуль: гнилая кожа, клочья одежды, горящие глаза."""
    rot = [(150, 138, 96), (112, 98, 66), (98, 82, 54), (80, 60, 40), (60, 42, 30)]
    def fn(img, d, t):
        shave(img, t)
        recolor(img, {(150, 110, 84): (84, 70, 48)})
        recolor(img, ramp(LONER_SKIN, rot))
        recolor(img, {(254, 254, 254): (250, 230, 90)})
        recolor(img, {(53, 61, 47): (58, 50, 40)})
        recolor(img, ramp(PANTS_BLUE, [(52, 46, 40), (76, 68, 58), (104, 94, 80)]))
        recolor(img, ramp(MOHAWK, [(90, 80, 50)] * 4))
        # дыры в одежде — сквозь них видна кожа
        import random
        r = random.Random(d)
        for _ in range(9):
            x, y = r.randrange(img.get_width()), r.randrange(t + 16, img.get_height() - 4)
            if rgb(img, x, y) not in (None, INK):
                img.set_at((x, y), rot[r.randrange(3)])
    return variant("loner", fn)


ROACH = [(20, 12, 10), (56, 28, 18), (96, 48, 26), (140, 74, 36), (186, 110, 56), (230, 160, 90)]


def make_roach():
    """Радтаракан: тот же приём, что у жука, только мельче, рыжий и с длинными усами."""
    global CHITIN, SHELL, GLOW
    saved = CHITIN, SHELL, GLOW
    CHITIN, SHELL, GLOW = ROACH, [ROACH[1], ROACH[2], ROACH[3], ROACH[4], ROACH[5], (250, 200, 140)], (255, 120, 80)
    try:
        return make_beetle(height=18)
    finally:
        CHITIN, SHELL, GLOW = saved


def make_turret():
    """Турель Vault-Tec: шестигранное основание с жёлто-чёрной разметкой, тумба, купол со
    стальным бликом, сдвоенные стволы по направлению, мигающий красный датчик и полоса
    Vault-Tec. Рисуется мелким пиксель-артом 34×34 (игра увеличивает вдвое), контур — общий INK."""
    W_, H_ = 34, 34
    steel, steel_hi, steel_lo, dark = (110, 118, 126), (176, 186, 194), (70, 76, 84), (34, 38, 44)
    out = {}
    for d in DIRS:
        out[d] = []
        for i in range(4):
            img = pygame.Surface((W_, H_), pygame.SRCALPHA)
            cx = W_ // 2
            # основание: шестигранная плита, по краю — жёлто-чёрные полосы
            base = [(cx - 12, 28), (cx - 7, 24), (cx + 7, 24), (cx + 12, 28), (cx + 7, 32), (cx - 7, 32)]
            pygame.draw.polygon(img, steel_lo, base)
            for k in range(-11, 12, 4):
                pygame.draw.line(img, (220, 180, 40), (cx + k, 31), (cx + k + 2, 29))
            pygame.draw.polygon(img, dark, base, 1)
            pygame.draw.rect(img, steel_lo, (cx - 3, 18, 7, 8))          # тумба
            pygame.draw.line(img, steel, (cx - 2, 18), (cx - 2, 25))
            # стволы — до или после купола, чтобы «назад» они прятались за ним
            def barrels():
                if d == "down":
                    for bx in (cx - 3, cx + 2):
                        pygame.draw.rect(img, dark, (bx, 16, 2, 9))
                elif d == "up":
                    for bx in (cx - 3, cx + 2):
                        pygame.draw.rect(img, dark, (bx, 2, 2, 8))
                else:
                    sgn = 1 if d == "right" else -1
                    x0 = cx + (6 if sgn > 0 else -16)
                    for by in (11, 14):
                        pygame.draw.rect(img, dark, (x0, by, 10, 2))
                    pygame.draw.rect(img, (250, 220, 120) if i == 0 else dark,
                                     (x0 + (10 if sgn > 0 else -1), 11, 1, 5))   # вспышка на первом кадре
            if d == "up":
                barrels()
            pygame.draw.ellipse(img, steel, (cx - 8, 6, 17, 14))            # купол
            pygame.draw.ellipse(img, steel_hi, (cx - 6, 7, 8, 5))           # блик
            pygame.draw.line(img, (40, 90, 170), (cx - 7, 15), (cx + 7, 15))   # полоса Vault-Tec
            pygame.draw.line(img, (230, 190, 60), (cx - 7, 16), (cx + 7, 16))
            pygame.draw.ellipse(img, dark, (cx - 8, 6, 17, 14), 1)
            if d != "up":
                barrels()
            eye = (255, 70, 40) if i % 2 == 0 else (130, 24, 18)
            ex = {"down": cx, "up": cx, "left": cx - 4, "right": cx + 4}[d]
            if d != "up":
                pygame.draw.rect(img, eye, (ex - 1, 10, 3, 2))
            # общий контур
            mask = pygame.mask.from_surface(img, 10)
            for y in range(H_):
                for x in range(W_):
                    if not mask.get_at((x, y)) and any(0 <= x + dx < W_ and 0 <= y + dy < H_ and mask.get_at((x + dx, y + dy))
                                                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        img.set_at((x, y), INK)
            out[d].append(img)
    return out


def make_ghoul_kid():
    """Ребёнок-гуль из школы: тот же дикий гуль, но на треть ниже."""
    out = {}
    for d, frames in load("feral").items():
        out[d] = [pygame.transform.scale(f, (max(1, round(f.get_width() * 0.7)), max(1, round(f.get_height() * 0.7))))
                  for f in frames]
    return out


def make_ghoul_lady():
    """Мисс Лейн, учительница-гуль: жительница folk_d, кожа серо-зелёная и в пятнах, волосы седые.
    Кадры крупные (native), как у исходника."""
    import random
    r = random.Random(41)
    out = {}
    for d, frames in load("folk_d").items():
        out[d] = []
        for f in frames:
            img = f.copy()
            w, h = img.get_size()
            for y in range(h):
                for x in range(w):
                    c = img.get_at((x, y))
                    if c.a < 40:
                        continue
                    lum = (c.r + c.g + c.b) / 3
                    if c.r > 150 and c.r > c.g > c.b and c.r - c.b > 40:          # кожа
                        k = lum / 255
                        g = (int(110 + 70 * k), int(118 + 66 * k), int(84 + 40 * k))
                        if r.random() < 0.12:
                            g = (int(g[0] * 0.7), int(g[1] * 0.62), int(g[2] * 0.6))   # язвы
                        img.set_at((x, y), (*g, c.a))
                    elif lum < 110 and abs(c.r - c.g) < 30 and y < h * 0.4:      # тёмные волосы -> седые клочья
                        v = int(130 + lum * 0.6)
                        img.set_at((x, y), (v, v, int(v * 0.95), c.a))
            out[d].append(img)
    return out


def make_joined():
    """«Сплетённый» из крипты Бейкера: фиолетовый зверь-мутант, перекрашенный в бледно-розовую плоть
    с багровыми швами, — трое прихожан, сросшихся в одно тело. Кадры native, как у исходника."""
    out = {}
    for d, frames in load("beast").items():
        out[d] = []
        for f in frames:
            img = f.copy()
            w, h = img.get_size()
            for y in range(h):
                for x in range(w):
                    c = img.get_at((x, y))
                    if c.a < 40:
                        continue
                    lum = (c.r + c.g + c.b) / 3
                    if c.b > c.g + 10:                          # фиолетовая шкура -> бледная плоть
                        k = lum / 200
                        img.set_at((x, y), (min(255, int(120 + 120 * k)), int(80 + 90 * k), int(80 + 80 * k), c.a))
                    elif lum > 150 and c.r > 150:               # рога -> багровые швы
                        img.set_at((x, y), (150, 40, 40, c.a))
            out[d].append(img)
    return out


NATIVE = {"ghoul_lady", "joined"}   # кадры уже в игровом размере


# ----------------------------------------------------------------

MAKERS = {"raider": make_raider, "gang": make_gang, "boss": make_boss, "beetle": make_beetle,
          "ada": make_ada, "doc": make_doc, "sheriff": make_sheriff, "silas": make_silas, "mo": make_mo,
          "lenny": make_lenny, "merc": make_merc, "folk_a": make_folk_a, "folk_b": make_folk_b,
          "feral": make_feral, "radroach": make_roach, "turret": make_turret,
          "ghoul_kid": make_ghoul_kid, "ghoul_lady": make_ghoul_lady, "joined": make_joined}


def preview(ids, path):
    z = 5
    rows = []
    for sid in ids:
        fr = load(sid)
        rows.append(fr)
    cell_w = max(img.get_width() for fr in rows for lst in fr.values() for img in lst) * z + 8
    cell_h = max(img.get_height() for fr in rows for lst in fr.values() for img in lst) * z + 8
    sheet = pygame.Surface((cell_w * 16, cell_h * len(ids)))
    sheet.fill((112, 100, 84))
    for r, fr in enumerate(rows):
        for c, d in enumerate(DIRS):
            for i, img in enumerate(fr[d]):
                s = pygame.transform.scale_by(img, z)
                sheet.blit(s, ((c * 4 + i) * cell_w + 4, r * cell_h + cell_h - s.get_height() - 4))
    pygame.image.save(sheet, path)


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for sid, make in MAKERS.items():
        save(sid, make())
        if sid in NATIVE:
            with open(os.path.join(SPRITES, sid, "native"), "w") as fh:
                fh.write("кадры уже в игровом размере\n")
        print("готово:", sid)
    if "preview" in sys.argv:
        path = sys.argv[sys.argv.index("preview") + 1] if len(sys.argv) > sys.argv.index("preview") + 1 \
            else os.path.join(ROOT, "assets", "_preview_variants.png")
        preview(list(MAKERS), path)
        print("превью:", path)


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
