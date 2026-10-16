"""
Свои мелкие спрайты для убежищ — то, чего нет в наборах: меловые счёты, детский рисунок, доска девяти, схема убежищ,
полотнище «МЫ НЕ УШЛИ», трафаретная «15», разметка пола, кабели, пятна сырости, следы и колеи, блеск свежих крышек.
Рисуются пиксель-артом (без сглаживания), 48-пиксельными клетками, и регистрируются как объекты x_vd_*
(data/props.json, assets/town/index.json). Стенные — block=False (висят на стене), полу́ — layer=floor.

Запуск из папки game_project:  .venv/bin/python tools/make_vault_decals.py
"""
import json
import math
import os
import random

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
T = 48
OUT = "assets/town/props"
REG = {}          # имя -> {"size": [w, h], "layer": ..., "block": ..., "foot": ...}


def new(w=T, h=T):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def save(name, img, layer=None, block=False, foot=(1, 1), light=None):
    pygame.image.save(img, os.path.join(OUT, f"{name}.png"))
    REG[name] = {"size": list(img.get_size()), "layer": layer, "block": block, "foot": list(foot), "light": light}


def outline(img, color=(20, 18, 16, 255)):
    """Тёмная обводка по краю непрозрачных пикселей — как у остальных спрайтов набора."""
    w, h = img.get_size()
    src = img.copy()
    for y in range(h):
        for x in range(w):
            if src.get_at((x, y)).a == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src.get_at((nx, ny)).a > 180:
                        img.set_at((x, y), color)
                        break
    return img


def blob(img, cx, cy, rx, ry, color, seed=0, wob=0.25):
    """Неровное пятно (три гармоники по краю)."""
    rnd = random.Random(seed)
    k = [rnd.uniform(0, 6.3) for _ in range(3)]
    for y in range(int(cy - ry * 1.5), int(cy + ry * 1.5) + 1):
        for x in range(int(cx - rx * 1.5), int(cx + rx * 1.5) + 1):
            if not (0 <= x < img.get_width() and 0 <= y < img.get_height()):
                continue
            a = math.atan2((y - cy) / ry, (x - cx) / rx)
            w = 1 + wob * (0.6 * math.sin(2 * a + k[0]) + 0.5 * math.sin(3 * a + k[1]) + 0.35 * math.sin(5 * a + k[2]))
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= w * w:
                img.set_at((x, y), color)


