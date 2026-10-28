"""
Чаша фонтана для площади Зайзикса (5×4 клетки): белый кафельный бортик с тенью и внутри вода с рябью —
из клеток набора pool. Готового уличного фонтана в наборах нет (только кибер-тумбы), а вода кодом пола
у движка — пруд с песчаным берегом. Статуя в центре — отдельный объект (tools/build_zzyzx.py).

Запуск из папки game_project:  .venv/bin/python tools/make_fountain.py
"""
import json
import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.display.set_mode((1, 1))
from src import props as P   # noqa: E402

T = 48
CW, CH = 5, 4                       # клеток: бортик по краю, вода внутри 3×2
OUT = "assets/town/props/zz_fountain_pool.png"


def main():
    rim = P.pack_image("pk:pool/p1/0,0,1,1")
    water = [P.pack_image(f"pk:pool/p1/{x},{y},1,1") for x, y in ((4, 4), (5, 4), (6, 5), (7, 4))]
    img = pygame.Surface((CW * T, CH * T), pygame.SRCALPHA)
    for cy in range(CH):
        for cx in range(CW):
            img.blit(rim, (cx * T, cy * T))
    inner = pygame.Rect(T // 2, T // 2, (CW - 1) * T, (CH - 1) * T)        # вода шире кафеля: бортик в полклетки
    for i, y in enumerate(range(inner.top, inner.bottom, T)):
        for j, x in enumerate(range(inner.left, inner.right, T)):
            img.blit(water[(i * 3 + j) % len(water)], (x, y), (0, 0, min(T, inner.right - x), min(T, inner.bottom - y)))
    shade = pygame.Surface((inner.w, 8), pygame.SRCALPHA)                   # северный бортик бросает тень на воду
    shade.fill((20, 40, 70, 90))
    img.blit(shade, inner.topleft)
    pygame.draw.rect(img, (70, 78, 86), inner, 2)                            # внутренняя кромка
    pygame.draw.rect(img, (120, 120, 116), img.get_rect(), 2)                # внешняя кромка бортика
    pygame.draw.line(img, (150, 150, 146), (2, CH * T - 4), (CW * T - 3, CH * T - 4), 3)   # лицевая грань снизу
    pygame.image.save(img, OUT)
    idx = "assets/town/index.json"                  # размер картинки — для каталога объектов (src/props.py)
    d = json.load(open(idx, encoding="utf-8"))
    d["zz_fountain_pool"] = {"size": list(img.get_size()), "made_by": "tools/make_fountain.py"}
    json.dump(d, open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(OUT, img.get_size())


if __name__ == "__main__":
    main()
