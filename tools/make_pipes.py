"""
Труба, лежащая на земле (вид сверху), — прямые куски и угол 48×48: в наборах есть только колена-обломки и
стояки. Серая сталь с ржавыми пятнами и фланцами на стыках, под трубой — тень. Первая — у Зайзикса: труба
от пруда «Сладкая вода» к фильтру (tools/build_zzyzx.py).

  zz_pipe_h — вдоль запад—восток, zz_pipe_v — вдоль север—юг, zz_pipe_ne / zz_pipe_nw — угол: труба
  приходит с севера и уходит на восток / на запад; zz_pipe_intake — водозабор с раструбом и решёткой (конец
  в воде), zz_pipe_inlet — колено у самой земли: с севера и на восток, в основание бака.

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
    elif name == "zz_pipe_intake":          # водозабор: раструб с решёткой опущен в воду, вокруг — рябь
        straight(img, False, rnd, 16, T)
        flange(img, False, T - 3)
        for r, col in ((15, (226, 240, 246, 150)), (12, (255, 255, 255, 110))):   # пена вокруг раструба
            pygame.draw.ellipse(img, col, (T // 2 - r - 2, 14 - r // 2, 2 * r + 4, r + 6), 1)
        pygame.draw.ellipse(img, DARK, (c - 5, 6, W + 10, 14))           # раструб шире трубы
        pygame.draw.ellipse(img, MID, (c - 4, 7, W + 8, 11))
        pygame.draw.ellipse(img, (30, 40, 48), (c - 1, 9, W + 2, 7))     # тёмный зев
        for gx in range(c + 1, c + W, 4):                                 # решётка от мусора
            pygame.draw.line(img, LIGHT, (gx, 9), (gx, 15))
    elif name == "zz_pipe_inlet":           # с севера и на восток у самой земли: входит в основание бака
        low = T - W - 6
        straight(img, False, rnd, 0, low + W)
        straight(img, True, rnd, c, T, c=low)
        pygame.draw.rect(img, DARK, (c - 2, low - 2, W + 4, W + 4), 2)   # литое колено
        flange(img, True, T - 6)
    else:                                   # угол: с севера до центра, от центра на восток или запад
        straight(img, False, rnd, 0, c + W)
        if name == "zz_pipe_ne":
            straight(img, True, rnd, c, T)
        else:
            straight(img, True, rnd, 0, c + W)
        pygame.draw.rect(img, DARK, (c - 2, c - 2, W + 4, W + 4), 2)     # литое колено
    return img


def main():
    names = ("zz_pipe_h", "zz_pipe_v", "zz_pipe_ne", "zz_pipe_nw", "zz_pipe_intake", "zz_pipe_inlet")
    for i, n in enumerate(names):
        pygame.image.save(make(n, 31 + i), f"{OUT}/{n}.png")
    idx = "assets/town/index.json"                  # размер картинки — для каталога объектов (src/props.py)
    d = json.load(open(idx, encoding="utf-8"))
    for n in names:
        d[n] = {"size": [T, T], "made_by": "tools/make_pipes.py"}
    json.dump(d, open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("нарисовано:", ", ".join(names))


if __name__ == "__main__":
    main()
