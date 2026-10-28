"""
«Замок» Спрингера (tools/build_zzyzx.py, раздел zzyzx_hotel): детская колыбель вдовы Харпер.

Ни в одном наборе колыбели нет: единственный похожий спрайт (hotel_1_036) — обычная односпальная
кровать с железной спинкой. Ставить чужую кровать «вместо колыбели» нельзя (docs/furnish/logic.md:
«спрайт — по месту»), поэтому колыбель нарисована здесь — один предмет, одна картинка.

  zz_cradle   1 клетка (48×48): деревянная колыбель на качалках, внутри одеяло и подушка,
              спинка выше к изголовью — та же перспектива, что у кроватей набора hotel

Запуск из папки game_project:  .venv/bin/python tools/make_zzyzx_hotel.py
"""
import json
import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.display.set_mode((1, 1))

OUT = "assets/town/props/zz_cradle.png"
WOOD = (158, 118, 76)
LIGHT = (190, 150, 104)
DARK = (104, 74, 48)
LINEN = (228, 218, 198)
LINEN_D = (204, 192, 170)


def cradle():
    """Колыбель сверху-спереди: неглубокий ящик с бортами и прутьями, внутри подушка и стёганое одеяло;
    под ящиком — качалка-полоз, концы выступают за борта. Перспектива и палитра — как у кроватей hotel."""
    s = pygame.Surface((48, 48), pygame.SRCALPHA)
    # качалка: полоз, выступающий за борта, концы загнуты
    pygame.draw.arc(s, DARK, (4, 29, 40, 15), 3.14, 6.28, 3)
    pygame.draw.arc(s, WOOD, (5, 30, 38, 13), 3.14, 6.28, 1)
    # ящик: борта
    pygame.draw.rect(s, DARK, (8, 10, 32, 28), border_radius=2)
    pygame.draw.rect(s, LIGHT, (9, 11, 30, 26), border_radius=2)
    pygame.draw.rect(s, WOOD, (12, 14, 24, 20))                          # нутро
    # прутья по бортам
    for x in range(10, 37, 3):
        pygame.draw.rect(s, DARK, (x, 11, 1, 3))
        pygame.draw.rect(s, DARK, (x, 34, 1, 2))
    for y in range(14, 34, 3):
        pygame.draw.rect(s, DARK, (9, y, 2, 1))
        pygame.draw.rect(s, DARK, (37, y, 2, 1))
    # постель: подушка у изголовья, стёганое одеяло
    pygame.draw.rect(s, (243, 239, 230), (13, 15, 22, 5))
    pygame.draw.rect(s, LINEN_D, (13, 19, 22, 1))
    pygame.draw.rect(s, LINEN, (13, 21, 22, 12))
    for y in (25, 29):
        pygame.draw.line(s, LINEN_D, (13, y), (34, y), 1)
    pygame.draw.line(s, (176, 100, 92), (13, 27), (34, 27), 1)           # розовая кайма одеяла
    return s


def main():
    img = cradle()
    pygame.image.save(img, OUT)
    d = json.load(open("assets/town/index.json", encoding="utf-8"))
    d["zz_cradle"] = {"size": list(img.get_size()), "made_by": "tools/make_zzyzx_hotel.py"}
    json.dump(d, open("assets/town/index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("нарисовано: zz_cradle", img.get_size())


if __name__ == "__main__":
    main()
