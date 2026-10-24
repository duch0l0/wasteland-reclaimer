"""
Свои объекты карт, которых нет в наборе «wasteland town», — рисуются кодом:

  x_grave        могильный холмик (обыскивается лопатой)
  x_cross        деревянный крест          x_tombstone  надгробие
  x_vault_door   дверь-шестерня Убежища 57 в скале (снаружи)
  x_vault_gear   та же дверь изнутри убежища (x_vault_gear12 — с номером 12, Некрополь)
  x_manhole      люк ливнёвки (спуск)      x_ladder     лестница наверх с полосой света
  x_board        доска объявлений          x_sandbags   мешки с песком (низкое укрытие)
  x_cliff        скала (кусок обрыва)      x_pipe       ржавая труба у стены
  x_puddle       лужа с тиной (пол)        x_vault_sign табличка «57» Vault-Tec
  x_barrel_boom  красная бочка с горючим — взрывается от выстрела
  x_thermometer  Термометр Бейкера — «самый высокий градусник в мире», стрелка на 134 °F

Ещё здесь — описания объектов из набора «War ruins» (RUINS ниже: картинки уже нарезаны
tools/slice_ruins.py, рисовать ничего не надо — только имя, масштаб и пятно на земле).

Рисуем в половинном размере и увеличиваем вдвое без сглаживания — в тон
пиксель-арту персонажей. Картинки ложатся в assets/town/props/, размеры —
в assets/town/index.json, описания — в data/props.json (добавляются, если
их там нет; уже заданные поля не трогаются).

Запуск из папки game_project:  .venv/bin/python tools/make_props.py
"""
import json
import math
import os
import random
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "town", "props")
INDEX = os.path.join(ROOT, "assets", "town", "index.json")
CATALOG = os.path.join(ROOT, "data", "props.json")
sys.path.insert(0, ROOT)          # vault_door_cliff берёт куски наборов через src.props

INK = (20, 16, 14)
rnd = random.Random(57)


