"""
Труба, лежащая на земле (вид сверху), — прямые куски, колена, кран 48×48: в наборах есть только колена-обломки и
стояки. Серая сталь с ржавыми пятнами и фланцами на стыках, под трубой — тень. Первая — у Зайзикса: труба
от пруда «Сладкая вода» к фильтру (tools/build_zzyzx.py).

  zz_pipe_h — вдоль запад—восток, zz_pipe_v — вдоль север—юг; zz_pipe_sw / _ne / _nw — колена юг—запад,
  север—восток, север—запад; zz_pipe_bury_w —
  труба уходит в песок на запад (тает под засыпкой: дальше к воде идёт под землёй); zz_pipe_inlet — колено у
  самой земли: с севера и на восток, в основание бака; zz_pipe_outlet — выход из-под бака на запад;
  zz_pipe_v_up — короткий кусок от низа клетки до днища бака, наверху фланец; zz_pipe_tap — кран с вентилем и струёй на западном конце.

Запуск из папки game_project:  .venv/bin/python tools/make_pipes.py
"""
import json
import random

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
T = 48
OUT = "assets/town/props"
W = 18                                      # толщина трубы, px
DARK, MID, LIGHT, HI = (64, 68, 74), (104, 110, 116), (138, 144, 150), (176, 182, 186)
RUST, RUST_D = (150, 86, 46), (112, 60, 34)
SHADOW = (0, 0, 0, 70)


def straight(img, horizontal, rnd, x0=0, x1=T, c=None):
    """Кусок трубы вдоль оси: тень, тело с бликом, ржавые пятна; x0..x1 — какой отрезок клетки,
    c — где лежит труба поперёк (по умолчанию посередине клетки)."""
    c = (T - W) // 2 if c is None else c
    if horizontal:
        pygame.draw.rect(img, SHADOW, (x0, c + 4, x1 - x0, W))
        pygame.draw.rect(img, DARK, (x0, c, x1 - x0, W))
        pygame.draw.rect(img, MID, (x0, c + 2, x1 - x0, W - 4))
        pygame.draw.rect(img, LIGHT, (x0, c + 3, x1 - x0, 3))
        pygame.draw.rect(img, HI, (x0, c + 4, x1 - x0, 1))
        for _ in range(2):
            rx = rnd.randrange(x0, max(x0 + 1, x1 - 8))
            pygame.draw.rect(img, RUST, (rx, c + 6, rnd.randint(4, 8), rnd.randint(3, 5)))
            pygame.draw.rect(img, RUST_D, (rx + 1, c + W - 4, 3, 2))
    else:
        pygame.draw.rect(img, SHADOW, (c + 4, x0, W, x1 - x0))
        pygame.draw.rect(img, DARK, (c, x0, W, x1 - x0))
        pygame.draw.rect(img, MID, (c + 2, x0, W - 4, x1 - x0))
        pygame.draw.rect(img, LIGHT, (c + 3, x0, 3, x1 - x0))
        pygame.draw.rect(img, HI, (c + 4, x0, 1, x1 - x0))
        for _ in range(2):
            ry = rnd.randrange(x0, max(x0 + 1, x1 - 8))
            pygame.draw.rect(img, RUST, (c + 6, ry, rnd.randint(3, 5), rnd.randint(4, 8)))
            pygame.draw.rect(img, RUST_D, (c + W - 4, ry + 1, 2, 3))


def flange(img, horizontal, at):
    """Фланец стыка: кольцо пошире трубы с болтами."""
    c = (T - W) // 2
    if horizontal:
        pygame.draw.rect(img, DARK, (at - 3, c - 3, 6, W + 6))
        pygame.draw.rect(img, LIGHT, (at - 2, c - 2, 2, W + 4))
        for by in (c - 1, c + W - 1):
            img.set_at((at, by), HI)
    else:
        pygame.draw.rect(img, DARK, (c - 3, at - 3, W + 6, 6))
        pygame.draw.rect(img, LIGHT, (c - 2, at - 2, W + 4, 2))
        for bx in (c - 1, c + W - 1):
            img.set_at((bx, at), HI)


def elbow(img, arms, rnd, row=None):
    """Колено: из центра — плечи в стороны arms (n/s/e/w); row — на какой высоте лежат плечи e/w
    (у самой земли — чтобы войти в основание бака сбоку), плечо n тогда тянется до этой высоты."""
    c = (T - W) // 2
    r = c if row is None else row
    if "n" in arms:
        straight(img, False, rnd, 0, r + W)
    if "s" in arms:
        straight(img, False, rnd, r, T)
    if "e" in arms:
        straight(img, True, rnd, c, T, c=r)
    if "w" in arms:
        straight(img, True, rnd, 0, c + W, c=r)
    pygame.draw.rect(img, DARK, (c - 2, r - 2, W + 4, W + 4), 2)          # литое колено


