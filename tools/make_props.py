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

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "town", "props")
INDEX = os.path.join(ROOT, "assets", "town", "index.json")
CATALOG = os.path.join(ROOT, "data", "props.json")

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


def vault_door():
    """Скала с круглой дверью-шестернёй и жёлтой рамой (снаружи)."""
    s = cliff(96, 72)
    cx, cy, r = 48, 42, 22
    pygame.draw.circle(s, (40, 36, 34), (cx, cy), r + 4)              # проём
    gear(s, cx, cy, r)
    for k in range(-26, 27, 4):                                          # жёлто-чёрная рама
        col = (220, 180, 40) if (k // 4) % 2 == 0 else (30, 28, 26)
        px(s, cx + k, cy - r - 6, col)
        px(s, cx + k + 1, cy - r - 6, col)
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


def ladder():
    s = canvas(24, 40)
    light = canvas(24, 40)
    pygame.draw.polygon(light, (255, 240, 180, 60), [(4, 0), (20, 0), (24, 40), (0, 40)])
    s.blit(light, (0, 0))
    rect(s, 6, 0, 2, 40, (120, 110, 96))
    rect(s, 16, 0, 2, 40, (120, 110, 96))
    for y in range(3, 40, 6):
        rect(s, 6, y, 12, 2, (150, 140, 120))
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


def vault_sign():
    s = canvas(26, 20)
    rect(s, 1, 1, 24, 16, (40, 70, 140))
    rect(s, 2, 2, 22, 14, (52, 90, 170))
    font = pygame.font.Font(None, 18)
    t = font.render("57", False, (236, 200, 60))
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
    "x_board": (board, {"foot": [2, 1]}),
    "x_sandbags": (sandbags, {"foot": [2, 1]}),
    "x_cliff": (cliff, {"foot": [2, 1], "sight": True}),
    "x_pipe": (pipe, {"foot": [1, 1]}),
    "x_puddle": (puddle, {"block": False, "layer": "floor"}),
    "x_vault_sign": (vault_sign, {"foot": [1, 1]}),
    "x_mesa_vault": (mesa_vault, {"foot": [14, 3], "sight": True}),
    "x_barrel_boom": (barrel_boom, {"foot": [1, 1], "explosive": True}),
    "x_thermometer": (thermometer, {"foot": [2, 1], "sight": True}),
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


def dump_catalog(cat):
    """Тот же вид, что у data/props.json: одна запись — одна строка."""
    line = lambda v: json.dumps(v, ensure_ascii=False, separators=(", ", ": "))
    out = ["{"]
    for k, v in cat.items():
        if isinstance(v, dict):
            out.append(f"  {json.dumps(k, ensure_ascii=False)}: {{")
            items = list(v.items())
            for i, (kk, vv) in enumerate(items):
                out.append(f"    {json.dumps(kk, ensure_ascii=False)}: {line(vv)}" + ("," if i < len(items) - 1 else ""))
            out.append("  }")
        else:
            out.append(f"  {json.dumps(k, ensure_ascii=False)}: {line(v)}")
        out[-1] += ","
    out[-1] = out[-1].rstrip(",")
    return "\n".join(out) + "\n}\n"


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    with open(INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)
    with open(CATALOG, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    for name, (draw, desc) in PROPS.items():
        img = draw()
        img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
        pygame.image.save(img, os.path.join(OUT, name + ".png"))
        index[name] = {"page": None, "rect": None, "size": list(img.get_size()), "made_by": "tools/make_props.py"}
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
        f.write(dump_catalog(catalog))
    print(f"нарисовано объектов: {len(PROPS)} -> {OUT}")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
