"""
Свои предметы цистерны под купальнями (tools/build_zzyzx.py, раздел `cs`): напорный насос, стояк в потолок,
слив из потолка, тонкая линия дозирования CS-3, кружка и пепельница Гаса, знак опасности CS-3, табличка
«Ступень 2 — не отключать», довоенный плакат техники безопасности, пломба на шкафу.

В наборах этого нет: насос в pack-наборах только колонка (`w_pump`), труб в наборах — обломки; таблички
с русским текстом рисуются здесь (как `sign_fuel` в tools/make_props.py).

Трубы — в одном стиле с tools/make_pipes.py (серая сталь 18 px, фланцы, ржавые пятна), чтобы лежащие в
цистерне магистрали и стояки читались одной системой. Ничего чужого не перерисовывается: файлы только
свои, `assets/town/index.json` дополняется размерами.

Запуск из папки game_project:  .venv/bin/python tools/make_cistern.py
"""
import json
import os

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
T = 48
OUT = "assets/town/props"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "assets", "fonts", "DejaVuSans-Bold.ttf")
W = 18                                            # толщина магистральной трубы, px
DARK, MID, LIGHT, HI = (64, 68, 74), (104, 110, 116), (138, 144, 150), (176, 182, 186)
RUST, RUST_D = (150, 86, 46), (112, 60, 34)
SHADOW = (0, 0, 0, 70)
INK = (38, 34, 30)


