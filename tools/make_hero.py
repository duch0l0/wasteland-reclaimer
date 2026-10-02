"""
Герой по слоям: основа (житель folk_j), броня на теле, головной убор, оружие в руках.

Все слои — кадры одного размера (холст CW×CH, ноги героя на нижнем крае), поэтому игра
просто кладёт их друг на друга (src/hero_look.py) по тому, что надето и что в руках.

  assets/hero/base/<действие>/<сторона>/<кадр>.png
  assets/hero/body_<id>/…    броня: tire — куртка из покрышек, signs — бронежилет из
                             дорожных знаков, robe — балахон послушника
  assets/hero/head_<id>/…    головной убор: hardhat — каска строителя, moto — мотошлем
  assets/hero/weapon_<id>/…  оружие: melee (лом), pistol (самопал), pistol10, rifle,
                             shotgun, assault

Действия: walk (4 кадра, кадр 1 — стоит), melee (удар ломом: замах, удар, доводка),
shoot (выстрел: прицел, вспышка, отдача с дымком). Стороны: down, left, right, up.

Броня и шлемы перекрашивают пиксели самой основы в своей зоне (голова — верхние 45% силуэта,
туловище — до 75%), поэтому повторяют силуэт и шагают вместе с героем. Оружие — из листа
npc/raw/weapons.png (те же стволы, что на иконках предметов), лом рисуется. Влево —
зеркало правой стороны; вверх — оружие за спиной героя (слой кладётся первым).

Запуск из папки game_project (после tools/slice_sprites.py):  .venv/bin/python tools/make_hero.py
"""
import json
import math
import os
import shutil
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_item_icons import objects  # noqa: E402

BASE = os.path.join("assets", "sprites", "folk_j")
OUT = os.path.join("assets", "hero")
SHEET = os.path.join("npc", "raw", "weapons.png")
CW, CH = 112, 92
DIRS = ["down", "left", "right", "up"]
WALK = [0, 1, 2, 3]
INK = (24, 20, 26)
SKIN = (236, 190, 150)

# оружие: номер на листе, длина в пикселях, хват и дуло (доли картинки, ствол смотрит вправо)
GUNS = {
    "pistol": (66, 20, (0.30, 0.55), (1.0, 0.22)),
    "pistol10": (81, 21, (0.30, 0.55), (1.0, 0.22)),
    "rifle": (3, 44, (0.30, 0.62), (1.0, 0.30)),
    "shotgun": (20, 40, (0.32, 0.62), (1.0, 0.30)),
    "assault": (72, 39, (0.36, 0.55), (1.0, 0.25)),
}
LONG = {"rifle", "shotgun", "assault"}