def canvas(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def px(s, x, y, c):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((int(x), int(y)), c)


def rect(s, x, y, w, h, c):
    pygame.draw.rect(s, c, (x, y, w, h))


def outline(s, color=INK):
    """Контур в 1 пиксель вокруг непрозрачного."""
    w, h = s.get_size()
    src = s.copy()
    for y in range(h):
        for x in range(w):
            if src.get_at((x, y)).a:
                continue
            if any(0 <= x + dx < w and 0 <= y + dy < h and src.get_at((x + dx, y + dy)).a > 100
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                s.set_at((x, y), color)
    return s


def noise(s, colors, n, area=None):
    x0, y0, w, h = area or (0, 0, *s.get_size())
    for _ in range(n):
        x, y = x0 + rnd.randrange(w), y0 + rnd.randrange(h)
        if s.get_at((x, y)).a > 200:
            s.set_at((x, y), rnd.choice(colors))


# ------------------------------------------------------------ рисунки (половинный размер)

def grave():
    s = canvas(24, 16)
    pygame.draw.ellipse(s, (92, 70, 48), (1, 4, 22, 11))
    pygame.draw.ellipse(s, (120, 94, 64), (3, 4, 17, 7))
    noise(s, [(70, 52, 36), (140, 112, 78), (104, 80, 56)], 40)
    return outline(s)


def cross():
    s = canvas(14, 26)
    rect(s, 6, 2, 3, 22, (110, 78, 48))
    rect(s, 2, 7, 11, 3, (110, 78, 48))
    rect(s, 7, 2, 1, 22, (146, 106, 66))
    rect(s, 2, 7, 11, 1, (146, 106, 66))
    pygame.draw.ellipse(s, (80, 60, 40), (3, 22, 9, 4))
    return outline(s)


def tombstone():
    s = canvas(16, 20)
    pygame.draw.ellipse(s, (130, 128, 122), (2, 1, 12, 10))
    rect(s, 2, 6, 12, 12, (130, 128, 122))
    rect(s, 3, 3, 4, 14, (156, 154, 146))
    rect(s, 5, 9, 6, 1, (90, 88, 84))
    rect(s, 5, 12, 5, 1, (90, 88, 84))
    rect(s, 1, 17, 14, 3, (86, 70, 50))
    noise(s, [(110, 108, 104), (90, 110, 70)], 14, (2, 2, 12, 14))
    return outline(s)


def cliff(w=48, h=40):
    s = canvas(w, h)
    pts = [(0, h)] + [(x, 6 + int(5 * math.sin(x * 0.5) + rnd.randrange(3))) for x in range(0, w + 1, 4)] + [(w, h)]
    pygame.draw.polygon(s, (104, 84, 62), pts)
    for y in range(h):
        for x in range(w):
            c = s.get_at((x, y))
            if c.a:
                k = (y / h) * 0.5
                shade = (int(104 - 40 * k), int(84 - 34 * k), int(62 - 26 * k))
                if rnd.random() < 0.08:
                    shade = tuple(v + 18 for v in shade)
                s.set_at((x, y), shade)
    for _ in range(7):  # трещины
        x, y = rnd.randrange(4, w - 4), rnd.randrange(10, h - 6)
        for k in range(rnd.randrange(3, 7)):
            px(s, x + k // 2, y + k, (58, 44, 32))
    return outline(s)


def vault_door(label="57"):
    """Скала с круглой дверью-шестернёй и жёлтой рамой (снаружи)."""
    s = cliff(96, 72)
    cx, cy, r = 48, 42, 22
    pygame.draw.circle(s, (40, 36, 34), (cx, cy), r + 4)              # проём
    gear(s, cx, cy, r, label)
    for k in range(-26, 27, 4):                                          # жёлто-чёрная рама
        col = (220, 180, 40) if (k // 4) % 2 == 0 else (30, 28, 26)
        px(s, cx + k, cy - r - 6, col)
        px(s, cx + k + 1, cy - r - 6, col)
    return s


def vault_door_cliff(label="11"):
    """Дверь убежища, врезанная в обрыв плато из набора desert-natural: сверху песок плато, ниже — каменный
    фасад обрыва (те же куски, что у скал вокруг), в фасаде — тёмный проём, жёлто-чёрная рама и шестерня."""
    from src import props as PP
    face = PP.pack_image("pk:desnat/p1/10,14,2,2")              # 96×96: верх — песок, низ — камень
    s = pygame.Surface((192, 144), pygame.SRCALPHA)
    s.blit(face, (0, 48))
    s.blit(face, (96, 48))
    cx, cy, r = 96, 100, 30
    pygame.draw.rect(s, (34, 30, 28), (cx - r - 8, cy - r - 4, 2 * r + 16, r + 40))       # проём в скале
    pygame.draw.circle(s, (34, 30, 28), (cx, cy), r + 8)
    for k in range(-r - 8, r + 9, 6):                                                      # жёлто-чёрная рама
        col = (220, 180, 40) if (k // 6) % 2 == 0 else (30, 28, 26)
        pygame.draw.rect(s, col, (cx + k, cy - r - 10, 6, 4))
    gear(s, cx, cy, r, label)
    pygame.draw.rect(s, (70, 64, 58), (cx - r - 14, 139, 2 * r + 28, 5))                  # порог
    return s


def gear(s, cx, cy, r, label="57"):
    teeth = 10
    for i in range(teeth):
        a = i / teeth * math.tau
        tx, ty = cx + math.cos(a) * r, cy + math.sin(a) * r
        pygame.draw.circle(s, (120, 124, 128), (int(tx), int(ty)), 4)
    pygame.draw.circle(s, (132, 136, 140), (cx, cy), r - 1)
    pygame.draw.circle(s, (160, 164, 168), (cx - 3, cy - 3), r - 7)
    pygame.draw.circle(s, (104, 108, 112), (cx, cy), r - 9)
    pygame.draw.circle(s, (132, 136, 140), (cx, cy), 5)
    font = pygame.font.Font(None, 20)
    t = font.render(label, False, (230, 190, 50))
    s.blit(t, t.get_rect(center=(cx, cy + 1)))


def vault_gear(label="57"):
    s = canvas(64, 64)
    pygame.draw.circle(s, (46, 50, 58), (32, 32), 31)
    gear(s, 32, 32, 22, label)
    return outline(s)


def manhole():
    s = canvas(22, 16)
    pygame.draw.ellipse(s, (58, 58, 62), (0, 0, 22, 16))
    pygame.draw.ellipse(s, (84, 84, 90), (2, 2, 18, 12))
    for x in range(5, 18, 3):
        rect(s, x, 4, 1, 8, (36, 36, 40))
    return outline(s)


def ladder(h=40):
    """Лестница к люку. Свет из люка — не плашка, а конус: ярче всего наверху, к полу и к краям
    сходит на нет (иначе лестница выглядит наклеенной — замечание автора 24.10)."""
    s = canvas(24, h)
    for y in range(h):
        t = y / (h - 1)                         # 0 — у люка, 1 — у пола
        half = 8 + 4 * t                        # конус расширяется книзу
        for x in range(24):
            d = abs(x + 0.5 - 12) / half
            if d < 1:
                a = 70 * (1 - t) ** 1.5 * (1 - d * d)
                if a >= 1:
                    px(s, x, y, (255, 240, 180, int(a)))
    for y in range(h):                          # стойки: внизу темнее — свет до пола не доходит
        k = 1 - 0.25 * y / (h - 1)
        c = tuple(int(v * k) for v in (120, 110, 96))
        rect(s, 6, y, 2, 1, c)
        rect(s, 16, y, 2, 1, c)
    for y in range(3, h, 6):
        k = 1 - 0.25 * y / (h - 1)
        rect(s, 6, y, 12, 2, tuple(int(v * k) for v in (150, 140, 120)))
    for x in range(4, 20):                      # тень у пола, где лестница упирается
        px(s, x, h - 1, (0, 0, 0, 60))
    return s


def board():
    s = canvas(40, 30)
    rect(s, 4, 18, 2, 12, (90, 64, 40))
    rect(s, 34, 18, 2, 12, (90, 64, 40))
    rect(s, 1, 2, 38, 20, (120, 86, 52))
    rect(s, 3, 4, 34, 16, (150, 112, 70))
    for x, y, w, h, c in ((5, 5, 8, 9, (230, 222, 196)), (15, 6, 7, 7, (240, 236, 214)),
                          (24, 5, 10, 8, (214, 204, 170)), (8, 14, 9, 5, (236, 230, 200)),
                          (22, 14, 8, 5, (200, 70, 60))):
        rect(s, x, y, w, h, c)
        for k in range(1, h - 1, 2):
            rect(s, x + 1, y + k, w - 2, 1, (130, 120, 100))
        px(s, x + w // 2, y, (200, 40, 40))
    return outline(s)


def sandbags():
    s = canvas(48, 18)
    for row, y in ((0, 8), (1, 2)):
        for i in range(4 - row):
            x = 2 + i * 11 + row * 6
            pygame.draw.ellipse(s, (170, 150, 110), (x, y, 13, 9))
            pygame.draw.ellipse(s, (196, 178, 136), (x + 2, y + 1, 8, 4))
    noise(s, [(150, 132, 96), (140, 122, 90)], 30)
    return outline(s)


def pipe():
    s = canvas(16, 36)
    rect(s, 4, 0, 8, 36, (120, 72, 40))
    rect(s, 5, 0, 2, 36, (170, 104, 60))
    rect(s, 2, 10, 12, 3, (90, 54, 30))
    rect(s, 2, 26, 12, 3, (90, 54, 30))
    noise(s, [(80, 110, 70), (140, 60, 30)], 12)
    return outline(s)


def puddle():
    s = canvas(34, 16)
    pygame.draw.ellipse(s, (40, 60, 44, 200), (0, 2, 34, 13))
    pygame.draw.ellipse(s, (60, 86, 58, 200), (5, 4, 20, 6))
    px(s, 9, 5, (150, 190, 140))
    px(s, 20, 8, (150, 190, 140))
    return s


def vault_sign(label="57"):
    s = canvas(26, 20)
    rect(s, 1, 1, 24, 16, (40, 70, 140))
    rect(s, 2, 2, 22, 14, (52, 90, 170))
    font = pygame.font.Font(None, 18)
    t = font.render(label, False, (236, 200, 60))
    s.blit(t, t.get_rect(center=(13, 9)))
    rect(s, 12, 17, 2, 3, (80, 80, 84))
    return outline(s)


def barrel_boom():
    s = canvas(16, 22)
    rect(s, 2, 3, 12, 17, (170, 40, 30))
    rect(s, 3, 3, 3, 17, (210, 70, 50))
    for y in (6, 13):
        rect(s, 2, y, 12, 1, (110, 24, 20))
    pygame.draw.ellipse(s, (130, 30, 24), (2, 1, 12, 5))
    rect(s, 6, 8, 4, 4, (240, 200, 40))                 # знак «огнеопасно»
    px(s, 7, 9, (30, 24, 20))
    px(s, 8, 10, (30, 24, 20))
    return outline(s)


DIGITS = {"1": ["010", "110", "010", "010", "111"], "3": ["111", "001", "011", "001", "111"],
          "4": ["101", "101", "111", "001", "001"], "F": ["111", "100", "110", "100", "100"]}


def thermometer():
    """Термометр Бейкера: табло с цифрами наверху, белая колонна со шкалой и красным
    столбиком, бетонное основание. Половинный размер 32×200."""
    s = canvas(32, 200)
    rect(s, 2, 186, 28, 14, (120, 112, 100))           # основание
    rect(s, 2, 186, 28, 3, (150, 142, 128))
    noise(s, [(100, 92, 82), (138, 130, 116)], 30, (2, 189, 28, 11))
    rect(s, 9, 24, 14, 163, (206, 200, 184))           # колонна
    rect(s, 19, 24, 4, 163, (168, 160, 144))           # тень справа
    rect(s, 9, 24, 2, 163, (230, 226, 212))            # блик слева
    for y in range(34, 180, 8):                        # шкала
        rect(s, 9, y, 4 if (y // 8) % 2 else 3, 1, (70, 60, 52))
    rect(s, 15, 64, 3, 116, (176, 36, 28))             # столбик
    rect(s, 15, 64, 1, 116, (214, 70, 52))
    pygame.draw.circle(s, (176, 36, 28), (16, 180), 4)
    for _ in range(14):                                # ржавчина
        x, y = rnd.randint(9, 22), rnd.randint(26, 184)
        rect(s, x, y, rnd.randint(1, 2), rnd.randint(1, 4), (150, 90, 50))
    rect(s, 0, 0, 32, 24, (46, 44, 42))                # табло
    rect(s, 1, 1, 30, 22, (28, 26, 26))
    x = 3
    for ch in "134F":
        for row, line in enumerate(DIGITS[ch]):
            for col, bit in enumerate(line):
                if bit == "1":
                    rect(s, x + col * 2, 4 + row * 3, 2, 2, (238, 128, 44))
        x += 7
    rect(s, 4, 20, 24, 1, (90, 40, 30))
    outline(s)
    return s


def mesa_vault():
    """Столовая гора с дверью Убежища 57 в южном склоне (вид сверху-спереди)."""
    w, h = 336, 176
    s = canvas(w, h)
    top_h = 70                                   # плоская вершина
    # контур: неровная вершина, склон вниз к подножию
    ridge = [(x, 18 + int(10 * math.sin(x * 0.045) + 6 * math.sin(x * 0.13) + rnd.randrange(3))
              + int(max(0, 40 - min(x, w - x)) ** 1.35))                # плечи горы ниже вершины
             for x in range(0, w + 1, 6)]
    foot = [(x, h - 4 - int(4 * math.sin(x * 0.09)) - rnd.randrange(3)) for x in range(w, -1, -6)]
    pygame.draw.polygon(s, (120, 98, 72), ridge + foot)
    for y in range(h):
        for x in range(w):
            if not s.get_at((x, y)).a:
                continue
            if y < top_h + int(8 * math.sin(x * 0.05)):
                c = (134, 112, 82)                                   # вершина — светлее
            else:
                k = (y - top_h) / (h - top_h)
                c = (int(112 - 44 * k), int(90 - 38 * k), int(66 - 28 * k))   # склон темнеет к низу
                if (x + y // 3) % 17 == 0:                            # вертикальные рёбра породы
                    c = tuple(v - 16 for v in c)
            if rnd.random() < 0.06:
                c = tuple(max(0, min(255, v + rnd.choice((-14, 12)))) for v in c)
            s.set_at((x, y), c)
    for _ in range(40):                                               # камни и кусты на вершине
        x, y = rnd.randrange(10, w - 10), rnd.randrange(24, top_h - 6)
        if s.get_at((x, y)).a:
            pygame.draw.circle(s, rnd.choice([(96, 80, 60), (150, 130, 96), (90, 110, 60)]), (x, y), rnd.randrange(2, 4))
    for _ in range(14):                                               # трещины на склоне
        x, y = rnd.randrange(8, w - 8), rnd.randrange(top_h + 6, h - 20)
        for k in range(rnd.randrange(5, 12)):
            px(s, x + (k // 3) * rnd.choice((-1, 1)), y + k, (54, 42, 30))
    # проём и дверь-шестерня внизу посередине
    cx, cy, r = w // 2, h - 34, 26
    pygame.draw.rect(s, (60, 54, 48), (cx - r - 10, cy - r - 8, 2 * r + 20, 2 * r + 28))
    pygame.draw.circle(s, (34, 30, 28), (cx, cy), r + 5)
    gear(s, cx, cy, r)
    for k in range(-r - 10, r + 11, 4):                                # жёлто-чёрная рама
        col = (220, 180, 40) if (k // 4) % 2 == 0 else (30, 28, 26)
        pygame.draw.rect(s, col, (cx + k, cy - r - 10, 4, 3))
    pygame.draw.rect(s, (84, 80, 76), (cx - r - 12, h - 8, 2 * r + 24, 6))   # порог
    return outline(s)


def rocket():
    """Ракета REPCONN «Гелиос» на стартовом столе: белый корпус с красными кольцами, стабилизаторы,
    кабина-иллюминатор, ферма обслуживания сбоку. Половинный размер 48×176."""
    w, h = 48, 176
    s = canvas(w, h)
    cx = 22
    rect(s, cx - 9, 34, 18, 120, (226, 226, 220))                       # корпус
    rect(s, cx - 9, 34, 4, 120, (190, 192, 190))                        # тень на корпусе
    for y in (60, 96, 132):
        rect(s, cx - 9, y, 18, 4, (196, 54, 46))                       # красные кольца
    for k in range(18):                                                  # обтекатель
        rect(s, cx - 9 + k // 2, 34 - k, 18 - k, 1, (226, 226, 220) if k < 14 else (196, 54, 46))
    pygame.draw.circle(s, (60, 110, 160), (cx, 46), 4)                  # иллюминатор
    pygame.draw.circle(s, (150, 200, 240), (cx - 1, 45), 2)
    for side in (-1, 1):                                                 # стабилизаторы
        pts = [(cx + side * 9, 128), (cx + side * 17, 150), (cx + side * 17, 158), (cx + side * 9, 150)]
        pygame.draw.polygon(s, (196, 54, 46), pts)
    rect(s, cx - 6, 154, 12, 6, (70, 70, 74))                          # сопло
    rect(s, 2, 160, w - 4, 14, (120, 118, 112))                        # стартовый стол
    rect(s, 2, 160, w - 4, 3, (150, 148, 140))
    for y in range(40, 160, 8):                                          # ферма обслуживания
        rect(s, w - 8, y, 6, 1, (90, 88, 84))
        px(s, w - 8 + (y // 8) % 6, y + 4, (90, 88, 84))
    rect(s, w - 8, 40, 1, 120, (90, 88, 84))
    rect(s, w - 3, 40, 1, 120, (90, 88, 84))
    return outline(s)


def police_box():
    """Синяя полицейская будка посреди пустыни. Внутри, говорят, больше, чем снаружи."""
    w, h = 44, 92
    s = canvas(w, h)
    blue, dark, lite = (36, 66, 128), (24, 44, 92), (64, 98, 168)
    rect(s, 4, 14, 36, 76, blue)
    rect(s, 4, 14, 4, 76, dark)
    rect(s, 2, 8, 40, 8, blue)                                          # карниз
    rect(s, 6, 9, 32, 5, (20, 22, 26))                                  # табличка
    for x in range(9, 36, 4):
        rect(s, x, 11, 2, 1, (230, 230, 230))
    rect(s, 18, 2, 8, 7, (230, 228, 200))                               # фонарь
    rect(s, 20, 0, 4, 3, dark)
    for row in range(3):                                                 # окошки
        for col in range(2):
            rect(s, 10 + col * 13, 20 + row * 22, 11, 16, dark)
            if row == 0:
                for i in range(2):
                    for j in range(2):
                        rect(s, 11 + col * 13 + i * 5, 21 + j * 7, 4, 6, (220, 226, 236))
            else:
                rect(s, 11 + col * 13, 21 + row * 22, 9, 14, lite)
    rect(s, 21, 20, 2, 66, dark)                                         # створки
    rect(s, 3, 88, 38, 4, (90, 84, 70))                                  # песок у основания
    return outline(s)


def saucer():
    """Летающая тарелка, зарывшаяся краем в песок: серебристый диск, купол, мигающие огоньки."""
    w, h = 120, 60
    s = canvas(w, h)
    pygame.draw.ellipse(s, (150, 130, 100), (0, 38, w, 22))             # воронка
    pygame.draw.ellipse(s, (110, 94, 70), (8, 42, w - 16, 14))
    hull = [(6, 34), (60, 18), (114, 26), (108, 40), (52, 50), (10, 44)]
    pygame.draw.polygon(s, (176, 182, 190), hull)
    pygame.draw.polygon(s, (130, 136, 146), [(10, 44), (52, 50), (108, 40), (110, 36), (52, 44), (10, 38)])
    pygame.draw.ellipse(s, (120, 200, 210), (44, 6, 34, 22))            # купол
    pygame.draw.ellipse(s, (190, 240, 245), (50, 9, 12, 7))
    for i, x in enumerate((20, 38, 56, 74, 92)):                          # огоньки
        pygame.draw.circle(s, (120, 255, 120) if i % 2 else (255, 90, 80), (x, 36 + (x - 60) // 12), 2)
    pygame.draw.line(s, (60, 60, 64), (84, 26), (100, 12), 2)           # обломанная антенна
    return outline(s)


def whale():
    """Кашалот, упавший с неба. Удивлённый. Очень удивлённый."""
    w, h = 150, 64
    s = canvas(w, h)
    body = (96, 104, 118)
    pygame.draw.ellipse(s, (140, 120, 92), (0, 48, w, 16))              # вмятина в песке
    pygame.draw.ellipse(s, body, (6, 14, 112, 44))                       # туловище
    rect(s, 10, 22, 50, 30, body)                                        # тупая голова кашалота
    pygame.draw.ellipse(s, (150, 156, 166), (14, 40, 96, 16))            # светлое брюхо
    pygame.draw.polygon(s, body, [(112, 30), (146, 14), (140, 30), (148, 46), (112, 42)])   # хвост
    pygame.draw.circle(s, (20, 20, 24), (24, 30), 3)                     # глаз — удивлённый
    pygame.draw.circle(s, (240, 240, 240), (23, 29), 1)
    pygame.draw.line(s, (60, 64, 74), (12, 44), (40, 46), 2)             # рот
    return outline(s)


def petunia():
    """Горшок с петунией. «О нет, только не снова»."""
    w, h = 22, 26
    s = canvas(w, h)
    pygame.draw.polygon(s, (176, 92, 56), [(4, 14), (18, 14), (16, 25), (6, 25)])
    rect(s, 3, 12, 16, 3, (196, 108, 66))
    for x, y, c in ((7, 8, (210, 80, 170)), (12, 5, (230, 110, 190)), (15, 9, (200, 70, 160))):
        pygame.draw.circle(s, c, (x, y), 3)
        px(s, x, y, (250, 230, 120))
    rect(s, 10, 9, 1, 4, (70, 130, 60))
    return outline(s)


def planks():
    """Дощатый настил моста через каньон (лежит на земле, по нему ходят)."""
    w, h = 48, 48
    s = canvas(w, h)
    for i, y in enumerate(range(2, 46, 7)):
        c = (128, 92, 58) if i % 2 else (146, 106, 66)
        rect(s, 0, y, w, 6, c)
        rect(s, 0, y + 5, w, 1, (90, 62, 38))
        px(s, 6 + (i * 13) % 34, y + 2, (70, 50, 30))
    rect(s, 3, 0, 2, h, (96, 70, 44))                                   # верёвочные перила-бревна
    rect(s, w - 5, 0, 2, h, (96, 70, 44))
    return s


# ------------------------------------------------ Пятнадцатая: что не нашлось в наборах
# Сначала искали готовое в бандле SCKR (483 набора, сводки _catalog/*.png). Всё, что нашлось,
# взято оттуда — таблица REPLACED, своих картинок у этих предметов больше нет (docs/furnish/fifteen.md §2.2).
# Здесь рисуем только то, чего в наборах нет.
#
# Рисуем в полном размере (1 px = 1 px картинки), как предметы наборов: контур в 1 px с полупрозрачной
# кромкой (soft_outline), десятки оттенков, блики и тени по граням, дизеринг на переходах.
# Прежние версии рисовались вдвое мельче и растягивались вдвое — отсюда и был пиксель вчетверо крупнее.

WOOD_D, WOOD, WOOD_L = (86, 60, 36), (120, 86, 52), (150, 112, 70)
METAL_D, METAL, METAL_L = (78, 82, 86), (120, 124, 128), (162, 166, 170)
BRASS, BRASS_L = (170, 134, 62), (212, 178, 96)
PAPER, PAPER_D = (232, 226, 204), (176, 168, 142)
SHADOW = (66, 52, 38)

# было -> (картинка из набора, поля для P(...) на шаге 4.2)
REPLACED = {
    "x_piano": ("pk:west/west_2_012", {"foot": [2, 1]}),
    "x_screen": ("pk:west/west_2_016", {"foot": [2, 1], "sight": True}),
    "x_garden": ("pk:wfarm/wfarm_5_057", {"foot": [2, 1]}),
    "x_scales": ("pk:bazaar/bazaar_1_022", {"foot": [2, 1]}),
    "x_radio": ("pk:jtown/jtown_5_019", {"foot": [1, 1]}),
    "x_portrait": ("pk:west/west_8_018", {"foot": [1, 1], "block": False}),
    "x_clock": ("pk:west/west_2_011", {"foot": [1, 1], "block": False}),
    "x_carpet": ("pk:bazaar/bazaar_1_089", {"foot": [2, 1], "block": False, "layer": "floor"}),
    "x_register": ("pk:town50/town50_2_104", {"foot": [1, 1], "scale": 0.4, "search": "drawer", "title": "касса"}),   # в наборе огромная — с продавца ростом
    "x_fireext": ("pk:fstation/fstation_1_047", {"foot": [1, 1]}),
    "x_cart": ("pk:bazaar/bazaar_1_023", {"foot": [2, 1], "search": "junk", "title": "тележка"}),
    "x_cauldron": ("pk:west/west_5_031", {"foot": [1, 1], "search": "junk", "title": "котелок",
                                          "light": {"r": 110, "color": [255, 150, 70], "at": [0.5, 0.85],
                                                    "flicker": 1}}),
    # не верёвка, а моток проволоки (решение автора): место — гараж и свалка, не спортзал
    "x_wire_coil": ("pk:west/west_4_076", {"foot": [1, 1], "block": False, "layer": "floor", "scale": 0.75,
                                           "title": "моток проволоки", "search": "junk"}),
    "x_safe": ("pk:west/west_3_132", {"foot": [1, 1], "search": "military", "title": "сейф"}),
    "x_microscope": ("pk:wschool/wschool_3_038", {"foot": [1, 1]}),
    "x_easel": ("pk:aoffice/aoffice_3_037", {"foot": [1, 1]}),
    "x_curtain": ("pk:lhotel/lhotel_5_035", {"foot": [2, 1], "sight": True}),
}


def soft_outline(s, color=INK):
    """Контур в 1 px и полупрозрачная кромка снаружи — так выглядят вырезанные предметы наборов."""
    w, h = s.get_size()
    solid = {(x, y) for y in range(h) for x in range(w) if s.get_at((x, y)).a > 96}
    ring = set()
    for x, y in solid:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in solid:
                ring.add((nx, ny))
    for p in ring:
        s.set_at(p, color)
    for x, y in list(ring):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in solid and (nx, ny) not in ring:
                s.set_at((nx, ny), (color[0], color[1], color[2], 96))
    return s


def dither(s, x, y, w, h, c1, c2, step=2):
    """Шахматка двух оттенков — переход вместо плашки."""
    for py in range(y, y + h):
        for px_ in range(x, x + w):
            if (px_ + py) % step == 0:
                px(s, px_, py, c2)
            elif (px_ + py) % step == 1:
                px(s, px_, py, c1)


def _shadow(s, x, y, w, h):
    pygame.draw.ellipse(s, SHADOW, (x, y, w, h))


def _star(s, cx, cy, r, color, inner=0.45):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(s, color, pts)


# ------------------------------------------------------------ флаги (в наборах флагов на древке нет)
def _flag(cloth, emblem, star=True):
    s = canvas(40, 52)
    _shadow(s, 3, 45, 10, 4)
    # древко: волокна, блик слева, тень справа
    rect(s, 4, 6, 4, 44, WOOD)
    rect(s, 4, 6, 1, 44, (156, 118, 74))
    rect(s, 7, 6, 1, 44, (72, 48, 30))
    for y in range(9, 47, 4):
        px(s, 5, y, (102, 72, 44))
        px(s, 6, y + 2, (134, 98, 60))
    px(s, 6, 22, (86, 60, 38))
    px(s, 5, 34, (86, 60, 38))
    pygame.draw.circle(s, (146, 112, 52), (6, 4), 2)              # навершие
    pygame.draw.circle(s, (206, 172, 92), (6, 4), 1)
    px(s, 5, 3, (238, 214, 150))
    # полотнище: полосы с волной, складки через одну
    for i in range(10):
        x = 8 + i * 3
        top = 7 + (1 if i % 3 == 0 else 0)
        bot = 38 + (1 if i % 4 == 1 else 0) - (1 if i % 5 == 3 else 0)
        k = (0, 4, -10, -14, 8, 6, -6, -12, 10, 2)[i]
        c = tuple(max(0, min(255, v + k)) for v in cloth)
        rect(s, x, top, 3, bot - top, c)
        if i in (2, 6):                                            # глубокая складка
            rect(s, x + 1, top + 1, 1, bot - top - 2, tuple(max(0, v - 26) for v in c))
        if i in (4, 8):                                            # гребень складки
            rect(s, x, top + 1, 1, bot - top - 2, tuple(min(255, v + 26) for v in c))
    rect(s, 8, 6, 32, 2, tuple(min(255, v + 14) for v in cloth))   # верхняя кромка
    # герб
    if star:
        _star(s, 23, 18, 8, tuple(max(0, v - 40) for v in emblem), 0.5)
        _star(s, 23, 18, 7, emblem, 0.45)
        px(s, 23, 15, (250, 232, 168))
    else:                                                          # герб Vault-Tec: шестерня-дверь
        pygame.draw.circle(s, (32, 34, 44), (23, 18), 9)
        pygame.draw.circle(s, emblem, (23, 18), 8)
        for i in range(8):
            a = i * math.pi / 4
            x0, y0 = 23 + math.cos(a) * 3, 18 + math.sin(a) * 3
            x1, y1 = 23 + math.cos(a) * 7, 18 + math.sin(a) * 7
            pygame.draw.line(s, (78, 74, 62), (x0, y0), (x1, y1), 1)
        pygame.draw.circle(s, (52, 50, 44), (23, 18), 3)
        pygame.draw.circle(s, (120, 132, 158), (23, 18), 2)
    # тень полотнища на древке
    rect(s, 8, 8, 1, 27, (54, 36, 24))
    return soft_outline(s)


def flag():
    """Флаг города на древке — ратуша."""
    return _flag((136, 52, 42), (228, 198, 96), star=True)


def flag_vt():
    """Флаг Vault-Tec: синее полотнище, шестерня-дверь убежища."""
    return _flag((58, 82, 138), (214, 176, 92), star=False)


# ------------------------------------------------------------ табличка «НЕТ БЕНЗИНА»
def sign_fuel():
    """Щит на двух столбах у навеса заправки. Надпись — DejaVuSans-Bold без сглаживания."""
    s = canvas(120, 76)
    for x in (18, 96):
        _shadow(s, x - 3, 70, 14, 5)
        rect(s, x, 32, 8, 40, (112, 78, 46))
        rect(s, x, 32, 1, 40, (150, 112, 70))
        rect(s, x + 7, 32, 1, 40, (74, 50, 32))
        for y in range(36, 70, 5):
            px(s, x + 2, y, (94, 66, 40))
            px(s, x + 5, y + 2, (134, 98, 60))
        pygame.draw.circle(s, (56, 54, 52), (x + 4, 38), 1)        # гвоздь
        pygame.draw.circle(s, (56, 54, 52), (x + 4, 62), 1)
    # щит: жесть с потёками ржавчины
    rect(s, 2, 2, 116, 40, (228, 220, 198))
    dither(s, 6, 6, 108, 32, (228, 220, 198), (218, 210, 188), 2)
    rect(s, 2, 2, 116, 2, (244, 238, 218))
    rect(s, 2, 40, 116, 2, (188, 176, 150))
    pygame.draw.rect(s, (138, 50, 40), (2, 2, 116, 40), 1)
    pygame.draw.rect(s, (176, 82, 62), (4, 4, 112, 36), 1)
    for x0, y0, w0, h0 in ((92, 6, 3, 12), (96, 20, 2, 9), (10, 26, 3, 10), (104, 30, 3, 6)):
        rect(s, x0, y0, w0, h0, (146, 92, 58))                     # ржавые потёки
        px(s, x0 + 1, y0 + h0, (116, 70, 44))
    pygame.draw.circle(s, (92, 84, 72), (100, 36), 3)              # пулевая пробоина в углу
    pygame.draw.circle(s, (44, 40, 36), (100, 36), 2)
    px(s, 101, 35, (30, 28, 26))
    pygame.draw.line(s, (172, 160, 134), (6, 6), (12, 12), 1)      # царапины у края
    pygame.draw.line(s, (172, 160, 134), (110, 8), (114, 14), 1)
    for x, y in ((5, 5), (114, 5), (5, 38), (114, 38)):            # заклёпки
        pygame.draw.circle(s, (112, 106, 96), (x, y), 1)
        px(s, x, y - 1, (168, 162, 150))
    font = pygame.font.Font(os.path.join(ROOT, "assets", "fonts", "DejaVuSans-Bold.ttf"), 16)
    for size, line, cy in ((13, "НЕТ БЕНЗИНА", 14), (9, "ПРИВОЗ В ПЯТНИЦУ", 26)):
        font = pygame.font.Font(os.path.join(ROOT, "assets", "fonts", "DejaVuSans-Bold.ttf"), size)
        t = font.render(line, False, (156, 42, 32))
        r = t.get_rect(center=(60, cy))
        s.blit(t, (r.x, r.y))
    return soft_outline(s)


# ------------------------------------------------------------ сортир-кабинка
def outhouse():
    """Кабинка во дворе: доски в четверть, дранка внахлёст, месяц в двери, трава у порога."""
    s = canvas(56, 72)
    _shadow(s, 4, 64, 48, 8)
    tones = [(122, 88, 54), (132, 96, 60), (114, 82, 50), (126, 92, 56)]
    for i, x in enumerate(range(7, 49, 5)):
        rect(s, x, 17, 5, 51, tones[i % 4])
        rect(s, x, 17, 1, 51, (92, 64, 40))
        rect(s, x + 1, 17, 1, 51, (146, 108, 70))
        px(s, x + 3, 26, (74, 52, 32))
        px(s, x + 3, 48, (74, 52, 32))
    rect(s, 6, 17, 1, 51, (158, 118, 76))
    rect(s, 50, 17, 1, 51, (72, 48, 30))
    rect(s, 6, 17, 45, 3, (54, 40, 28))                          # тень под свесом
    # крыша: два ската, дранка рядами внахлёст
    pygame.draw.polygon(s, (66, 46, 30), [(0, 19), (28, 1), (56, 19)])
    for row, y in enumerate(range(4, 19, 3)):
        half = int((y - 1) * 1.5)
        for x in range(28 - half, 28 + half, 4):
            off = 2 if row % 2 else 0
            col = (106, 76, 46) if (x // 4 + row) % 3 else (88, 62, 38)
            rect(s, x + off, y, 3, 3, col)
            px(s, x + off, y, (132, 98, 62))
            px(s, x + off + 2, y + 2, (58, 42, 28))
    pygame.draw.line(s, (54, 38, 26), (0, 19), (28, 1), 1)        # конёк
    pygame.draw.line(s, (54, 38, 26), (28, 1), (56, 19), 1)
    rect(s, 25, 0, 6, 3, (86, 62, 38))
    rect(s, 25, 0, 6, 1, (118, 86, 54))
    pygame.draw.line(s, (46, 34, 24), (0, 19), (56, 19), 1)       # свес крыши
    # дверь: рама, доски, петли
    rect(s, 13, 21, 30, 48, (146, 108, 70))                       # наличник
    rect(s, 13, 21, 30, 1, (172, 132, 88))
    rect(s, 13, 68, 30, 1, (96, 68, 44))
    rect(s, 15, 23, 26, 44, (124, 90, 56))                        # полотно
    for x in (20, 25, 30, 35):
        rect(s, x, 23, 1, 44, (106, 76, 46))
        px(s, x + 1, 24, (140, 102, 64))
    rect(s, 15, 23, 26, 1, (152, 114, 74))
    # месяц-прорезь: тёмный кружок, из него вырезан светлый — серп открыт вправо
    pygame.draw.circle(s, (36, 28, 22), (26, 31), 7)
    pygame.draw.circle(s, (124, 90, 56), (23, 29), 7)
    # вентиляционные щели у пола
    for y in (54, 57):
        rect(s, 19, y, 16, 1, (88, 62, 40))
        rect(s, 19, y + 1, 16, 1, (142, 104, 66))
    # петли, щеколда
    for y in (27, 58):
        rect(s, 13, y, 8, 2, METAL_D)
        px(s, 14, y, METAL)
        px(s, 19, y, METAL_L)
    rect(s, 36, 46, 5, 2, METAL_D)
    px(s, 40, 46, METAL_L)
    # порог и трава
    rect(s, 11, 67, 34, 4, (98, 70, 46))
    rect(s, 11, 67, 34, 1, (138, 100, 64))
    rect(s, 11, 70, 34, 1, (74, 52, 32))
    for x, y in ((6, 65), (8, 68), (48, 64), (50, 67), (44, 69), (3, 68)):
        px(s, x, y, (92, 116, 62))
        px(s, x + 1, y - 1, (118, 142, 80))
        px(s, x, y - 2, (104, 128, 70))
    noise(s, [(104, 74, 48), (140, 102, 64), (92, 66, 42)], 34, (7, 20, 43, 45))
    return soft_outline(s)


# ------------------------------------------------------------ спортзал
def wallbars():
    """Шведская стенка у стены спортзала: две стойки, десять перекладин, крепления."""
    s = canvas(40, 80)
    for x0 in (3, 33):
        rect(s, x0, 2, 4, 78, (150, 112, 70))
        rect(s, x0, 2, 1, 78, (178, 138, 90))
        rect(s, x0 + 3, 2, 1, 78, (102, 72, 44))
        for y in range(6, 78, 7):
            px(s, x0 + 2, y + 2, (120, 86, 52))
    for y in range(8, 78, 7):                                      # перекладины
        rect(s, 3, y, 34, 3, (166, 126, 80))
        rect(s, 3, y, 34, 1, (198, 158, 102))
        rect(s, 3, y + 2, 34, 1, (116, 82, 48))
        px(s, 8, y + 3, (96, 68, 40))                              # тень от перекладины
        px(s, 20, y + 3, (96, 68, 40))
        px(s, 32, y + 3, (96, 68, 40))
    for y in (4, 40, 76):                                          # крепления к стене
        rect(s, 0, y, 3, 4, METAL_D)
        rect(s, 37, y, 3, 4, METAL_D)
        px(s, 1, y + 1, METAL)
        px(s, 38, y + 1, METAL)
    noise(s, [(136, 100, 62), (108, 78, 46)], 40, (3, 2, 34, 78))
    return soft_outline(s)


def climb_rope():
    """Канат с крюка в спортзале: витая верёвка в пять пикселей, узел с двумя хвостами."""
    s = canvas(24, 80)
    rect(s, 7, 0, 10, 3, METAL_D)                                 # пластина на потолке
    rect(s, 7, 0, 10, 1, METAL_L)
    px(s, 9, 1, (56, 58, 60))
    px(s, 15, 1, (56, 58, 60))
    pygame.draw.circle(s, METAL, (12, 5), 3, 1)
    px(s, 11, 4, METAL_L)
    for y in range(8, 66):
        i = y - 8
        x = 9 + (1 if (i // 4) % 2 else 0)
        rect(s, x, y, 5, 1, (124, 96, 60))                        # тело каната
        k = i % 4                                                # косая прядь, шаг 4 px
        px(s, x + k, y, (180, 148, 98))
        px(s, x + (k + 1) % 5, y, (162, 130, 84))
        px(s, x + (k + 3) % 5, y, (96, 72, 44))
        if i % 7 == 0:
            px(s, x + 2, y, (196, 164, 110))
    pygame.draw.ellipse(s, (142, 112, 70), (5, 63, 14, 10))       # узел
    pygame.draw.ellipse(s, (172, 140, 90), (6, 64, 12, 6))
    pygame.draw.line(s, (110, 84, 52), (6, 70), (18, 68), 1)
    px(s, 8, 66, (198, 166, 112))
    rect(s, 9, 72, 2, 7, (132, 104, 66))                          # хвосты
    rect(s, 13, 71, 2, 8, (150, 120, 78))
    px(s, 10, 78, (108, 84, 52))
    px(s, 14, 78, (122, 96, 60))
    px(s, 12, 73, (176, 144, 96))
    return soft_outline(s)


# ------------------------------------------------------------ класс
def globe():
    """Глобус у стола учителя: латунный меридиан, шар с материками, деревянная стойка."""
    s = canvas(40, 48)
    _shadow(s, 8, 40, 24, 6)
    rect(s, 9, 38, 22, 5, WOOD)                                    # основание
    rect(s, 9, 38, 22, 1, (168, 128, 82))
    rect(s, 9, 42, 22, 1, (74, 50, 32))
    rect(s, 18, 30, 4, 8, BRASS)                                   # стойка
    rect(s, 18, 30, 1, 8, BRASS_L)
    pygame.draw.circle(s, BRASS, (20, 20), 15, 1)                  # меридиан
    pygame.draw.circle(s, BRASS_L, (20, 20), 13, 0)                # латунная подложка
    pygame.draw.circle(s, (48, 84, 124), (20, 20), 12)              # океан
    dither(s, 9, 9, 22, 22, (48, 84, 124), (56, 94, 136), 2)
    pygame.draw.circle(s, (40, 72, 108), (20, 20), 12, 1)
    for pts in ([(12, 13), (17, 11), (20, 14), (18, 19), (13, 20), (11, 16)],       # материк
                [(24, 12), (30, 14), (31, 19), (26, 21), (23, 17)],
                [(17, 24), (22, 23), (24, 27), (19, 29)]):
        pygame.draw.polygon(s, (104, 146, 84), pts)
        pygame.draw.polygon(s, (128, 166, 96), pts[:3])
    for x, y in ((11, 21), (27, 24), (29, 10)):                    # мелкие острова
        px(s, x, y, (110, 150, 88))
    rect(s, 14, 12, 3, 1, (188, 214, 236))                          # блик
    px(s, 13, 13, (206, 226, 244))
    pygame.draw.arc(s, (86, 62, 38), pygame.Rect(4, 16, 8, 8), math.pi * 0.5, math.pi * 1.5, 1)  # рожки оси
    pygame.draw.arc(s, (86, 62, 38), pygame.Rect(28, 16, 8, 8), -math.pi * 0.5, math.pi * 0.5, 1)
    px(s, 6, 19, BRASS_L)
    px(s, 33, 19, BRASS_L)
    return soft_outline(s)


def kids_drawings():
    """Детский рисунок на стене класса: лист со скотчем, солнце, дом, две фигурки; второй — позади."""
    s = canvas(44, 40)
    rect(s, 26, 4, 15, 18, (222, 214, 190))                         # второй лист
    pygame.draw.rect(s, (196, 186, 160), (26, 4, 15, 18), 1)
    pygame.draw.circle(s, (226, 182, 58), (34, 11), 3)              # солнце
    for dx, dy in ((0, -5), (5, 0), (0, 5), (-5, 0), (4, -4), (-4, 4)):
        px(s, 34 + dx, 11 + dy, (230, 190, 70))
    rect(s, 28, 16, 11, 4, (110, 150, 90))                          # трава
    px(s, 31, 18, (188, 72, 60)); px(s, 35, 17, (188, 72, 60))      # цветы
    # основной лист
    rect(s, 3, 3, 32, 33, PAPER)
    rect(s, 3, 3, 32, 1, (246, 240, 220))
    rect(s, 3, 35, 32, 1, (198, 190, 164))
    pygame.draw.rect(s, (188, 178, 152), (3, 3, 32, 33), 1)
    rect(s, 5, 5, 28, 12, (206, 220, 232))                          # небо
    dither(s, 5, 5, 28, 12, (206, 220, 232), (216, 228, 238), 2)
    pygame.draw.circle(s, (232, 186, 52), (11, 11), 4)              # солнце с лучами
    for i in range(8):
        a = i * math.pi / 4
        px(s, 11 + math.cos(a) * 6, 11 + math.sin(a) * 6, (230, 190, 64))
    rect(s, 18, 8, 3, 1, (86, 88, 96))                              # облако
    rect(s, 20, 7, 3, 1, (96, 98, 106))
    # дом
    rect(s, 22, 15, 10, 9, (196, 88, 64))
    pygame.draw.polygon(s, (132, 84, 58), [(21, 15), (27, 10), (33, 15)])
    rect(s, 25, 19, 4, 5, (92, 70, 52))
    rect(s, 29, 16, 2, 2, (238, 220, 140))                          # окно
    px(s, 27, 8, (200, 200, 190))                                    # дым
    px(s, 28, 7, (210, 210, 200))
    # фигурки и трава
    for x, c in ((9, (60, 70, 140)), (15, (70, 130, 80))):
        pygame.draw.circle(s, c, (x, 23), 2)
        rect(s, x - 1, 25, 3, 4, c)
        pygame.draw.line(s, c, (x - 2, 26), (x + 2, 26), 1)
        pygame.draw.line(s, c, (x - 1, 29), (x - 2, 32), 1)
        pygame.draw.line(s, c, (x + 1, 29), (x + 2, 32), 1)
    pygame.draw.line(s, (110, 150, 88), (6, 32), (32, 32), 1)
    for x in range(7, 31, 3):
        px(s, x, 31, (128, 168, 96))
    rect(s, 4, 4, 5, 2, (222, 218, 208))                            # скотч
    px(s, 4, 3, (198, 194, 184))
    rect(s, 30, 33, 4, 2, (210, 206, 196))                          # отогнутый угол
    return soft_outline(s, (78, 70, 60))


def jail_cell():
    """Камера за решёткой для участка шерифа: уличный спрайт west_7_020 без кактуса и перекати-поля
    на крыше (верхние 56 px) — внутри здания на камере ничего не растёт."""
    img = pygame.image.load(os.path.join("assets", "packs", "west", "props", "west_7_020.png")).convert_alpha()
    w, h = img.get_size()
    return img.subsurface((0, 56, w, h - 56)).copy()


def _mark_full(*fns):
    for f in fns:
        f.full_size = True
    return fns


_mark_full(flag, flag_vt, sign_fuel, outhouse, wallbars, climb_rope, globe, kids_drawings, jail_cell)

# имя -> (рисунок, описание в каталоге)
PROPS = {
    "x_grave": (grave, {"foot": [1, 1], "search": "grave", "title": "могила"}),
    "x_cross": (cross, {"foot": [1, 1]}),
    "x_tombstone": (tombstone, {"foot": [1, 1]}),
    "x_vault_door": (vault_door, {"foot": [4, 2], "sight": True}),
    "x_vault_gear": (vault_gear, {"foot": [2, 1], "sight": True}),
    "x_vault_gear12": (lambda: vault_gear("12"), {"foot": [2, 1], "sight": True}),   # Убежище 12 (Некрополь)
    "x_manhole": (manhole, {"block": False, "layer": "floor"}),
    "x_ladder": (ladder, {"block": False, "layer": "floor"}),
    "x_ladder_wall": (lambda: ladder(64), {"block": False, "layer": "floor"}),   # во всю стену подвала, до люка
    "x_board": (board, {"foot": [2, 1]}),
    "x_sandbags": (sandbags, {"foot": [2, 1]}),
    "x_cliff": (cliff, {"foot": [2, 1], "sight": True}),
    "x_pipe": (pipe, {"foot": [1, 1]}),
    "x_puddle": (puddle, {"block": False, "layer": "floor"}),
    "x_vault_sign": (vault_sign, {"foot": [1, 1]}),
    "x_mesa_vault": (mesa_vault, {"foot": [14, 3], "sight": True}),
    "x_barrel_boom": (barrel_boom, {"foot": [1, 1], "explosive": True}),
    "x_thermometer": (thermometer, {"foot": [2, 1], "sight": True}),
    # новые — только в конец: рисунки берут случайность из общего генератора, порядок не менять
    "x_rocket": (rocket, {"foot": [2, 1], "sight": True}),
    # Убежища 15 и 4: дверь снаружи (в скале), шестерня изнутри, табличка
    **{f"x_vault_door{n}": (lambda n=n: vault_door_cliff(n), {"foot": [4, 2], "sight": True}) for n in ("15", "4", "22")},
    "x_vault_door0": (lambda: vault_door("0"), {"foot": [4, 2], "sight": True}),
    **{f"x_vault_gear{n}": (lambda n=n: vault_gear(n), {"foot": [2, 1], "sight": True}) for n in ("15", "4", "22", "0")},
    **{f"x_vault_sign{n}": (lambda n=n: vault_sign(n), {"foot": [1, 1]}) for n in ("15", "4", "22", "0")},
    # особые встречи в пустоши (src/encounters.py)
    "x_police_box": (police_box, {"foot": [1, 1], "sight": True, "search": "junk", "title": "синяя будка"}),
    "x_saucer": (saucer, {"foot": [4, 1], "sight": True, "scale": 1.5}),
    "x_whale": (whale, {"foot": [5, 1], "sight": True, "scale": 1.7}),
    "x_petunia": (petunia, {"foot": [1, 1], "search": "junk", "title": "горшок с петунией"}),
    "x_planks": (planks, {"block": False, "layer": "floor"}),
    # Убежище 11 (жребий): дверь в скале, шестерня изнутри, табличка
    "x_vault_door11": (lambda: vault_door_cliff("11"), {"foot": [4, 2], "sight": True}),
    "x_vault_gear11": (lambda: vault_gear("11"), {"foot": [2, 1], "sight": True}),
    "x_vault_sign11": (lambda: vault_sign("11"), {"foot": [1, 1]}),
    # Пятнадцатая, шаг 4 (docs/furnish/fifteen.md §2.2): своих картинок осталось восемь — того,
    # чего в бандле SCKR нет. Остальные 17 предметов берутся из наборов (REPLACED выше).
    "x_jail_cell": (jail_cell, {"foot": [2, 1], "sight": True, "title": "камера"}),   # участок шерифа
    "x_flag": (flag, {"foot": [1, 1]}),                                    # флаг ратуши
    "x_flag_vt": (flag_vt, {"foot": [1, 1]}),                               # флаг Vault-Tec
    "x_sign_fuel": (sign_fuel, {"foot": [2, 1]}),                           # «НЕТ БЕНЗИНА»
    "x_outhouse": (outhouse, {"foot": [1, 1], "sight": True, "search": "junk", "title": "сортир"}),
    "x_wallbars": (wallbars, {"foot": [1, 1]}),                             # шведская стенка
    "x_climb_rope": (climb_rope, {"foot": [1, 1], "block": False}),          # канат в спортзале
    "x_globe": (globe, {"foot": [1, 1]}),                                   # глобус у стола учителя
    "x_kids_drawings": (kids_drawings, {"foot": [1, 1]}),                   # детский рисунок на стене
}


# объекты набора «War ruins»: имя -> (картинка, масштаб, пятно [ширина, глубина], доп. поля)
B, V, S = 1.5, 1.25, 1.2   # масштаб: постройки, машины, мелочь (герой в игре — 74 px)
RUINS = {
    # лачуги, хижины, палатки
    "r_shack": ("r21_034", B, [4, 2], {"sight": True}), "r_shack_ruin": ("r21_035", B, [5, 2], {"sight": True}),
    "r_shack_tin": ("r21_037", B, [5, 2], {"sight": True}), "r_house_wood": ("r22_018", B, [3, 2], {"sight": True}),
    "r_shed_tin": ("r22_024", B, [3, 2], {"sight": True}), "r_shed_tin_b": ("r22_025", B, [3, 2], {"sight": True}),
    "r_cabin": ("r22_041", B, [2, 2], {"sight": True}), "r_cabin_b": ("r22_055", B, [2, 2], {"sight": True}),
    "r_cabin_c": ("r27_023", B, [2, 2], {"sight": True}), "r_cabin_d": ("r27_024", B, [3, 2], {"sight": True}),
    "r_shack_e": ("r27_029", B, [2, 2], {"sight": True}), "r_shack_blue": ("r27_008", B, [2, 1], {"sight": True}),
    "r_shack_f": ("r27_007", B, [3, 2], {"sight": True}), "r_shack_g": ("r27_021", B, [3, 1], {"sight": True}),
    "r_shanty": ("r27_030", B, [3, 2], {"sight": True}), "r_shanty_big": ("r27_026", B, [5, 3], {"sight": True}),
    "r_hut": ("r22_069", B, [3, 2], {"sight": True}),
    "r_tent_big": ("r21_038", S, [4, 1], {"sight": True}), "r_tent_yellow": ("r22_034", S, [2, 1], {}),
    "r_tent_beige": ("r22_053", S, [2, 1], {}), "r_tent_purple": ("r22_054", S, [2, 1], {}),
    "r_tent_green": ("r22_067", S, [2, 1], {"sight": True}), "r_tent_orange": ("r22_068", S, [2, 1], {"sight": True}),
    "r_tent_low": ("r22_070", S, [2, 1], {}), "r_awning": ("r22_073", S, [2, 1], {"block": False, "layer": "floor"}),
    # большие постройки
    "r_bunker": ("r26_000", B, [5, 2], {"sight": True}), "r_bunker_small": ("r26_012", B, [3, 2], {"sight": True}),
    "r_hangar": ("r26_001", B, [6, 2], {"sight": True}), "r_barn": ("r26_015", B, [4, 2], {"sight": True}),
    "r_water_tower": ("r26_006", B, [1, 1], {}), "r_water_tower_b": ("r26_007", B, [1, 1], {}),
    "r_water_tower_tall": ("r26_016", B, [2, 1], {"sight": True}), "r_derrick": ("r27_002", B, [2, 1], {"sight": True}),
    "r_silo": ("r27_018", B, [2, 2], {"sight": True}),
    # деревья и сухая трава (трава — проходимая)
    **{f"r_dtree_{c}": (img, 1.3, [1, 1], {}) for c, img in zip("abcdefg", ("r21_011", "r21_012", "r21_013", "r21_014",
                                                                           "r21_016", "r21_020", "r21_022"))},
    "r_dry_grass": ("r21_004", S, [1, 1], {"block": False}), "r_dry_grass_b": ("r21_005", S, [1, 1], {"block": False}),
    "r_dry_bush": ("r21_006", S, [1, 1], {"block": False}),
    # хлам и мелочь
    "r_junk_mound": ("r21_044", S, [4, 2], {"sight": True, "search": "junk", "title": "гора хлама"}),
    "r_dumpster": ("r21_045", S, [2, 1], {"search": "junk", "title": "мусорный бак"}),
    "r_dumpster_b": ("r21_050", S, [2, 1], {"search": "junk", "title": "мусорный бак"}),
    "r_trash_can": ("r21_046", S, [1, 1], {"search": "junk", "title": "урна"}),
    "r_billboard": ("r21_040", S, [1, 1], {}), "r_pole_broken": ("r21_041", S, [1, 1], {}),
    "r_pole_wire": ("r21_049", S, [1, 1], {}),
    "r_trash": ("r21_024", S, [2, 1], {"block": False, "layer": "floor"}),
    "r_bones": ("r21_027", S, [2, 1], {"block": False, "layer": "floor"}),
    "r_rocks": ("r21_026", S, [2, 1], {}), "r_planks": ("r21_031", S, [2, 1], {}), "r_planks_b": ("r21_033", S, [2, 1], {}),
    "r_barrels": ("r22_032", S, [1, 1], {"search": "junk", "title": "бочка"}),
    "r_bin": ("r22_042", S, [1, 1], {}), "r_bin_b": ("r22_043", S, [1, 1], {}),
    "r_logs": ("r22_051", S, [1, 1], {}), "r_logs_b": ("r22_065", S, [1, 1], {}),
    # свет (ночные карты, src/lighting.py): фонари, бочки с огнём, горящие обломки
    "r_streetlamp": ("r12_033", B, [1, 1], {"light": {"r": 210, "color": [255, 165, 85], "at": [0.82, 0.1]}}),
    "r_streetlamp_b": ("r12_035", B, [1, 1], {"light": {"r": 210, "color": [255, 165, 85], "at": [0.18, 0.1]}}),
    "x_fire_barrel": ("r12_052", B, [1, 1], {"title": "бочка с огнём",
                      "light": {"r": 170, "color": [255, 140, 60], "at": [0.5, 0.12], "flicker": 1, "flame": True}}),
    "r_burning_rubble": ("r12_022", B, [2, 1], {"light": {"r": 190, "color": [255, 120, 50], "at": [0.5, 0.45],
                                                         "flicker": 1, "flame": True}}),
    "r_sandbags": ("r24_048", S, [1, 1], {}), "r_sandbags_b": ("r24_049", S, [1, 1], {}),
    "r_sandbag_row": ("r24_057", S, [2, 1], {}), "r_sandbag_row_b": ("r24_060", S, [2, 1], {}),
    # машины
    "r_car_wreck": ("r21_051", V, [4, 1], {"search": "junk", "title": "остов машины"}),
    "r_car_a": ("r22_037", V, [2, 1], {}), "r_car_b": ("r22_038", V, [2, 1], {}),
    "r_car_c": ("r22_039", V, [2, 1], {}), "r_pickup": ("r22_040", V, [2, 1], {}),
    "r_car_red": ("r24_043", V, [2, 1], {}), "r_taxi": ("r24_034", V, [2, 1], {}),
    "r_car_d": ("r24_035", V, [2, 1], {}), "r_car_e": ("r24_050", V, [2, 1], {}),
    "r_moto": ("r21_052", S, [2, 1], {}), "r_moto_b": ("r24_030", S, [2, 1], {}),
    "r_rv": ("r24_018", V, [5, 1], {"sight": True, "search": "cloth", "title": "трейлер"}),
    "r_rv_b": ("r24_025", V, [5, 1], {"sight": True}), "r_rv_c": ("r24_026", V, [5, 1], {"sight": True}),
    "r_camper": ("r24_003", V, [4, 1], {"sight": True}),
    "r_army_truck": ("r24_005", V, [5, 1], {"sight": True, "search": "military", "title": "армейский грузовик"}),
    "r_tanker": ("r24_006", V, [5, 1], {"sight": True}), "r_van": ("r24_012", V, [5, 1], {"sight": True}),
}


# Набор «west» (Wild West, SCKR) — мебель и улица для ручной расстановки городов (docs/furnish/logic.md).
# Имена w_*; след — по ширине спрайта (48 px — клетка); настенное — block False (вешается на стену).
W = "pk:west/west_"
WEST = {
    # дом и контора
    "w_desk": (W + "2_000", {"foot": [2, 1], "title": "письменный стол"}),
    "w_chair": (W + "2_001", {"block": False}),
    "w_chair_b": (W + "2_002", {"block": False}),
    "w_sofa": (W + "2_003", {"foot": [2, 1]}),
    "w_rocker": (W + "2_004", {}),
    "w_bed": (W + "2_005", {"foot": [2, 1], "title": "кровать"}),
    "w_wardrobe": (W + "2_006", {"search": "cloth", "title": "платяной шкаф"}),
    "w_dresser": (W + "2_007", {"foot": [2, 1], "search": "drawer", "title": "комод"}),
    "w_nightstand": (W + "2_008", {}),
    "w_fireplace": (W + "2_010", {"foot": [2, 1], "light": {"r": 140, "color": [255, 150, 70], "at": [0.5, 0.75], "flicker": 0.4}}),
    "w_wall_clock": (W + "2_011", {"block": False}),
    "w_armchair": (W + "2_013", {}),
    "w_bench": (W + "2_015", {"foot": [2, 1]}),
    "w_stove": (W + "2_018", {"title": "печка"}),
    "w_grand_clock": (W + "2_019", {}),
    "w_poker": (W + "2_021", {"foot": [2, 1]}),
    "w_bathtub": (W + "2_023", {"foot": [2, 1]}),
    "w_curtains": (W + "2_026", {"foot": [2, 1], "block": False}),
    "w_window": (W + "2_027", {"foot": [2, 1], "block": False}),
    "w_mirror": (W + "2_028", {"block": False}),
    "w_painting": (W + "2_030", {"foot": [2, 1], "block": False}),
    "w_plant": (W + "2_031", {}),
    "w_plant_b": (W + "2_042", {}),
    "w_hay": (W + "2_045", {}),
    "w_lamp": (W + "2_050", {"block": False, "light": {"r": 90, "color": [255, 190, 110], "at": [0.5, 0.3], "flicker": 0.3}}),
    "w_rug_red": (W + "2_060", {"foot": [2, 2], "block": False, "layer": "floor"}),
    "w_rug_green": (W + "2_061", {"foot": [2, 2], "block": False, "layer": "floor"}),
    "w_rug_quilt": (W + "2_062", {"foot": [2, 2], "block": False, "layer": "floor"}),
    "w_shelf": (W + "2_106", {"foot": [2, 1], "search": "shelf", "title": "полки"}),
    "w_wine_rack": (W + "2_107", {"foot": [2, 1]}),
    "w_bar_stools": (W + "2_108", {"foot": [3, 1], "title": "стойка"}),
    "w_sideboard": (W + "2_109", {"foot": [2, 1], "search": "drawer", "title": "буфет"}),
    "w_liquor": (W + "2_110", {"foot": [2, 1], "search": "shelf", "title": "шкаф с бутылками"}),
    "w_bookcase": (W + "2_116", {"foot": [2, 1], "search": "shelf", "title": "книжный шкаф"}),
    "w_bookcase_b": (W + "2_117", {"foot": [2, 1], "search": "shelf", "title": "книжный шкаф"}),
    "w_newspaper": (W + "2_111", {"block": False, "layer": "floor"}),
    "w_mailbox": (W + "2_114", {}),
    # салун
    "w_backbar": (W + "8_019", {"foot": [4, 1], "title": "полки с бутылками"}),
    "w_bar": (W + "8_046", {"foot": [4, 1], "title": "стойка"}),
    "w_bar_b": (W + "8_049", {"foot": [4, 1], "title": "стойка"}),
    "w_jukebox": (W + "8_054", {"title": "музыкальный автомат"}),
    "w_wanted": (W + "8_040", {"block": False}),
    "w_saloon_sign": (W + "8_015", {"foot": [2, 1], "block": False}),
    "w_table_set": (W + "8_025", {"foot": [2, 1]}),
    "w_round_table": (W + "8_037", {"foot": [2, 1]}),
    "w_poker_big": (W + "8_043", {"foot": [3, 1]}),
    "w_pool": (W + "8_048", {"foot": [2, 1]}),
    "w_stool_red": (W + "8_073", {"block": False}),
    "w_stool_grey": (W + "8_075", {"block": False}),
    "w_portrait": (W + "8_018", {"foot": [2, 1], "block": False}),
    "w_wine_tall": (W + "8_058", {}),
    "w_oil_lamp": (W + "8_072", {"block": False, "light": {"r": 90, "color": [255, 190, 110], "at": [0.5, 0.35], "flicker": 0.3}}),
    "w_candelabra": (W + "8_055", {"light": {"r": 110, "color": [255, 180, 90], "at": [0.5, 0.15], "flicker": 0.5}}),
    "w_stairs": (W + "8_068", {"foot": [2, 1]}),
    # улица и двор
    "w_jail": (W + "7_020", {"foot": [2, 2], "title": "камера"}),
    "w_well": (W + "7_024", {"title": "колодец"}),
    "w_pump": (W + "7_025", {"title": "колонка"}),
    "w_hitch": (W + "7_017", {"foot": [2, 1]}),
    "w_hitch_b": (W + "7_018", {"foot": [2, 1]}),
    "w_wagon": (W + "7_040", {"foot": [3, 1], "search": "junk", "title": "фургон"}),
    "w_forge": (W + "7_043", {"light": {"r": 120, "color": [255, 130, 60], "at": [0.5, 0.6], "flicker": 0.6}}),
    "w_outhouse": (W + "7_019", {"title": "сортир"}),
    "w_fence": (W + "7_046", {"foot": [2, 1]}),
    "w_fence_b": (W + "7_054", {"foot": [2, 1]}),
    "w_fence_stakes": (W + "7_055", {"foot": [2, 1]}),
    "w_fence_post": (W + "7_047", {}),
    "w_street_lamp": (W + "7_053", {"light": {"r": 170, "color": [255, 175, 95], "at": [0.6, 0.15]}}),
    "w_crates": (W + "7_030", {"search": "crate", "title": "ящики"}),
    "w_barrels": (W + "7_014", {"foot": [2, 1]}),
    # участок шерифа, кухня, кладовая
    "w_gun_rack": (W + "5_014", {"foot": [2, 1], "title": "оружейная стойка"}),
    "w_desk_b": (W + "5_017", {"foot": [2, 1]}),
    "w_desk_c": (W + "5_018", {"foot": [2, 1], "search": "drawer", "title": "стол"}),
    "w_cabinet": (W + "5_000", {"foot": [2, 1], "search": "drawer", "title": "шкаф"}),
    "w_glass_cabinet": (W + "5_003", {"foot": [2, 1], "search": "shelf", "title": "шкаф со стеклом"}),
    "w_cupboard": (W + "5_004", {"foot": [2, 1], "search": "drawer", "title": "кухонный шкаф"}),
    "w_locker": (W + "5_007", {"search": "locker", "title": "шкафчик"}),
    "w_cookstove": (W + "5_026", {"foot": [2, 1], "title": "плита"}),
    "w_oil_drum": (W + "5_012", {}),
    "w_lantern": (W + "5_046", {"block": False, "light": {"r": 90, "color": [255, 190, 110], "at": [0.5, 0.4], "flicker": 0.3}}),
    "w_sacks": (W + "5_043", {}),
    "w_table_long": (W + "5_006", {"foot": [2, 1], "title": "стол"}),        # прямой стол — для рядов
    "w_table_plain": (W + "5_001", {"foot": [2, 1], "title": "стол"}),
    "w_chair_r": (W + "8_024", {"block": False}),                           # стул в профиль: сидят лицом вправо
    "w_chair_l": (W + "8_050", {"block": False}),                           # стул в профиль: лицом влево
    "w_crate_sacks": (W + "5_041", {"foot": [2, 1], "search": "crate", "title": "ящик"}),
    "w_junk_pile": (W + "5_036", {"foot": [2, 1], "search": "junk", "title": "куча хлама"}),
}
# стеллажи старого каталога с картинкой в две клетки и следом в одну — двойники со следом [2, 1]:
# ставить вплотную рядами, не проходить сквозь край картинки (docs/furnish/logic.md)
WEST.update({
    # настольные лампы — мельче напольных: на столе лампа не может быть размером со стул
    "w_table_lamp": (W + "8_072", {"block": False, "scale": 0.6, "light": {"r": 80, "color": [255, 190, 110], "at": [0.5, 0.35], "flicker": 0.3}}),
    "w_table_lantern": (W + "5_046", {"block": False, "scale": 0.6, "light": {"r": 80, "color": [255, 190, 110], "at": [0.5, 0.4], "flicker": 0.3}}),
    "table_lantern": ("p2_088", {"block": False, "scale": 0.45, "light": {"r": 80, "color": [255, 180, 90], "at": [0.5, 0.4], "flicker": 0.4}}),
    "rack_goods": ("p2_006", {"scale": 0.75, "sight": True, "search": "shelf", "title": "стеллаж", "foot": [2, 1]}),   # shelf_goods со следом по ширине картинки
    "rack_stuff": ("p2_051", {"scale": 0.75, "sight": True, "search": "shelf", "title": "стеллаж с барахлом", "foot": [2, 1]}),   # shelf_stuff_3 со следом по ширине картинки
    "rack_tools": ("p2_052", {"scale": 0.75, "sight": True, "search": "shelf", "title": "стеллаж с барахлом", "foot": [2, 1]}),   # shelf_stuff_4 со следом по ширине картинки
    "rack_parts": ("p2_053", {"scale": 0.75, "sight": True, "search": "shelf", "title": "стеллаж с барахлом", "foot": [2, 1]}),   # shelf_stuff_5 со следом по ширине картинки
    "rack_metal": ("p2_021", {"scale": 0.75, "search": "shelf", "title": "железный стеллаж", "foot": [2, 1]}),   # metal_shelf со следом по ширине картинки
    "rack_tall": ("p2_038", {"scale": 0.75, "sight": True, "foot": [2, 1]}),   # shelf_metal_tall со следом по ширине картинки
    "rack_empty": ("p2_005", {"scale": 0.75, "sight": True, "foot": [2, 1]}),   # shelf_empty со следом по ширине картинки
    "rack_rust": ("p2_039", {"scale": 0.75, "sight": True, "foot": [2, 1]}),   # shelf_rust со следом по ширине картинки
})
REPLACED.update(WEST)


def register_pack_props(catalog):
    """Предметы, взятые из наборов SCKR (REPLACED выше): картинка «pk:…» уже есть, рисовать нечего —
    в каталог пишутся только поля. Поля не перетираются: правка в data/props.json остаётся главной."""
    added = 0
    for name, (img, fields) in REPLACED.items():
        entry = catalog["props"].setdefault(name, {})
        if not entry:
            added += 1
        entry.setdefault("img", img)
        for k, v in fields.items():
            entry.setdefault(k, v)
    return added


def main():
    catalog_only = "--catalog-only" in sys.argv      # только регистрация наборных предметов
    pygame.init()
    pygame.display.set_mode((1, 1))
    with open(INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)
    with open(CATALOG, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    if catalog_only:
        print(f"зарегистрировано наборных предметов: {register_pack_props(catalog)} -> {CATALOG}")
        with open(CATALOG, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=1)
        return
    register_pack_props(catalog)
    for name, (draw, desc) in PROPS.items():
        img = draw()
        if not getattr(draw, "full_size", False) and "vault_door_cliff" not in getattr(draw, "__code__", draw.__call__).co_names:
            img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
        pygame.image.save(img, os.path.join(OUT, name + ".png"))
        # made_by у уже нарисованных не переписываем: у дверей убежищ там пометка про vault_door_cliff
        old = index.get(name, {}).get("made_by", "")
        index[name] = {"page": None, "rect": None, "size": list(img.get_size()),
                       "made_by": old if old.startswith("tools/make_props.py ") else "tools/make_props.py"}
        entry = catalog["props"].setdefault(name, {})
        entry.setdefault("img", name)
        for k, v in desc.items():
            entry.setdefault(k, v)
    # свет у объектов «wasteland town»
    for name, light in {"lamp_post": {"r": 200, "color": [255, 170, 90], "at": [0.5, 0.06]},
                        "lantern_lit": {"r": 120, "color": [255, 180, 90], "at": [0.5, 0.4], "flicker": 0.4},
                        "candles": {"r": 80, "color": [255, 170, 80], "at": [0.5, 0.3], "flicker": 0.6},
                        "terminal": {"r": 70, "color": [90, 220, 120], "at": [0.5, 0.3]}}.items():
        catalog["props"][name].setdefault("light", light)
    catalog["props"].setdefault("campfire", {"img": "p2_079", "scale": 0.75, "light": {
        "r": 190, "color": [255, 140, 60], "at": [0.5, 0.35], "flicker": 1, "flame": True}})
    for name, (img, scale, foot, extra) in RUINS.items():
        entry = catalog["props"].setdefault(name, {})
        for k, v in {"img": img, "scale": scale, "foot": foot, **extra}.items():
            entry.setdefault(k, v)
    catalog["loot_tables"].setdefault("grave", {"крышки": [3, 15, 60], "бинт": [1, 1, 20], "патроны": [2, 5, 25],
                                                "ткань": [1, 2, 40]})
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    with open(CATALOG, "w", encoding="utf-8") as f:
        # формат — как у закоммиченного data/props.json (indent=1): одна правка не должна
        # переформатировать весь каталог на четыре тысячи строк
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print(f"нарисовано объектов: {len(PROPS)} -> {OUT}")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