def canvas(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def text(surf, s, size, color, center=None, topleft=None):
    f = pygame.font.Font(FONT, size)
    t = f.render(s, False, color)
    if center:
        surf.blit(t, t.get_rect(center=center))
    else:
        surf.blit(t, topleft)
    return t


def fit_text(surf, s, size, color, box, center_y):
    """Строка, вписанная в ширину box (box — (x0, x1)): шрифт уменьшается, пока не влезет."""
    while size > 4:
        f = pygame.font.Font(FONT, size)
        t = f.render(s, False, color)
        if t.get_width() <= box[1] - box[0]:
            surf.blit(t, t.get_rect(center=((box[0] + box[1]) // 2, center_y)))
            return t
        size -= 1
    return None


def pipe_v(img, y0, y1, c, rnd):
    """Вертикальный кусок магистральной трубы от y0 до y1 (как straight() в make_pipes)."""
    pygame.draw.rect(img, SHADOW, (c + 4, y0, W, y1 - y0))
    pygame.draw.rect(img, DARK, (c, y0, W, y1 - y0))
    pygame.draw.rect(img, MID, (c + 2, y0, W - 4, y1 - y0))
    pygame.draw.rect(img, LIGHT, (c + 3, y0, 3, y1 - y0))
    pygame.draw.rect(img, HI, (c + 4, y0, 1, y1 - y0))
    for _ in range(max(1, (y1 - y0) // 26)):
        ry = rnd.randrange(y0, max(y0 + 1, y1 - 8))
        pygame.draw.rect(img, RUST, (c + 6, ry, rnd.randint(3, 5), rnd.randint(4, 8)))
        pygame.draw.rect(img, RUST_D, (c + W - 4, ry + 1, 2, 3))


def flange_v(img, at, c):
    """Фланец поперёк вертикальной трубы."""
    pygame.draw.rect(img, DARK, (c - 3, at - 3, W + 6, 6))
    pygame.draw.rect(img, LIGHT, (c - 2, at - 2, W + 4, 2))
    for bx in (c - 1, c + W - 1):
        img.set_at((bx, at), HI)


def riser(seed):
    """Труба входит в потолок: снизу вверх, два фланца, у верха — тёмная обойма в перекрытии."""
    import random
    rnd = random.Random(seed)
    img = canvas(T, 120)
    c = (T - W) // 2
    pipe_v(img, 16, 120, c, rnd)
    flange_v(img, 52, c)
    flange_v(img, 92, c)
    pygame.draw.rect(img, DARK, (c - 5, 60, W + 10, 4))                 # хомут крепления к стене
    for bx in (c - 4, c + W + 2):
        pygame.draw.rect(img, HI, (bx, 61, 2, 2))
    pygame.draw.ellipse(img, (22, 22, 24), (c - 8, 2, W + 16, 16))      # перекрытие: обойма
    pygame.draw.ellipse(img, (58, 62, 66), (c - 8, 2, W + 16, 16), 2)
    pygame.draw.ellipse(img, (12, 12, 14), (c - 2, 5, W + 4, 9))
    return img


def drop(seed):
    """Труба выходит из потолка и сливает воду: открытый раструб внизу, струя до пола."""
    import random
    rnd = random.Random(seed)
    img = canvas(T, 120)
    c = (T - W) // 2
    pipe_v(img, 12, 92, c, rnd)
    flange_v(img, 44, c)
    pygame.draw.ellipse(img, (22, 22, 24), (c - 8, 0, W + 16, 14))
    pygame.draw.ellipse(img, (58, 62, 66), (c - 8, 0, W + 16, 14), 2)
    pygame.draw.rect(img, DARK, (c - 4, 88, W + 8, 8))                  # раструб
    pygame.draw.rect(img, MID, (c - 2, 90, W + 4, 5))
    pygame.draw.ellipse(img, (16, 18, 20), (c - 2, 92, W + 4, 8))
    for x in range(c + 1, c + W, 3):                                    # падающая струя
        for y in range(98, 120, 4):
            img.set_at((x, y), (150, 200, 235))
            img.set_at((x + 1, y + 1), (210, 235, 250))
    return img


def pump(seed):
    """Напорный насос: литая улитка на плите, мотор позади, патрубки влево и вверх, маховик задвижки."""
    import random
    rnd = random.Random(seed)
    img = canvas(72, 72)
    pygame.draw.rect(img, (0, 0, 0, 70), (8, 64, 58, 6))
    pygame.draw.rect(img, (54, 58, 62), (4, 56, 64, 12))                # плита
    pygame.draw.rect(img, (78, 82, 88), (4, 56, 64, 3))
    pygame.draw.rect(img, (40, 44, 48), (4, 66, 64, 2))
    for x in (8, 60):                                                   # анкерные болты
        pygame.draw.rect(img, (150, 156, 160), (x, 60, 3, 3))
    pygame.draw.rect(img, (96, 102, 108), (30, 24, 26, 34))             # мотор
    pygame.draw.rect(img, (118, 124, 130), (32, 26, 22, 4))
    pygame.draw.rect(img, (66, 70, 76), (30, 40, 26, 3))
    pygame.draw.circle(img, (86, 92, 98), (43, 34), 9)                  # вентилятор мотора
    pygame.draw.circle(img, (54, 58, 62), (43, 34), 9, 2)
    pygame.draw.circle(img, (70, 74, 80), (43, 34), 3)
    pygame.draw.circle(img, (128, 134, 140), (17, 44), 15)              # улитка
    pygame.draw.circle(img, (96, 102, 108), (17, 44), 15, 2)
    pygame.draw.circle(img, (150, 156, 162), (13, 40), 11)
    pygame.draw.circle(img, (78, 84, 90), (17, 44), 4)
    pygame.draw.rect(img, (72, 78, 84), (0, 39, 8, 12))                 # патрубок на запад
    pygame.draw.rect(img, (104, 110, 116), (0, 41, 8, 8))
    pygame.draw.rect(img, (150, 156, 162), (7, 37, 3, 16))              # фланец
    pygame.draw.rect(img, (72, 78, 84), (14, 12, 12, 18))               # напорный патрубок вверх
    pygame.draw.rect(img, (104, 110, 116), (16, 12, 8, 18))
    pygame.draw.rect(img, (150, 156, 162), (12, 10, 16, 3))
    pygame.draw.circle(img, (150, 40, 34), (24, 20), 6)                 # маховик
    pygame.draw.circle(img, (200, 70, 56), (24, 20), 6, 2)
    pygame.draw.line(img, (90, 20, 18), (18, 20), (30, 20), 2)
    for _ in range(3):                                                  # ржавые пятна и подтёк
        rx, ry = rnd.randint(6, 56), rnd.randint(30, 54)
        pygame.draw.rect(img, RUST, (rx, ry, rnd.randint(3, 6), rnd.randint(2, 4)))
    pygame.draw.rect(img, (44, 48, 52), (20, 56, 6, 6))                 # лужица под насосом
    return img


def thin(seed, arms):
    """Тонкая линия дозирования (8 px, светлая сталь) с хомутами: arms — из "nsew", какие плечи есть."""
    import random
    rnd = random.Random(seed)
    img = canvas(T, T)
    w = 8
    c = (T - w) // 2
    body, edge, glint = (122, 128, 134), (74, 78, 84), (188, 194, 200)

    def seg(horizontal, a0, a1, at):
        if horizontal:
            pygame.draw.rect(img, SHADOW, (a0, at + 2, a1 - a0, w))
            pygame.draw.rect(img, edge, (a0, at, a1 - a0, w))
            pygame.draw.rect(img, body, (a0, at + 1, a1 - a0, w - 2))
            pygame.draw.rect(img, glint, (a0, at + 2, a1 - a0, 1))
        else:
            pygame.draw.rect(img, SHADOW, (at + 2, a0, w, a1 - a0))
            pygame.draw.rect(img, edge, (at, a0, w, a1 - a0))
            pygame.draw.rect(img, body, (at + 1, a0, w - 2, a1 - a0))
            pygame.draw.rect(img, glint, (at + 2, a0, 1, a1 - a0))

    if "e" in arms or "w" in arms:
        seg(True, 0 if "w" in arms else c, T if "e" in arms else c + w, c)
    if "s" in arms or "n" in arms:
        seg(False, 0 if "n" in arms else c, T if "s" in arms else c + w, c)
    if len(arms) == 2:                                                  # колено — литая муфта на стыке
        pygame.draw.rect(img, (74, 78, 84), (c - 1, c - 1, w + 2, w + 2), 2)
    for at in (14, 34):                                                 # хомуты
        if "e" in arms or "w" in arms:
            pygame.draw.rect(img, (58, 62, 66), (at, c - 2, 3, w + 4))
        if "n" in arms or "s" in arms:
            pygame.draw.rect(img, (58, 62, 66), (c - 2, at, w + 4, 3))
    for _ in range(2):
        x, y = rnd.randint(6, 38), rnd.randint(6, 38)
        img.set_at((x, y), glint)
    return img


def mug(seed):
    """Эмалированная кружка Гаса: сколотая эмаль, тёмный чай на дне."""
    img = canvas(24, 26)
    pygame.draw.ellipse(img, (0, 0, 0, 60), (4, 22, 17, 4))
    pygame.draw.circle(img, (196, 200, 202), (18, 12), 5, 2)            # ручка
    pygame.draw.rect(img, (172, 178, 182), (4, 6, 14, 17))              # корпус
    pygame.draw.rect(img, (206, 212, 214), (5, 7, 4, 15))
    pygame.draw.rect(img, (132, 138, 142), (15, 7, 3, 15))
    pygame.draw.ellipse(img, (226, 230, 232), (4, 4, 14, 5))            # венчик
    pygame.draw.ellipse(img, (96, 70, 44), (6, 5, 10, 3))               # чай
    pygame.draw.rect(img, (238, 240, 240), (8, 6, 5, 2))                # скол эмали
    pygame.draw.rect(img, (150, 156, 160), (4, 22, 14, 2))
    return img


def ashtray(seed):
    """Жестяная пепельница с окурками."""
    import random
    rnd = random.Random(seed)
    img = canvas(30, 16)
    pygame.draw.ellipse(img, (0, 0, 0, 60), (4, 11, 22, 5))
    pygame.draw.ellipse(img, (104, 110, 114), (2, 4, 26, 10))           # жестянка
    pygame.draw.ellipse(img, (150, 156, 160), (3, 5, 24, 8), 2)
    pygame.draw.ellipse(img, (74, 78, 82), (7, 7, 16, 5))               # пепел
    for x, y in ((8, 9), (12, 7), (17, 8)):                             # окурки
        pygame.draw.rect(img, (226, 222, 212), (x, y, 5, 2))
        img.set_at((x + 5, y), (198, 120, 60))
        img.set_at((x + 5, y + 1), (150, 84, 44))
        img.set_at((x - 1, y), (110, 108, 100))
    return img


def sign_cs3(seed):
    """Знак опасности на стойке: жёлтый щит, чёрный трилистник, «CS-3»."""
    img = canvas(48, 72)
    pygame.draw.rect(img, (0, 0, 0, 70), (20, 66, 14, 5))
    pygame.draw.rect(img, (88, 86, 80), (22, 40, 5, 28))                # стойка
    pygame.draw.rect(img, (120, 118, 110), (22, 40, 2, 28))
    pygame.draw.rect(img, (196, 176, 56), (4, 4, 40, 38))               # щит
    pygame.draw.rect(img, (128, 112, 30), (4, 4, 40, 38), 2)
    pygame.draw.rect(img, (24, 22, 18), (6, 6, 36, 34), 1)
    cx, cy = 24, 18
    pygame.draw.circle(img, (24, 22, 18), (cx, cy), 3)
    for k in range(3):                                                  # трилистник
        a = -90 + k * 120
        import math
        px_, py_ = cx + 9 * math.cos(math.radians(a)), cy + 9 * math.sin(math.radians(a))
        pygame.draw.circle(img, (24, 22, 18), (int(px_), int(py_)), 6)
        pygame.draw.polygon(img, (24, 22, 18), [(cx, cy),
                                                (int(cx + 11 * math.cos(math.radians(a - 27))),
                                                 int(cy + 11 * math.sin(math.radians(a - 27)))),
                                                (int(cx + 11 * math.cos(math.radians(a + 27))),
                                                 int(cy + 11 * math.sin(math.radians(a + 27))))])
    text(img, "CS-3", 11, (24, 22, 18), center=(24, 34))
    return img


def sign_step2(seed):
    """Табличка на ступени: тёмный металл, жёлтая строка «СТУПЕНЬ 2 — НЕ ОТКЛЮЧАТЬ»."""
    img = canvas(112, 26)
    pygame.draw.rect(img, (0, 0, 0, 70), (2, 23, 108, 3))
    pygame.draw.rect(img, (58, 56, 50), (0, 0, 112, 24))
    pygame.draw.rect(img, (86, 84, 76), (1, 1, 110, 22), 1)
    pygame.draw.rect(img, (36, 34, 30), (0, 23, 112, 1))
    fit_text(img, "СТУПЕНЬ 2", 11, (222, 196, 70), (5, 90), 7)
    fit_text(img, "НЕ ОТКЛЮЧАТЬ", 8, (222, 196, 70), (8, 88), 18)
    pygame.draw.rect(img, (150, 44, 36), (94, 8, 8, 10))                # красный гриб-кнопка рядом
    pygame.draw.rect(img, (196, 96, 84), (95, 9, 6, 3))
    for x, y in ((104, 4), (104, 18), (4, 20)):                         # болты
        img.set_at((x, y), (150, 148, 140))
    return img


def poster_safety(seed):
    """Довоенный плакат техники безопасности Vault-Tec: синий лист, жёлтая кайма, шестерня и рука."""
    img = canvas(80, 84)
    pygame.draw.rect(img, (0, 0, 0, 60), (3, 81, 74, 3))
    pygame.draw.rect(img, (196, 186, 158), (0, 0, 80, 82))              # бумага
    pygame.draw.rect(img, (34, 62, 96), (3, 3, 74, 76))                 # синее поле
    pygame.draw.rect(img, (196, 176, 56), (3, 3, 74, 76), 2)            # жёлтая кайма
    fit_text(img, "ТЕХНИКА", 11, (230, 226, 210), (6, 74), 15)
    fit_text(img, "БЕЗОПАСНОСТИ", 8, (230, 226, 210), (6, 74), 29)
    import math
    cx, cy = 40, 52
    for k in range(8):                                                  # шестерня
        a = k * 45
        x = cx + 11 * math.cos(math.radians(a))
        y = cy + 11 * math.sin(math.radians(a))
        pygame.draw.rect(img, (206, 186, 76), (int(x) - 2, int(y) - 2, 4, 4))
    pygame.draw.circle(img, (206, 186, 76), (cx, cy), 10)
    pygame.draw.circle(img, (34, 62, 96), (cx, cy), 4)
    pygame.draw.polygon(img, (222, 196, 170), [(cx + 12, cy - 4), (cx + 21, cy),
                                               (cx + 16, cy + 7), (cx + 8, cy + 2)])
    fit_text(img, "РУКИ ПРОЧЬ", 9, (222, 196, 170), (6, 74), 70)
    return img


def seal(seed):
    """Пломба на дверце: свинцовая шайба на витой проволоке."""
    img = canvas(20, 20)
    pygame.draw.line(img, (170, 174, 178), (4, 3), (16, 9), 1)
    pygame.draw.line(img, (206, 210, 214), (5, 4), (15, 8), 1)
    pygame.draw.circle(img, (0, 0, 0, 60), (11, 14), 6)
    pygame.draw.circle(img, (128, 130, 132), (10, 12), 6)
    pygame.draw.circle(img, (172, 176, 178), (9, 11), 4)
    pygame.draw.line(img, (86, 88, 90), (7, 12), (12, 12), 1)
    return img



def catwalk(seed):
    """Стальной настил мостка через канал: рифлёная плита с решёткой, рама и ржавые пятна."""
    import random
    rnd = random.Random(seed)
    img = canvas(96, 48)
    for i in range(2):                                                  # две плиты по клетке
        x0 = i * 48
        pygame.draw.rect(img, (0, 0, 0, 80), (x0 + 2, 44, 44, 4))
        pygame.draw.rect(img, (66, 70, 74), (x0 + 1, 6, 46, 38))        # рама
        pygame.draw.rect(img, (96, 100, 104), (x0 + 1, 6, 46, 2))
        pygame.draw.rect(img, (46, 50, 54), (x0 + 1, 42, 46, 2))
        for gy in range(10, 40, 5):                                     # решётка
            pygame.draw.line(img, (124, 128, 132), (x0 + 3, gy + 1), (x0 + 45, gy + 1))
            pygame.draw.line(img, (54, 58, 62), (x0 + 3, gy + 2), (x0 + 45, gy + 2))
        for gx in range(8, 46, 6):                                      # поперечные прутья
            pygame.draw.line(img, (110, 114, 118), (x0 + gx, 9), (x0 + gx, 41))
        for _ in range(3):                                              # ржавчина на настиле
            rx, ry = x0 + rnd.randint(4, 38), rnd.randint(10, 36)
            pygame.draw.rect(img, RUST, (rx, ry, rnd.randint(3, 6), 2))
        for bx in (x0 + 4, x0 + 42):                                    # болты по углам
            pygame.draw.rect(img, (150, 154, 158), (bx, 8, 2, 2))
            pygame.draw.rect(img, (150, 154, 158), (bx, 38, 2, 2))
    return img


def tally(seed):
    """Засечки ремонтов на стене: девять групп по пять и одна свежая, ржаво-красная."""
    img = canvas(48, 48)
    import random
    rnd = random.Random(seed)
    cols = [(150, 146, 132), (138, 134, 120)]
    n = 0
    for gx in range(2, 46, 10):                                        # группы по пятёрке
        for k in range(5):
            x = gx + k * 2
            col = cols[(n + k) % 2]
            pygame.draw.line(img, col, (x, 6), (x + 1, 16), 1)
        pygame.draw.line(img, cols[n % 2], (gx - 1, 8), (gx + 8, 14), 1)
        n += 1
    for k in range(2):                                                 # нижний ряд
        x = 4 + k * 12
        pygame.draw.line(img, cols[k], (x, 24), (x, 34), 1)
        pygame.draw.line(img, cols[k], (x + 3, 24), (x + 3, 34), 1)
    pygame.draw.line(img, (168, 74, 52), (30, 24), (31, 35), 2)         # свежая, ржаво-красная
    pygame.draw.line(img, (150, 66, 46), (33, 23), (34, 34), 2)
    pygame.draw.rect(img, (60, 56, 48), (6, 20, 30, 1))                 # царапины-риски
    return img


def toolboard(seed):
    """Доска с инструментом на стене: перфорированная панель, ключ, молоток, отвёртка, крюк."""
    img = canvas(72, 60)
    pygame.draw.rect(img, (0, 0, 0, 60), (2, 57, 68, 3))
    pygame.draw.rect(img, (88, 92, 94), (0, 0, 72, 58))                 # панель
    pygame.draw.rect(img, (60, 64, 66), (0, 0, 72, 58), 2)
    for x in range(6, 68, 6):                                           # перфорация
        for y in range(6, 54, 6):
            img.set_at((x, y), (54, 58, 60))
    pygame.draw.rect(img, (126, 130, 132), (8, 10, 3, 34))              # газовый ключ
    pygame.draw.rect(img, (96, 100, 102), (7, 8, 5, 6))
    pygame.draw.rect(img, (96, 100, 102), (7, 40, 5, 5))
    pygame.draw.rect(img, (120, 88, 54), (22, 22, 3, 26))               # рукоять молотка
    pygame.draw.rect(img, (78, 82, 86), (18, 12, 12, 8))                # боёк
    pygame.draw.rect(img, (110, 114, 118), (19, 13, 10, 2))
    pygame.draw.rect(img, (188, 186, 176), (40, 14, 2, 18))             # отвёртка
    pygame.draw.rect(img, (150, 40, 34), (39, 32, 4, 8))
    pygame.draw.rect(img, (150, 156, 160), (50, 12, 3, 20))             # крюк с цепью
    pygame.draw.arc(img, (150, 156, 160), (48, 30, 10, 10), 3.3, 6.0, 2)
    pygame.draw.rect(img, (96, 76, 48), (60, 16, 6, 22))                # кожаный ремень
    pygame.draw.rect(img, (70, 54, 34), (60, 24, 6, 3))
    return img

PROPS = {
    "zz_pump": (pump, 72, 72),
    "zz_pipe_riser": (riser, 48, 120),
    "zz_pipe_drop": (drop, 48, 120),
    "zz_pipe_thin_h": (lambda s: thin(s, "ew"), 48, 48),
    "zz_pipe_thin_v": (lambda s: thin(s, "ns"), 48, 48),
    "zz_pipe_thin_ne": (lambda s: thin(s, "ne"), 48, 48),
    "zz_pipe_thin_nw": (lambda s: thin(s, "nw"), 48, 48),
    "zz_pipe_thin_sw": (lambda s: thin(s, "sw"), 48, 48),
    "zz_pipe_thin_se": (lambda s: thin(s, "se"), 48, 48),
    "zz_mug": (mug, 24, 26),
    "zz_ashtray": (ashtray, 30, 16),
    "zz_sign_cs3": (sign_cs3, 48, 72),
    "zz_sign_step2": (sign_step2, 112, 26),
    "zz_poster_safety": (poster_safety, 80, 84),
    "zz_seal": (seal, 20, 20),
    "zz_catwalk": (catwalk, 96, 48),
    "zz_tally": (tally, 48, 48),
    "zz_toolboard": (toolboard, 72, 60),
}


def main():
    idx_path = os.path.join("assets", "town", "index.json")
    with open(idx_path, encoding="utf-8") as f:
        index = json.load(f)
    for i, (name, (draw, w, h)) in enumerate(PROPS.items()):
        img = draw(41 + i)
        assert img.get_size() == (w, h), (name, img.get_size())
        pygame.image.save(img, os.path.join(OUT, name + ".png"))
        index[name] = {"size": [w, h], "made_by": "tools/make_cistern.py"}
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print("нарисовано:", ", ".join(PROPS))


if __name__ == "__main__":
    main()