# ------------------------------------------------------------ основа
def base_frames():
    out = {}
    for d in DIRS:
        out[d] = []
        for i in WALK:
            img = pygame.image.load(os.path.join(BASE, d, f"{i}.png"))
            c = pygame.Surface((CW, CH), pygame.SRCALPHA)
            c.blit(img, ((CW - img.get_width()) // 2, CH - img.get_height()))
            out[d].append(c)
    return out


def zones(frame):
    """Зоны силуэта: (рамка, конец головы, конец туловища)."""
    r = pygame.mask.from_surface(frame, 40).get_bounding_rects()[0]
    return r, r.top + int(r.h * 0.45), r.top + int(r.h * 0.75)


def is_skin(c):
    return c.r > 170 and c.g > 120 and c.r > c.g > c.b and c.r - c.b > 40


def lum(c):
    return (c.r + c.g + c.b) / 765


def recolor(frame, rows, paint, skip_skin=True):
    """Слой: пиксели основы в строках rows перекрашены paint(x, y, яркость) (None — оставить пустым)."""
    out = pygame.Surface((CW, CH), pygame.SRCALPHA)
    for y in rows:
        for x in range(CW):
            c = frame.get_at((x, y))
            if c.a < 40 or (skip_skin and is_skin(c)):
                continue
            if lum(c) < 0.12:            # контур оставляем контуром
                out.set_at((x, y), (*INK, c.a))
                continue
            col = paint(x, y, lum(c))
            if col:
                out.set_at((x, y), (*col, c.a))
    return out


def shade(color, l, k=1.0):
    f = (0.5 + 0.9 * l) * k
    return tuple(max(0, min(255, int(v * f))) for v in color)


# ------------------------------------------------------------ броня
def body_tire(frame, d):
    r, hy, ty = zones(frame)
    return recolor(frame, range(hy, ty + 2), lambda x, y, l: shade((70, 68, 66), l, 0.9 if (x + y) % 4 else 0.65))


def body_signs(frame, d):
    r, hy, ty = zones(frame)
    cx, cy = r.centerx, (hy + ty) // 2

    def paint(x, y, l):
        if d == "up":                                           # на спине — жёлто-чёрные полосы
            return shade((230, 196, 40), l) if ((x + y) // 3) % 2 else shade((40, 36, 30), l)
        if d == "down" and abs(x - cx) + abs(y - cy) <= 6:      # на груди — знак «Стоп»
            return (220, 220, 220) if abs(x - cx) + abs(y - cy) == 6 else shade((200, 40, 36), l, 1.2)
        if d in ("left", "right"):
            return shade((200, 40, 36), l)
        return shade((190, 194, 198), l)
    return recolor(frame, range(hy, ty + 2), paint)


def body_robe(frame, d):
    r, hy, ty = zones(frame)
    out = recolor(frame, range(hy, r.bottom - 2), lambda x, y, l: shade((220, 208, 178), l))
    # ряса книзу расширяется колоколом: щель между ног закрашена
    for y in range(ty, r.bottom - 2):
        xs = [x for x in range(CW) if frame.get_at((x, y)).a >= 40]
        if xs:
            for x in range(xs[0] + 1, xs[-1]):
                if out.get_at((x, y)).a < 40:
                    out.set_at((x, y), shade((200, 188, 158), 0.5))
    return out


# ------------------------------------------------------------ головные уборы
def head_hardhat(frame, d):
    r, hy, ty = zones(frame)
    top_end = r.top + int((hy - r.top) * 0.42)
    out = recolor(frame, range(r.top, top_end), lambda x, y, l: shade((236, 196, 48), l, 1.1), skip_skin=False)
    xs = [x for x in range(CW) if frame.get_at((x, top_end)).a >= 40]
    if xs:                                                      # козырёк каски
        for x in range(xs[0] - 2, xs[-1] + 3):
            out.set_at((x, top_end), (170, 130, 24))
            out.set_at((x, top_end + 1), INK)
    return out


def head_moto(frame, d):
    r, hy, ty = zones(frame)
    hh = hy - r.top
    v0, v1 = r.top + int(hh * 0.45), r.top + int(hh * 0.75)
    cx = r.centerx

    def paint(x, y, l):
        if v0 <= y <= v1 and d != "up":
            side = {"down": True, "left": x < cx + 2, "right": x > cx - 2}[d]
            if side:
                return (70, 110, 150) if y == v0 + 1 else (34, 44, 64)    # визор с бликом
        return shade((150, 32, 30), l, 1.15)
    return recolor(frame, range(r.top, r.top + int(hh * 0.92)), paint, skip_skin=False)


# ------------------------------------------------------------ оружие
def gun_image(sheet, rects, key):
    idx, length, grip, muzzle = GUNS[key]
    r = rects[idx]
    img = sheet.subsurface(r).copy()
    k = length / r.w
    img = pygame.transform.smoothscale(img, (length, max(3, round(r.h * k))))
    return img, (grip[0] * img.get_width(), grip[1] * img.get_height()), \
        (muzzle[0] * img.get_width(), muzzle[1] * img.get_height())


def crowbar():
    """Лом: ржавый прут с загнутым «клювом», ствол смотрит вправо, хват — слева."""
    img = pygame.Surface((30, 9), pygame.SRCALPHA)
    pygame.draw.line(img, INK, (0, 5), (27, 5), 4)
    pygame.draw.line(img, (150, 60, 44), (1, 5), (26, 5), 2)
    pygame.draw.line(img, (196, 96, 70), (1, 4), (26, 4), 1)
    pygame.draw.lines(img, INK, False, [(25, 5), (28, 2), (29, 0)], 3)
    pygame.draw.lines(img, (150, 60, 44), False, [(25, 5), (28, 2)], 1)
    return img, (4, 5), (29, 1)


def place(layer, img, grip, at, angle, scale=1.0):
    """Положить оружие так, чтобы точка хвата оказалась в at, повернув на angle градусов."""
    if scale != 1.0:
        img = pygame.transform.smoothscale(img, (max(2, int(img.get_width() * scale)), img.get_height()))
        grip = (grip[0] * scale, grip[1])
    side = int(max(img.get_size()) * 2 + 4)
    pad = pygame.Surface((side, side), pygame.SRCALPHA)
    pad.blit(img, (side / 2 - grip[0], side / 2 - grip[1]))
    rot = pygame.transform.rotate(pad, angle)
    layer.blit(rot, rot.get_rect(center=at))


def rotate_vec(v, angle):
    a = math.radians(angle)
    return (v[0] * math.cos(a) + v[1] * math.sin(a), -v[0] * math.sin(a) + v[1] * math.cos(a))


def hand(layer, at):
    x, y = int(at[0]), int(at[1])
    pygame.draw.rect(layer, INK, (x - 2, y - 2, 5, 5))
    pygame.draw.rect(layer, SKIN, (x - 1, y - 1, 3, 3))


def flash(layer, at, big=True):
    x, y = at
    rr = 7 if big else 4
    pts = [(x + math.cos(a) * (rr if i % 2 == 0 else rr / 2.5), y + math.sin(a) * (rr if i % 2 == 0 else rr / 2.5))
           for i, a in enumerate([k * math.pi / 5 for k in range(10)])]
    pygame.draw.polygon(layer, (255, 220, 110), pts)
    pygame.draw.circle(layer, (255, 255, 230), (int(x), int(y)), 2)


def smoke(layer, at):
    x, y = at
    for dx, dy, r in ((2, -2, 3), (5, -5, 2), (0, -6, 2)):
        pygame.draw.circle(layer, (190, 190, 180, 150), (int(x + dx), int(y + dy)), r)


def hand_point(frame, d):
    r, hy, ty = zones(frame)
    fx = {"down": 0.74, "right": 0.62, "up": 0.92, "left": 0.38}[d]   # вверх — у правого плеча
    fy = {"down": 0.62, "right": 0.60, "up": 0.48, "left": 0.60}[d]   # вверх — у плеча: ствол над ним
    return (r.x + r.w * fx, r.top + r.h * fy)


def weapon_layer(frame, d, key, action, i, gun):
    """Слой оружия для стороны d (left — зеркало right делается снаружи)."""
    img, grip, muzzle = gun
    layer = pygame.Surface((CW, CH), pygame.SRCALPHA)
    at = hand_point(frame, d)
    melee = key == "melee"
    fore = 1.0
    if action == "walk":
        angle = {"right": -60 if melee else -32, "down": -100 if melee else -90, "up": 80 if melee else 90}[d]
    elif action == "melee":
        angle = {"right": (115, 5, -55), "down": (150, -40, -100), "up": (60, 100, 140)}[d][i]
    else:   # shoot
        angle = {"right": 0, "down": -65, "up": 75}[d]
        if d != "right":
            fore = 0.75    # ствол на зрителя или от него — короче
    if action == "shoot" and i == 2:                      # отдача: ствол чуть назад
        back = rotate_vec((-2, 0), angle)
        at = (at[0] + back[0], at[1] + back[1])
    place(layer, img, grip, at, angle, fore)
    hand(layer, at)
    if not melee and key in LONG and action != "walk":   # вторая рука — на цевье
        v = rotate_vec(((img.get_width() * 0.62 - grip[0]) * fore, 0), angle)
        hand(layer, (at[0] + v[0], at[1] + v[1]))
    if action == "shoot":
        mv = rotate_vec(((muzzle[0] - grip[0]) * fore, muzzle[1] - grip[1]), angle)
        mp = (at[0] + mv[0], at[1] + mv[1])
        if i == 1:
            flash(layer, mp)
        elif i == 2:
            smoke(layer, mp)
    if action == "melee" and i == 1:                       # росчерк удара
        rr = pygame.Rect(0, 0, 44, 30)
        rr.center = (at[0] + (10 if d == "right" else 0), at[1] - 4)
        pygame.draw.arc(layer, (255, 240, 200), rr, -0.6, 1.8, 2)
    return layer


# ------------------------------------------------------------ сборка
def save_layer(name, frames):
    for (action, d, i), img in frames.items():
        folder = os.path.join(OUT, name, action, d)
        os.makedirs(folder, exist_ok=True)
        pygame.image.save(img, os.path.join(folder, f"{i}.png"))


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    pygame.display.set_mode((1, 1))
    shutil.rmtree(OUT, ignore_errors=True)
    base = base_frames()
    stand = {d: base[d][1] for d in DIRS}
    poses = {("walk", d, i): base[d][i] for d in DIRS for i in range(4)}
    poses.update({(a, d, i): stand[d] for a in ("melee", "shoot") for d in DIRS for i in range(3)})
    save_layer("base", poses)
    for name, fn in (("body_tire", body_tire), ("body_signs", body_signs), ("body_robe", body_robe),
                     ("head_hardhat", head_hardhat), ("head_moto", head_moto)):
        save_layer(name, {k: fn(f, k[1]) for k, f in poses.items()})
    sheet = pygame.image.load(SHEET)
    rects = objects(sheet)
    for key in ("melee",) + tuple(GUNS):
        gun = crowbar() if key == "melee" else gun_image(sheet, rects, key)
        frames = {}
        for (action, d, i), f in poses.items():
            if (action == "melee") != (key == "melee") and action != "walk":
                continue          # лом не стреляет, ружьём не машут
            if d == "left":
                continue
            frames[(action, d, i)] = weapon_layer(f, d, key, action, i, gun)
            if d == "right":   # влево — зеркало правой стороны
                frames[(action, "left", i)] = pygame.transform.flip(frames[(action, d, i)], True, False)
        save_layer(f"weapon_{key}", frames)
    with open(os.path.join(OUT, "info.json"), "w", encoding="utf-8") as fh:
        json.dump({"size": [CW, CH], "base": "folk_j", "made_by": "tools/make_hero.py"}, fh)
    print(f"герой: слои -> {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