def make(name, seed):
    rnd = random.Random(seed)
    img = pygame.Surface((T, T), pygame.SRCALPHA)
    c = (T - W) // 2
    if name == "zz_pipe_h":
        straight(img, True, rnd)
        flange(img, True, T - 3)
    elif name == "zz_pipe_v":
        straight(img, False, rnd)
        flange(img, False, T - 3)
    elif name == "zz_pipe_inlet":           # с севера и на восток у самой земли: входит в основание бака
        low = T - W - 6
        straight(img, False, rnd, 0, low + W)
        straight(img, True, rnd, c, T, c=low)
        pygame.draw.rect(img, DARK, (c - 2, low - 2, W + 4, W + 4), 2)   # литое колено
        flange(img, True, T - 6)
    elif name == "zz_pipe_bury_w":          # труба плавно уходит в песок на запад: тело тает, над концом — засыпка
        body = pygame.Surface((T, T), pygame.SRCALPHA)
        straight(body, True, rnd)
        for x in range(T):                                   # к западу всё глубже в песке — прозрачнее
            a = int(255 * max(0.0, min(1.0, (x - 4) / 30)))
            for y in range(T):
                px = body.get_at((x, y))
                if px.a:
                    body.set_at((x, y), (px.r, px.g, px.b, px.a * a // 255))
        img.blit(body, (0, 0))
        for r, col in ((0, (180, 146, 98, 60)), (3, (196, 160, 110, 70)), (6, (170, 134, 90, 60))):   # засыпанная траншея
            pygame.draw.ellipse(img, col, (4 + r, c - 6 + r, 16 - r, W + 12 - 2 * r))
        for k in range(6):                                   # редкие комья
            pygame.draw.rect(img, (160, 126, 84, 160), (7 + rnd.randrange(8), c - 2 + rnd.randrange(W + 4), 2, 2))
    elif name in ("zz_pipe_sw", "zz_pipe_ne", "zz_pipe_nw"):
        elbow(img, name[-2:], rnd)
    elif name == "zz_pipe_outlet":          # из-под основания бака (сверху) и на запад: чистая вода
        elbow(img, "nw", rnd)
        flange(img, False, 6)
    elif name == "zz_pipe_tap":             # кран на конце: вентиль и носик, струя вниз
        straight(img, True, rnd, 20, T)
        flange(img, True, 22)
        pygame.draw.circle(img, (150, 40, 34), (30, c - 4), 6)                # вентиль
        pygame.draw.circle(img, (200, 70, 56), (30, c - 4), 6, 2)
        pygame.draw.line(img, (90, 20, 18), (24, c - 4), (36, c - 4), 2)
        pygame.draw.rect(img, DARK, (10, c + 2, 12, W - 4))                   # носик
        pygame.draw.rect(img, MID, (10, c + 4, 12, W - 8))
        pygame.draw.rect(img, DARK, (10, c + W - 6, 6, 10))
        for y in range(c + W + 4, T - 2, 3):                                  # струя
            img.set_at((12, y), (150, 200, 235))
            img.set_at((13, y + 1), (210, 235, 250))
    else:
        raise ValueError(f"нет рисунка для {name}")
    return img


def riser_up(seed):
    """Кусок под баком: труба от низа клетки до днища бака (верхние 28 px пусты), наверху фланец — стык.
    Ставится обычным слоем (не полом) на клетку бака: виден между ножек и упирается в корпус."""
    img = make("zz_pipe_v", seed)
    pygame.draw.rect(img, (0, 0, 0, 0), (0, 0, T, 28))
    img.fill((0, 0, 0, 0), (0, 0, T, 28))
    flange(img, False, 31)
    return img


def main():
    pygame.image.save(riser_up(77), f"{OUT}/zz_pipe_v_up.png")
    names = ("zz_pipe_h", "zz_pipe_v", "zz_pipe_inlet", "zz_pipe_ne", "zz_pipe_nw",
             "zz_pipe_bury_w", "zz_pipe_sw", "zz_pipe_outlet", "zz_pipe_tap")
    for i, n in enumerate(names):
        pygame.image.save(make(n, 31 + i), f"{OUT}/{n}.png")
    idx = "assets/town/index.json"                  # размер картинки — для каталога объектов (src/props.py)
    d = json.load(open(idx, encoding="utf-8"))
    for n in names:
        d[n] = {"size": [T, T], "made_by": "tools/make_pipes.py"}
    d["zz_pipe_v_up"] = {"size": [T, T], "made_by": "tools/make_pipes.py"}
    json.dump(d, open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("нарисовано:", ", ".join(names))


if __name__ == "__main__":
    main()
