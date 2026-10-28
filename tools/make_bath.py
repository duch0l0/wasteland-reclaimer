"""
Купальни Зайзикса: чаша бассейна, сливная решётка и крючки для раздевалок (tools/build_zzyzx.py).

Вода кодом пола «~» внутри помещения читается лужей — плоский синий прямоугольник с тонкой каймой.
Поэтому чаша — картинка из клеток пака pool, как фонтан на бульваре (tools/make_fountain.py):
кафельный бортик, вода с плиткой на дне, ступени входа в южном борту, вход трубы в восточный борт
и сливная решётка на дне. Южная полоса бортика остаётся проходимой — по ней ходят и с неё входят.

  zz_bath_pool   14×6 клеток (672×288): бортик + вода; нижняя клетка ряда — дорожка со ступенями
  zz_bath_drain  1×1 — чугунная решётка слива в полу
  zz_hooks       1×1 — доска с крючками и висящим полотенцем (настенное, ставится с подъёмом dy)
  zz_hatch       1×1 — люк в цистерну: чугунная крышка с накладкой и замком (стоит на клетке портала)

Запуск из папки game_project:  .venv/bin/python tools/make_bath.py
"""
import json
import os
import random
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.display.set_mode((1, 1))
from src import props as P  # noqa: E402

T = 48
CW, CH = 14, 6                       # чаша: 14 клеток в ширину, 6 в глубину
POOL = "assets/town/props/zz_bath_pool.png"
DRAIN = "assets/town/props/zz_bath_drain.png"
HOOKS = "assets/town/props/zz_hooks.png"
HATCH = "assets/town/props/zz_hatch.png"


def pool():
    rim = P.pack_image("pk:pool/p1/14,0,1,1")          # тёплые каменные плиты бортика — не путать с водой
    water = [P.pack_image(f"pk:pool/p1/{x},{y},1,1") for x, y in
             ((4, 4), (5, 4), (6, 4), (7, 4), (4, 5), (5, 5))]      # вода с рябью (как у фонтана)
    img = pygame.Surface((CW * T, CH * T), pygame.SRCALPHA)
    for cy in range(CH):                                   # бортик под всей чашей
        for cx in range(CW):
            img.blit(rim, (cx * T, cy * T))

    left, right = 24, CW * T - 24                          # вода: по бокам полклетки бортика
    top, bottom = 44, (CH - 1) * T                         # сверху бортик шире, снизу — дорожка со ступенями
    rnd = random.Random(1907)
    for y in range(top, bottom, T):
        for x in range(left, right, T):
            w = min(T, right - x)
            h = min(T, bottom - y)
            img.blit(water[rnd.randrange(len(water))], (x, y), (0, 0, w, h))

    # ---- ступени входа: три подводные ступени в южном борту (клетки 4..7 по ширине)
    sx0, sx1 = 4 * T, 8 * T
    for i, band in enumerate((26, 20, 14)):                # три полосы, каждая уже предыдущей — сход в воду
        by = bottom - 12 - i * 12
        pygame.draw.rect(img, (206, 198, 180), (sx0 + i * 6, by, (sx1 - sx0) - i * 12, band))
        pygame.draw.rect(img, (120, 114, 100), (sx0 + i * 6, by, (sx1 - sx0) - i * 12, band), 2)
    pygame.draw.rect(img, (232, 226, 208), (sx0, bottom - 12, sx1 - sx0, 12))      # порог у самой воды
    pygame.draw.rect(img, (150, 144, 128), (sx0, bottom - 12, sx1 - sx0, 12), 2)

    # ---- вода не обрывается: кромка, тень северного бортика
    inner = pygame.Rect(left, top, right - left, bottom - top)
    pygame.draw.rect(img, (226, 238, 244), inner, 2)                     # светлая кромка воды
    shade = pygame.Surface((inner.w, 9), pygame.SRCALPHA)                # бортик бросает тень на воду
    shade.fill((16, 44, 70, 96))
    img.blit(shade, inner.topleft)
    pygame.draw.rect(img, (74, 84, 92), inner, 4)                        # внутренняя кромка чаши

    # ---- вход трубы в восточный борт: вода приходит из насосной (tools/make_pipes.py)
    ty = 3 * T + 6                                                       # та же строка, что и труба на полу (y=9)
    pygame.draw.rect(img, (28, 32, 38), (right - 4, ty - 4, CW * T - right + 2, 34))     # гнездо в борту
    pygame.draw.rect(img, (60, 64, 70), (right, ty, CW * T - right, 26))                 # тело трубы
    pygame.draw.rect(img, (120, 128, 136), (right, ty + 4, CW * T - right, 8))           # блик
    pygame.draw.rect(img, (86, 94, 102), (right, ty + 14, CW * T - right, 8))
    pygame.draw.rect(img, (150, 156, 160), (right, ty, 5, 26))                           # фланец у стенки чаши

    # ---- слив на дне чаши (чугунная решётка)
    gx, gy = left + 44, bottom - 62
    pygame.draw.rect(img, (44, 48, 54), (gx - 2, gy - 2, 40, 40))
    pygame.draw.rect(img, (92, 100, 108), (gx, gy, 36, 36))
    for i in range(1, 5):
        pygame.draw.line(img, (40, 44, 50), (gx + i * 7, gy + 2), (gx + i * 7, gy + 34), 3)
    pygame.draw.rect(img, (60, 66, 74), (gx, gy, 36, 36), 2)

    # ---- лицевая грань бортика снизу и внешний контур
    pygame.draw.rect(img, (128, 122, 108), img.get_rect(), 2)
    pygame.draw.line(img, (176, 170, 152), (3, CH * T - 4), (CW * T - 4, CH * T - 4), 4)
    pygame.image.save(img, POOL)
    return img


