"""
«Замок» Спрингера (tools/build_zzyzx.py, раздел zzyzx_hotel): детская колыбель вдовы Харпер.

Ни в одном наборе колыбели нет: единственный похожий спрайт (hotel_1_036) — обычная односпальная
кровать с железной спинкой. Ставить чужую кровать «вместо колыбели» нельзя (docs/furnish/logic.md:
«спрайт — по месту»), поэтому колыбель нарисована здесь — один предмет, одна картинка.

  zz_cradle   40×60: детская кроватка на качалках — прутья, подушка, одеяло с розовой каймой,
              спинка выше к изголовью — та же перспектива, что у кроватей набора hotel
  zz_runner   клетка ковровой дорожки коридора (бордо, золотая кайма), стыкуется по горизонтали
  zz_safe     стальной сейф «BANK», вырезан из склейки набора west (west_2_105)

Запуск из папки game_project:  .venv/bin/python tools/make_zzyzx_hotel.py
"""
import json
import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.display.set_mode((1, 1))

WOOD = (158, 118, 76)
LIGHT = (190, 150, 104)
DARK = (104, 74, 48)
LINEN = (228, 218, 198)
LINEN_D = (204, 192, 170)


def cradle():
    """Детская кроватка в перспективе набора hotel (как кровати: вид сверху-спереди): высокая спинка
    у изголовья, решётчатые борта из прутьев, внутри подушка и стёганое одеяло с розовой каймой, у ног —
    низкая спинка, снизу — гнутые качалки. 40×60 px: в рост кроватки рядом со взрослой кроватью."""
    W, H = 40, 60
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    OUT = (54, 36, 24)
    pygame.draw.ellipse(s, (0, 0, 0, 60), (3, H - 9, W - 6, 7))               # тень на полу
    for x0 in (4, W - 12):                                                    # качалки: дуги под ножками
        pygame.draw.arc(s, OUT, (x0 - 3, H - 16, 14, 12), 3.3, 6.1, 3)
        pygame.draw.arc(s, LIGHT, (x0 - 2, H - 15, 12, 10), 3.3, 6.1, 1)
    pygame.draw.rect(s, OUT, (4, 4, W - 8, 14), border_radius=4)             # спинка изголовья
    pygame.draw.rect(s, WOOD, (5, 5, W - 10, 12), border_radius=3)
    pygame.draw.rect(s, LIGHT, (7, 6, W - 14, 3), border_radius=2)
    pygame.draw.rect(s, OUT, (4, 14, W - 8, 34))                              # короб
    pygame.draw.rect(s, WOOD, (5, 15, W - 10, 32))
    pygame.draw.rect(s, (246, 242, 234), (8, 16, W - 16, 7), border_radius=2)   # подушка
    pygame.draw.rect(s, LINEN_D, (8, 22, W - 16, 1))
    pygame.draw.rect(s, LINEN, (8, 24, W - 16, 20))                           # одеяло
    for y in (30, 36):
        pygame.draw.line(s, LINEN_D, (8, y), (W - 9, y), 1)
    pygame.draw.rect(s, (214, 140, 140), (8, 24, W - 16, 2))                  # розовая кайма
    for x in range(6, W - 5, 4):                                              # прутья бортов поверх постели
        pygame.draw.line(s, DARK, (x, 18), (x, 46), 1)
    pygame.draw.rect(s, OUT, (4, 44, W - 8, 8), border_radius=2)             # низкая спинка в ногах
    pygame.draw.rect(s, WOOD, (5, 45, W - 10, 6), border_radius=2)
    pygame.draw.rect(s, LIGHT, (6, 45, W - 12, 1))
    for x in (5, W - 8):                                                      # ножки
        pygame.draw.rect(s, OUT, (x, 51, 3, 5))
    return s


def runner():
    """Клетка ковровой дорожки коридора 48×48: бордовый ворс, золотая кайма сверху и снизу, ромбы по
    центру. Стыкуется встык по горизонтали — дорожка ложится вдоль коридора без швов."""
    import random
    rnd = random.Random(7)
    s = pygame.Surface((48, 48), pygame.SRCALPHA)
    RED, RED_D, GOLD, GOLD_D = (128, 34, 36), (96, 22, 26), (206, 164, 82), (150, 112, 50)
    s.fill(RED, (0, 6, 48, 36))
    for _ in range(90):                                                        # ворс
        s.set_at((rnd.randrange(48), rnd.randrange(8, 40)), RED_D)
    for y0 in (6, 38):                                                         # кайма
        s.fill(GOLD_D, (0, y0, 48, 4))
        s.fill(GOLD, (0, y0 + 1, 48, 2))
    for cx in (12, 36):                                                        # ромбы узора
        pygame.draw.polygon(s, GOLD_D, [(cx, 16), (cx + 7, 24), (cx, 32), (cx - 7, 24)], 2)
        s.set_at((cx, 24), GOLD)
    return s


def safe():
    """Стальной сейф «BANK» из набора west: в паке он склеен с кассой и витриной (west_2_105, 94×166),
    вырезаем только его — левый верхний кусок 48×70."""
    from src import props as P
    return P.pack_image("pk:west/west_2_105").subsurface((0, 0, 48, 70)).copy()


def main():
    d = json.load(open("assets/town/index.json", encoding="utf-8"))
    for name, img in (("zz_cradle", cradle()), ("zz_safe", safe()), ("zz_runner", runner())):
        pygame.image.save(img, f"assets/town/props/{name}.png")
        d[name] = {"size": list(img.get_size()), "made_by": "tools/make_zzyzx_hotel.py"}
        print("нарисовано:", name, img.get_size())
    json.dump(d, open("assets/town/index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