# ------------------------------------------------------------------ стена
def tally():
    """Меловые счёты на стене: пять групп «палочки с зачёркиванием»."""
    img = new()
    ink = (70, 66, 62, 230)
    ox, oy = 4, 14
    for g in range(6):
        gx = ox + (g % 3) * 14
        gy = oy + (g // 3) * 15
        full = g < 5 or True
        for i in range(4):
            pygame.draw.line(img, ink, (gx + i * 2, gy), (gx + i * 2, gy + 9))
        if g < 5:
            pygame.draw.line(img, ink, (gx - 1, gy + 8), (gx + 8, gy + 1))
        else:
            pygame.draw.line(img, ink, (gx + 10, gy), (gx + 10, gy + 9))
    save("x_vd_tally", img)


def drawing():
    """Детский рисунок кнопками на стене: дом, солнце, девять человечков в ряд — «все дома»."""
    img = new()
    paper = (232, 224, 198, 255)
    pygame.draw.rect(img, paper, (8, 10, 32, 30))
    pygame.draw.rect(img, (190, 180, 150, 255), (8, 38, 32, 2))
    pygame.draw.line(img, (110, 170, 80, 255), (9, 33), (38, 33), 2)                 # трава
    pygame.draw.rect(img, (196, 84, 60, 255), (16, 22, 12, 9))                       # дом
    pygame.draw.polygon(img, (120, 60, 44, 255), [(14, 22), (30, 22), (22, 15)])
    pygame.draw.rect(img, (250, 220, 90, 255), (21, 26, 3, 5))
    pygame.draw.circle(img, (255, 214, 60, 255), (35, 15), 3)                        # солнце
    for i in range(9):                                                                 # девять человечков
        x = 10 + i * 3
        c = [(60, 90, 200), (200, 60, 70), (60, 160, 90), (170, 90, 180), (230, 140, 50)][i % 5]
        pygame.draw.rect(img, c, (x, 35, 2, 3))
        img.set_at((x, 34), (240, 190, 150, 255))
    for p in ((10, 11), (37, 11)):                                                     # кнопки
        pygame.draw.circle(img, (210, 50, 50, 255), p, 2)
    outline(img)
    save("x_vd_drawing", img)


def nine_board():
    """Доска девяти: рамка и девять фотографий в два ряда; под ними можно ставить свечи."""
    img = new(96, T)
    wood, wood_d, wood_l = (112, 78, 50, 255), (72, 48, 32, 255), (150, 112, 74, 255)
    pygame.draw.rect(img, wood_d, (3, 8, 90, 36))
    pygame.draw.rect(img, wood, (4, 9, 88, 34))
    pygame.draw.rect(img, wood_l, (4, 9, 88, 2))
    rnd = random.Random(15)
    skin = [(236, 196, 160), (200, 150, 110), (150, 100, 70), (242, 210, 180), (180, 130, 96)]
    cols = [(60, 90, 120), (120, 70, 60), (70, 110, 80), (140, 120, 60), (90, 70, 110), (100, 100, 110)]
    k = 0
    for row, n in ((0, 5), (1, 4)):
        for i in range(n):
            x = 8 + i * 17 + (8 if n == 4 else 0)
            y = 13 + row * 15
            pygame.draw.rect(img, (232, 226, 206, 255), (x, y, 14, 13))                  # снимок с белым полем
            pygame.draw.rect(img, cols[k % 6], (x + 1, y + 1, 12, 11))
            pygame.draw.circle(img, skin[rnd.randrange(5)], (x + 7, y + 5), 3)
            pygame.draw.rect(img, (50, 52, 60, 255), (x + 3, y + 8, 8, 4))
            if k in (3, 7):                                                              # у двоих — чёрная лента
                pygame.draw.line(img, (20, 20, 20, 255), (x, y), (x + 13, y + 12))
            k += 1
    outline(img)
    save("x_vd_nine", img)


def map_board():
    """Карта сети убежищ округа: береговая линия, пять булавок с нитками и цифры 4, 12, 15, 22, 57."""
    img = new(96, T)
    pygame.draw.rect(img, (84, 60, 40, 255), (3, 6, 90, 38))
    pygame.draw.rect(img, (206, 196, 162, 255), (5, 8, 86, 34))
    pygame.draw.polygon(img, (150, 170, 176, 255), [(5, 8), (40, 8), (28, 22), (14, 30), (5, 34)])   # океан
    pygame.draw.line(img, (110, 90, 60, 255), (40, 8), (28, 22), 1)
    for i in range(0, 80, 9):                                                                          # сетка
        pygame.draw.line(img, (190, 180, 148, 255), (12 + i, 9), (12 + i, 40))
    pins = {"4": (24, 24), "12": (54, 14), "15": (50, 30), "22": (78, 20), "57": (70, 36)}
    prev = None
    for label, p in pins.items():
        if prev:
            pygame.draw.line(img, (190, 40, 40, 255), prev, p)
        prev = p
    font = pygame.font.Font(None, 11)
    for label, p in pins.items():
        pygame.draw.circle(img, (210, 30, 30, 255) if label != "15" else (250, 210, 40, 255), p, 2)
        t = font.render(label, False, (50, 40, 30))
        img.blit(t, (p[0] + 3, p[1] - 5))
    outline(img)
    save("x_vd_map", img)


def sheet_banner():
    """Простыня на двух верёвках с краской: «МЫ НЕ УШЛИ»."""
    img = new(96, T)
    cloth, shade = (226, 222, 208, 255), (196, 190, 174, 255)
    pygame.draw.polygon(img, cloth, [(4, 8), (92, 8), (91, 38), (80, 41), (60, 38), (40, 41), (20, 38), (5, 40)])
    for x in range(10, 92, 14):
        pygame.draw.line(img, shade, (x, 9), (x + 1, 38))
    pygame.draw.line(img, (150, 120, 80, 255), (2, 7), (94, 7))
    for p in ((4, 8), (91, 8)):
        pygame.draw.circle(img, (120, 80, 50, 255), p, 2)
    font = pygame.font.Font(None, 17)
    txt = font.render("МЫ НЕ УШЛИ", False, (170, 38, 36))
    # без сглаживания: порог по альфе/яркости
    w, h = txt.get_size()
    for y in range(h):
        for x in range(w):
            c = txt.get_at((x, y))
            if c.r > 90 and c.a > 100:
                img.set_at((12 + x, 16 + y), (172, 40, 38, 255))
    outline(img)
    save("x_vd_sheet", img)


def stencil(num):
    """Большой трафаретный номер убежища жёлтым с чёрным контуром."""
    img = new(96, T)
    font = pygame.font.Font(None, 54)
    txt = font.render(str(num), False, (255, 255, 255))
    w, h = txt.get_size()
    ox, oy = (96 - w) // 2, (T - h) // 2 + 1
    mask = pygame.mask.from_surface(txt, 100)
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
        for (x, y) in mask.outline() if False else []:
            pass
    shadow = mask.to_surface(setcolor=(18, 16, 14, 255), unsetcolor=(0, 0, 0, 0))
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            img.blit(shadow, (ox + dx, oy + dy))
    fill = mask.to_surface(setcolor=(238, 196, 40, 255), unsetcolor=(0, 0, 0, 0))
    img.blit(fill, (ox, oy))
    for y in range(T):                                                                     # потёртость трафарета
        for x in range(96):
            if img.get_at((x, y)).a and (x * 7 + y * 13) % 11 == 0:
                c = img.get_at((x, y))
                img.set_at((x, y), (c.r * 3 // 4, c.g * 3 // 4, c.b * 3 // 4, c.a))
    save(f"x_vd_num{num}", img)


def exit_arrow():
    img = new(72, 28)
    pts = [(4, 14), (16, 4), (16, 10), (68, 10), (68, 18), (16, 18), (16, 24)]
    pygame.draw.polygon(img, (230, 200, 40, 255), pts)
    pygame.draw.polygon(img, (26, 24, 20, 255), pts, 1)
    font = pygame.font.Font(None, 11)
    t = font.render("ВЫХОД", False, (20, 20, 20))
    img.blit(t, (22, 9))
    save("x_vd_exit", img)


def plaque():
    img = new(64, 26)
    pygame.draw.rect(img, (156, 120, 54, 255), (3, 5, 58, 15))
    pygame.draw.rect(img, (210, 172, 80, 255), (3, 5, 58, 2))
    pygame.draw.rect(img, (90, 66, 30, 255), (3, 18, 58, 2))
    font = pygame.font.Font(None, 10)
    t = font.render("СМОТРИТЕЛЬ", False, (50, 34, 14))
    img.blit(t, (7, 9))
    for p in ((5, 7), (58, 7), (5, 17), (58, 17)):
        img.set_at(p, (70, 50, 20, 255))
    save("x_vd_plaque", img)


def waterline():
    """Отметка уровня воды на стене: бурая кромка, ниже — тёмная сырость, в углу — метки уровня."""
    img = new()
    pygame.draw.rect(img, (46, 56, 52, 150), (0, 20, T, 28))
    rnd = random.Random(3)
    for x in range(T):
        y = 18 + rnd.randint(0, 3)
        pygame.draw.line(img, (118, 98, 60, 210), (x, y), (x, y + 2))
    for y in (26, 34, 42):
        pygame.draw.line(img, (20, 24, 22, 220), (4, y), (10, y))
    save("x_vd_waterline", img)


# ------------------------------------------------------------------ пол
def hazard(vertical=False):
    """Жёлто-чёрная разметка поперёк клетки (диагональные «зебры»)."""
    img = new()
    for i in range(T):
        for j in range(12):
            on = ((i + j) // 6) % 2 == 0
            c = (232, 192, 36, 235) if on else (36, 32, 28, 235)
            x, y = (j + 18, i) if vertical else (i, j + 18)
            img.set_at((x, y), c)
    save("x_vd_hz_v" if vertical else "x_vd_hz_h", img, layer="floor")


def cables():
    """Толстые чёрные кабели по полу: прямые и повороты (подключены к аккумуляторам нижнего яруса)."""
    def base():
        return new()

    def tube(img, pts, w=6):
        pygame.draw.lines(img, (22, 22, 26, 255), False, pts, w)
        pygame.draw.lines(img, (52, 54, 62, 255), False, [(x, y - 1) for x, y in pts], w - 3)
        pygame.draw.lines(img, (92, 96, 108, 255), False, [(x, y - 2) for x, y in pts], 1)
    h = base(); tube(h, [(0, 24), (24, 25), (48, 24)]); save("x_vd_cab_h", h, layer="floor")
    v = base(); tube(v, [(24, 0), (25, 24), (24, 48)]); save("x_vd_cab_v", v, layer="floor")
    save("x_vd_cab_es", (lambda i: (tube(i, [(48, 24), (30, 24), (24, 30), (24, 48)]), i)[1])(base()), layer="floor")
    save("x_vd_cab_ws", (lambda i: (tube(i, [(0, 24), (18, 24), (24, 30), (24, 48)]), i)[1])(base()), layer="floor")
    save("x_vd_cab_en", (lambda i: (tube(i, [(48, 24), (30, 24), (24, 18), (24, 0)]), i)[1])(base()), layer="floor")
    save("x_vd_cab_wn", (lambda i: (tube(i, [(0, 24), (18, 24), (24, 18), (24, 0)]), i)[1])(base()), layer="floor")


def stains():
    """Пятна: сырость, ржавчина, масло, кровь — полупрозрачные, чтобы лежали на любом полу."""
    kinds = {"wet": ((40, 56, 62, 120), (150, 190, 200, 70)), "rust": ((120, 66, 34, 110), (160, 96, 50, 60)),
             "oil": ((18, 18, 22, 140), (80, 70, 110, 70)), "blood": ((96, 18, 18, 170), (150, 30, 28, 90))}
    for n, (c, hi) in kinds.items():
        for v in range(2):
            img = new()
            rnd = random.Random(hash(n) % 1000 + v)
            blob(img, 24 + rnd.randint(-3, 3), 24 + rnd.randint(-3, 3), 13 + v * 3, 9 + rnd.randint(0, 4), c, seed=v * 7 + 1)
            blob(img, 22, 22, 5 + v, 3, hi, seed=v + 5)
            save(f"x_vd_{n}{v}", img, layer="floor")
    for v, vert in enumerate((False, True)):                                           # волочение: след от тела
        img = new()
        for i in range(4, 44):
            o = int(2 * math.sin(i / 5.0))
            for t in range(-2, 3):
                x, y = (24 + o + t, i) if vert else (i, 24 + o + t)
                if random.Random(i * 5 + t).random() < 0.8:
                    img.set_at((x, y), (92, 16, 16, 200))
        save(f"x_vd_drag{'v' if vert else 'h'}", img, layer="floor")


# ------------------------------------------------------------------ улица
def ruts():
    """Колеи на песке: две тёмные полосы с поперечными насечками."""
    for vert in (False, True):
        img = new()
        for line in (16, 32):
            for i in range(T):
                x, y = (line, i) if vert else (i, line)
                img.set_at((x, y), (92, 70, 44, 150))
                x2, y2 = (x + 1, y) if vert else (x, y + 1)
                img.set_at((x2, y2), (120, 94, 60, 90))
        for i in range(2, T, 6):
            a = (16, 32) if vert else (i, 16)
            for p in ((i, 16), (i, 32)) if not vert else ((16, i), (32, i)):
                pygame.draw.line(img, (104, 80, 50, 200), (p[0] - 1, p[1]) if not vert else (p[0], p[1] - 1),
                                 (p[0] + 1, p[1]) if not vert else (p[0], p[1] + 1))
        save("x_vd_ruts_v" if vert else "x_vd_ruts_h", img, layer="floor")


def footprints():
    """Следы босых и обутых ног на песке — цепочкой."""
    img = new()
    for i, (x, y) in enumerate(((10, 40), (18, 32), (11, 24), (19, 16), (12, 8))):
        for dx, dy, w, h in ((0, 0, 3, 5), (0, -2, 3, 1)):
            pygame.draw.rect(img, (96, 74, 46, 130), (x + dx, y + dy, w, h))
    for i, (x, y) in enumerate(((30, 44), (36, 34), (29, 26), (37, 18), (30, 10))):
        pygame.draw.rect(img, (96, 74, 46, 120), (x, y, 3, 5))
    save("x_vd_steps", img, layer="floor")


def caps():
    """Горка свежих, нечеканенных крышек: блестят, как новенькие."""
    img = new(32, 24)
    rnd = random.Random(7)
    for i in range(22):
        x, y = 6 + rnd.randint(0, 18), 8 + rnd.randint(0, 11)
        pygame.draw.ellipse(img, (190, 154, 52, 255), (x, y, 6, 4))
        pygame.draw.ellipse(img, (246, 224, 120, 255), (x + 1, y, 4, 2))
    for p in ((10, 9), (20, 12), (15, 15)):
        pygame.draw.line(img, (255, 255, 235, 255), (p[0] - 1, p[1]), (p[0] + 1, p[1]))
        pygame.draw.line(img, (255, 255, 235, 255), (p[0], p[1] - 1), (p[0], p[1] + 1))
    outline(img)
    save("x_vd_caps", img, block=False, light={"r": 50, "color": [255, 230, 140], "at": [0.5, 0.6], "flicker": 0.2})


def drop():
    """Капли с трубы: тёмный след и блик — вешается на потолочную трубу или стену над водой."""
    img = new()
    for x, ln in ((18, 9), (26, 5), (33, 12)):
        pygame.draw.line(img, (60, 90, 98, 170), (x, 14), (x, 14 + ln))
        pygame.draw.circle(img, (160, 210, 220, 220), (x, 14 + ln + 1), 1)
    save("x_vd_drip", img)


def sparks():
    """Искры от сгоревшего щита: жёлто-белые, с мерцающим светом."""
    img = new()
    rnd = random.Random(11)
    for _ in range(14):
        x, y = rnd.randint(8, 40), rnd.randint(8, 40)
        pygame.draw.line(img, (255, 236, 150, 255), (x, y), (x + rnd.randint(-3, 3), y + rnd.randint(-3, 3)))
        img.set_at((x, y), (255, 255, 255, 255))
    save("x_vd_sparks", img, light={"r": 90, "color": [255, 220, 120], "at": [0.5, 0.5], "flicker": 0.9})


def frames():
    """Дверные рамы проёмов: стальные стойки по краям, перемычка с индикатором и жёлтой полосой."""
    steel, dark, edge = (84, 88, 98, 255), (40, 42, 48, 255), (130, 136, 148, 255)

    def strip(img, rect):
        pygame.draw.rect(img, dark, rect)
        x, y, w, h = rect
        pygame.draw.rect(img, steel, (x + 1, y + 1, max(1, w - 2), max(1, h - 2)))
    for name, rect in (("l", (0, 0, 8, T)), ("r", (T - 8, 0, 8, T)), ("t", (0, 0, T, 8)), ("b", (0, T - 8, T, 8))):
        img = new()
        strip(img, rect)
        x, y, w, h = rect
        if name in "lr":
            for yy in range(2, T, 8):
                pygame.draw.rect(img, (232, 192, 36, 255), (x + 1, yy, w - 2, 3))
        else:
            for xx in range(2, T, 8):
                pygame.draw.rect(img, (232, 192, 36, 255), (xx, y + 1, 3, h - 2))
        save(f"x_vd_fr_{name}", img, layer="floor")
    # перемычка над проёмом: лежит на верхней клетке; зелёный индикатор «открыто»
    img = new()
    pygame.draw.rect(img, dark, (0, 2, T, 14))
    pygame.draw.rect(img, steel, (0, 3, T, 11))
    pygame.draw.line(img, edge, (0, 4), (T, 4))
    for xx in range(2, T, 8):
        pygame.draw.rect(img, (232, 192, 36, 255), (xx, 10, 4, 3))
    pygame.draw.rect(img, (20, 20, 22, 255), (20, 5, 8, 4))
    pygame.draw.rect(img, (110, 240, 140, 255), (22, 6, 4, 2))
    save("x_vd_fr_hdr", img, light={"r": 60, "color": [110, 240, 140], "at": [0.5, 0.3], "flicker": 0.0})


LAMPCOL = {"warm": (255, 190, 110), "cold": (160, 200, 235), "red": (255, 60, 50), "green": (130, 235, 160),
           "violet": (200, 130, 255), "amber": (255, 160, 50)}


def lamps():
    """Свои лампы: настенный плафон в стальной решётке и торшер на ножке; цвет — как у света."""
    for kind, c in LAMPCOL.items():
        dark = tuple(int(v * 0.45) for v in c)
        # настенный плафон: кронштейн, решётка, горящая колба и ореол на стене
        img = new()
        for r, a in ((15, 40), (11, 70)):
            pygame.draw.circle(img, c + (a,), (24, 20), r)
        pygame.draw.rect(img, (46, 48, 54, 255), (14, 10, 20, 20), border_radius=4)
        pygame.draw.rect(img, dark + (255,), (17, 13, 14, 14), border_radius=3)
        pygame.draw.rect(img, c + (255,), (19, 15, 10, 10), border_radius=2)
        pygame.draw.rect(img, (255, 255, 240, 255), (22, 18, 4, 4))
        for x in (19, 23, 27):                                              # прутья решётки
            pygame.draw.line(img, (30, 32, 36, 255), (x, 13), (x, 27))
        pygame.draw.line(img, (30, 32, 36, 255), (17, 20), (31, 20))
        pygame.draw.rect(img, (70, 72, 80, 255), (20, 30, 8, 3))
        outline(img)
        fl = 0.3 if kind == "red" else 0.05
        save(f"x_vd_wl_{kind}", img, light={"r": 215, "color": [int(v * 0.72) for v in c], "at": [0.5, 0.45], "flicker": fl})
        # торшер: основание, тонкая стойка, конический абажур
        img = new(48, 64)
        pygame.draw.ellipse(img, (30, 30, 34, 255), (16, 54, 16, 7))
        pygame.draw.rect(img, (66, 68, 76, 255), (22, 24, 4, 33))
        pygame.draw.polygon(img, dark + (255,), [(14, 24), (34, 24), (29, 10), (19, 10)])
        pygame.draw.polygon(img, c + (255,), [(17, 22), (31, 22), (28, 13), (20, 13)])
        pygame.draw.rect(img, (255, 255, 235, 255), (22, 17, 4, 3))
        outline(img)
        save(f"x_vd_stand_{kind}", img, block=False, foot=(1, 1),
             light={"r": 235, "color": [int(v * 0.72) for v in c], "at": [0.5, 0.3], "flicker": 0.3 if kind == "red" else 0.05})


for fn in (frames, lamps, tally, drawing, nine_board, map_board, sheet_banner, exit_arrow, plaque, waterline, cables, stains,
           ruts, footprints, caps, drop, sparks):
    fn()
for _n in (7, 15, 4, 11, 12, 22, 57):
    stencil(_n)
hazard(False)
hazard(True)

p = "data/props.json"
d = json.load(open(p, encoding="utf-8"))
tgt = d["props"] if "props" in d else d
for n, r in REG.items():
    ent = {"img": n, "foot": r["foot"], "block": r["block"], "sight": False}
    if r["layer"]:
        ent["layer"] = r["layer"]
    if r["light"]:
        ent["light"] = r["light"]
    tgt[n] = ent
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
p = "assets/town/index.json"
d = json.load(open(p, encoding="utf-8"))
t = d["props"] if "props" in d else d
for n, r in REG.items():
    t[n] = {"size": r["size"], "made_by": "tools/make_vault_decals.py"}
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("нарисовано:", len(REG))
