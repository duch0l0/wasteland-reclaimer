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


def make_beetle():
    base = load("dog")
    out = {}
    for d, frames in base.items():
        out[d] = []
        for i, f in enumerate(frames):
            w, h = f.get_size()
            small = pygame.transform.smoothscale(f, (w * 32 // h, 32))
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


# ----------------------------------------------------------------

MAKERS = {"raider": make_raider, "gang": make_gang, "boss": make_boss, "beetle": make_beetle}


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
        print("готово:", sid)
    if "preview" in sys.argv:
        path = sys.argv[sys.argv.index("preview") + 1] if len(sys.argv) > sys.argv.index("preview") + 1 \
            else os.path.join(ROOT, "assets", "_preview_variants.png")
        preview(list(MAKERS), path)
        print("превью:", path)


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