def drain():
    img = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(img, (58, 62, 66), (6, 6, T - 12, T - 12))
    pygame.draw.rect(img, (96, 102, 108), (9, 9, T - 18, T - 18))
    for i in range(1, 6):
        pygame.draw.line(img, (40, 44, 48), (9 + i * 6, 11), (9 + i * 6, T - 13), 3)
    pygame.draw.rect(img, (120, 126, 130), (6, 6, T - 12, T - 12), 2)
    pygame.image.save(img, DRAIN)
    return img


def hatch():
    """Люк в цистерну: чугунная круглая крышка с петлёй слева, накладкой и висячим замком — видно, что заперт."""
    img = pygame.Surface((T, T), pygame.SRCALPHA)
    c = (T // 2, T // 2 + 1)
    pygame.draw.circle(img, (0, 0, 0, 70), (c[0] + 2, c[1] + 3), 21)          # тень под крышкой
    pygame.draw.circle(img, (46, 48, 52), c, 21)                              # обойма
    pygame.draw.circle(img, (86, 90, 96), c, 18)
    pygame.draw.circle(img, (66, 70, 76), c, 15)
    for ang in range(0, 360, 45):                                             # насечка на крышке
        import math
        a = math.radians(ang)
        pygame.draw.line(img, (52, 55, 60), (c[0] + int(6 * math.cos(a)), c[1] + int(6 * math.sin(a))),
                         (c[0] + int(14 * math.cos(a)), c[1] + int(14 * math.sin(a))), 2)
    for bx, by in ((-11, -10), (11, -10), (-11, 10), (11, 10)):               # болты по обойме
        pygame.draw.circle(img, (150, 152, 148), (c[0] + bx, c[1] + by), 2)
    pygame.draw.rect(img, (58, 60, 64), (1, c[1] - 5, 7, 10))                 # петля слева
    pygame.draw.rect(img, (108, 110, 114), (2, c[1] - 4, 4, 8))
    pygame.draw.rect(img, (40, 42, 46), (c[0] - 4, c[1] + 12, 8, 7))          # накладка с проушиной
    pygame.draw.rect(img, (26, 29, 26), (c[0] - 2, c[1] + 16, 4, 5))
    pygame.draw.rect(img, (176, 146, 64), (c[0] - 5, c[1] + 17, 10, 9), border_radius=2)   # замок
    pygame.draw.rect(img, (208, 176, 88), (c[0] - 5, c[1] + 17, 10, 3), border_radius=2)
    pygame.draw.arc(img, (150, 120, 50), (c[0] - 4, c[1] + 12, 8, 9), 0.3, 2.8, 2)         # дужка замка
    pygame.draw.circle(img, (60, 50, 20), (c[0], c[1] + 21), 1)                            # скважина
    pygame.image.save(img, HATCH)
    return img


def hooks():
    """Доска с крючками на стене: рейка, три крючка, на левом — полотенце, на правом — рубаха."""
    img = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(img, (58, 44, 32), (4, 6, T - 8, 11))
    pygame.draw.rect(img, (96, 74, 52), (4, 6, T - 8, 4))
    for px in (12, 24, 36):
        pygame.draw.circle(img, (150, 150, 148), (px, 17), 3)
        pygame.draw.line(img, (176, 176, 172), (px, 19), (px, 25), 2)
        pygame.draw.line(img, (176, 176, 172), (px, 25), (px + 3, 25), 2)
    cloth = pygame.Surface((13, 26), pygame.SRCALPHA)             # полотенце на левом крючке
    cloth.fill((214, 214, 200))
    pygame.draw.rect(cloth, (176, 176, 162), (0, 0, 13, 26), 2)
    pygame.draw.line(cloth, (150, 190, 200), (0, 9), (12, 9), 2)
    img.blit(cloth, (7, 16))
    shirt = pygame.Surface((15, 22), pygame.SRCALPHA)              # чья-то рубаха на правом
    shirt.fill((150, 120, 92))
    pygame.draw.rect(shirt, (118, 92, 68), (0, 0, 15, 22), 2)
    pygame.draw.line(shirt, (118, 92, 68), (7, 2), (7, 20), 1)
    img.blit(shirt, (30, 16))
    pygame.image.save(img, HOOKS)
    return img


def main():
    sizes = {"zz_bath_pool": pool(), "zz_bath_drain": drain(), "zz_hooks": hooks(), "zz_hatch": hatch()}
    idx = "assets/town/index.json"                 # размер картинки — для каталога объектов (src/props.py)
    d = json.load(open(idx, encoding="utf-8"))
    for name, img in sizes.items():
        d[name] = {"size": list(img.get_size()), "made_by": "tools/make_bath.py"}
    json.dump(d, open(idx, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("нарисовано:", ", ".join(f"{n} {img.get_size()}" for n, img in sizes.items()))


if __name__ == "__main__":
    main()
