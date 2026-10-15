"""
Боковые секции оград (вид на ограду «вдоль» — север—юг): горизонтальная секция, поставленная столбиком, выглядит
лестницей. Здесь рисуются звено-рейка и звено-столб 48×48 для четырёх видов оград; map.side_fence(kind, x, y0, y1)
(tools/mapkit.py) ставит столб через два звена.

Запуск из папки game_project:  .venv/bin/python tools/make_fence_side.py
"""
import json
import os

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
W = H = 48
OUT = "assets/town/props"
KINDS = {
    # имя: (цвет рейки, свет рейки, цвет столба, свет столба, цоколь, острия?)
    "wood":   ((92, 64, 42), (136, 100, 68), (74, 50, 34), (116, 82, 56), None, False),
    "wire":   ((150, 150, 156), (206, 206, 212), (96, 68, 46), (138, 100, 70), None, True),
    "picket": ((96, 66, 44), (140, 104, 72), (70, 48, 32), (112, 80, 54), None, False),
    "iron":   ((44, 46, 52), (96, 100, 112), (92, 92, 86), (124, 124, 112), (62, 62, 60), True),
}


def draw(kind, with_post):
    rail, rail_l, post, post_l, plinth, tips = KINDS[kind]
    img = pygame.Surface((W, H), pygame.SRCALPHA)
    if plinth:
        pygame.draw.rect(img, plinth, (20, 0, 8, H))
        pygame.draw.rect(img, post, (21, 0, 5, H))
    if kind == "picket":
        for y in range(2, H, 6):                                   # штакетины — короткие чёрточки поперёк рейки
            pygame.draw.rect(img, rail, (19, y, 10, 3))
            pygame.draw.rect(img, rail_l, (19, y, 10, 1))
        pygame.draw.rect(img, post, (23, 0, 2, H))
    else:
        pygame.draw.rect(img, rail, (22, 0, 3, H))
        pygame.draw.rect(img, rail_l, (22, 0, 1, H))
        if kind == "wire":
            for y in range(0, H, 8):                               # витки колючки
                pygame.draw.line(img, rail_l, (19, y), (28, y + 4))
                pygame.draw.line(img, rail_l, (28, y), (19, y + 4))
        if kind == "wood":
            pygame.draw.rect(img, rail, (20, 0, 7, 2))
        if tips:
            for y in range(3, H, 8):
                pygame.draw.rect(img, rail_l, (21, y, 5, 2))
    if with_post:
        pygame.draw.rect(img, post, (19, 10, 10, 26))
        pygame.draw.rect(img, post_l, (19, 10, 10, 3))
        pygame.draw.rect(img, (0, 0, 0, 90), (19, 33, 10, 3))
    return img


names = []
for kind in KINDS:
    for with_post in (False, True):
        name = f"x_fs_{kind}" + ("_post" if with_post else "")
        pygame.image.save(draw(kind, with_post), os.path.join(OUT, f"{name}.png"))
        names.append(name)
if "iron" in KINDS:                                        # кованая ограда кладбища — отдельное имя, уже зарегистрирована
    pass

p = "data/props.json"
d = json.load(open(p, encoding="utf-8"))
tgt = d["props"] if "props" in d else d
for n in names:
    tgt[n] = {"img": n, "foot": [1, 1], "block": True, "sight": False}
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
p = "assets/town/index.json"
d = json.load(open(p, encoding="utf-8"))
t = d["props"] if "props" in d else d
for n in names:
    t[n] = {"size": [W, H], "made_by": "tools/make_fence_side.py"}
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("нарисовано:", len(names))
