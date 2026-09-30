"""
Картинки для слайдов пролога: рисуются процедурно, потом тонируются в
янтарь, как старый диапроектор (зерно, царапины, виньетка).

Любую картинку можно заменить своей: assets/slides/<имя>.png — тогда
берётся она (тонировка остаётся, чтобы стиль был единым).
"""
import math
import os
import random

import pygame

from .. import fonts as fontlib

W, H = 880, 380
_CACHE = {}


def _sky(s, top, bottom):
    for y in range(H):
        t = y / H
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, c, (0, y), (W, y))


def _skyline(s, rnd, base_y, color, ruined=False):
    x = 0
    while x < W:
        bw, bh = rnd.randint(30, 80), rnd.randint(40, 170)
        if ruined:
            pts = [(x, base_y), (x, base_y - bh)]
            for i in range(1, 4):
                pts.append((x + bw * i // 4, base_y - bh + rnd.randint(-10, 50)))
            pts += [(x + bw, base_y - bh + rnd.randint(0, 60)), (x + bw, base_y)]
            pygame.draw.polygon(s, color, pts)
        else:
            pygame.draw.rect(s, color, (x, base_y - bh, bw, bh))
            for wy in range(base_y - bh + 8, base_y - 6, 14):  # окна
                for wx in range(x + 6, x + bw - 6, 12):
                    if rnd.random() < 0.3:
                        pygame.draw.rect(s, (230, 220, 160), (wx, wy, 4, 6))
        x += bw + rnd.randint(0, 12)
    pygame.draw.rect(s, color, (0, base_y, W, H - base_y))


def _mushroom(s, cx, base_y, size, glow=True):
    """Ядерный гриб: ножка и шапка из кругов."""
    if glow:
        g = pygame.Surface((W, H), pygame.SRCALPHA)
        for r in range(int(size * 2.4), 0, -12):
            pygame.draw.circle(g, (255, 230, 170, 10), (cx, base_y - size * 1.4), r)
        s.blit(g, (0, 0))
    stem_top = base_y - size * 1.3
    pygame.draw.polygon(s, (190, 170, 150), [(cx - size * 0.12, base_y), (cx - size * 0.2, stem_top),
                                             (cx + size * 0.2, stem_top), (cx + size * 0.12, base_y)])
    for i in range(3):
        pygame.draw.ellipse(s, (215, 200, 180), (cx - size * 0.35, stem_top + i * size * 0.3 - 10, size * 0.7, size * 0.18))
    rnd = random.Random(cx)
    for _ in range(26):  # клубящаяся шапка
        a = rnd.uniform(0, math.tau)
        rr = rnd.uniform(0, size * 0.55)
        x, y = cx + math.cos(a) * rr * 1.3, stem_top - size * 0.35 + math.sin(a) * rr * 0.55
        pygame.draw.circle(s, (rnd.randint(215, 250), rnd.randint(200, 235), rnd.randint(170, 210)), (x, y),
                           rnd.randint(int(size * 0.18), int(size * 0.3)))
    pygame.draw.ellipse(s, (240, 230, 210), (cx - size * 0.5, stem_top - size * 0.55, size, size * 0.35))
    pygame.draw.ellipse(s, (170, 150, 130), (cx - size * 0.9, base_y - size * 0.18, size * 1.8, size * 0.3))


def art_war(s, rnd, game):
    _sky(s, (40, 30, 30), (160, 110, 70))
    _mushroom(s, W // 2, H - 90, 170)
    _skyline(s, rnd, H - 60, (25, 20, 18))


def art_alaska(s, rnd, game):
    _sky(s, (150, 160, 170), (220, 225, 230))
    for i in range(6):  # горы
        x = i * 180 - 60
        pygame.draw.polygon(s, (120, 130, 140), [(x, H - 90), (x + 110, 60 + rnd.randint(0, 60)), (x + 240, H - 90)])
        pygame.draw.polygon(s, (240, 245, 250), [(x + 80, 110), (x + 110, 60 + 10), (x + 140, 110)])
    pygame.draw.rect(s, (230, 235, 240), (0, H - 100, W, 100))
    # силуэт силовой брони Т-51 — шлем, наплечники, корпус
    cx, by = W // 2 + 120, H - 20
    dark = (40, 44, 48)
    pygame.draw.rect(s, dark, (cx - 70, by - 210, 140, 170), border_radius=26)       # корпус
    pygame.draw.ellipse(s, dark, (cx - 115, by - 225, 90, 70))                        # наплечники
    pygame.draw.ellipse(s, dark, (cx + 25, by - 225, 90, 70))
    pygame.draw.rect(s, dark, (cx - 45, by - 300, 90, 90), border_radius=30)         # шлем
    for i in range(3):
        pygame.draw.rect(s, (200, 190, 150), (cx - 30, by - 268 + i * 12, 60, 6), border_radius=2)  # визор
    pygame.draw.rect(s, dark, (cx - 60, by - 45, 50, 45))
    pygame.draw.rect(s, dark, (cx + 10, by - 45, 50, 45))
    for _ in range(220):  # снег
        pygame.draw.circle(s, (255, 255, 255), (rnd.randrange(W), rnd.randrange(H)), rnd.choice((1, 1, 2)))


def art_mariposa(s, rnd, game):
    _sky(s, (30, 30, 36), (80, 70, 60))
    pygame.draw.rect(s, (60, 55, 50), (0, H // 2, W, H // 2))
    # подземный разрез с чанами — зеленоватое свечение
    pygame.draw.rect(s, (25, 30, 25), (80, H // 2 + 40, W - 160, H // 2 - 50))
    for i in range(4):
        x = 150 + i * 170
        glow = pygame.Surface((140, 140), pygame.SRCALPHA)
        pygame.draw.circle(glow, (120, 255, 140, 60), (70, 70), 70)
        s.blit(glow, (x - 45, H // 2 + 60))
        pygame.draw.rect(s, (90, 110, 95), (x - 25, H // 2 + 80, 50, 90), border_radius=10)
        pygame.draw.rect(s, (160, 240, 170), (x - 18, H // 2 + 95, 36, 55), border_radius=6)
    # база наверху: вышка, забор, ангар
    pygame.draw.rect(s, (40, 38, 36), (560, H // 2 - 70, 220, 70))
    pygame.draw.ellipse(s, (40, 38, 36), (560, H // 2 - 110, 220, 80))
    pygame.draw.rect(s, (35, 33, 30), (140, H // 2 - 150, 16, 150))
    pygame.draw.rect(s, (35, 33, 30), (110, H // 2 - 175, 76, 34))
    pygame.draw.polygon(s, (255, 250, 200), [(148, H // 2 - 160), (330, H // 2 - 40), (260, H // 2 - 20)])  # прожектор
    for x in range(0, W, 26):
        pygame.draw.line(s, (30, 28, 26), (x, H // 2 - 34), (x, H // 2), 2)
    pygame.draw.line(s, (30, 28, 26), (0, H // 2 - 30), (W, H // 2 - 30), 2)
    pygame.draw.line(s, (30, 28, 26), (0, H // 2 - 14), (W, H // 2 - 14), 2)


def art_bombs(s, rnd, game):
    _sky(s, (60, 30, 20), (230, 150, 80))
    for cx, size in ((140, 70), (330, 110), (560, 90), (760, 60)):
        _mushroom(s, cx, H - 70, size, glow=True)
    pygame.draw.rect(s, (40, 25, 20), (0, H - 70, W, 70))
    for x in range(0, W, 3):  # горизонт — пустыня
        pygame.draw.line(s, (60, 40, 30), (x, H - 70), (x, H - 70 + rnd.randint(0, 8)))


def art_vault(s, rnd, game):
    _sky(s, (30, 30, 34), (60, 58, 56))
    cx, cy, r = W // 2, H // 2 + 10, 150
    pygame.draw.circle(s, (50, 50, 55), (cx, cy), r + 30)
    teeth = 16
    for i in range(teeth):  # шестерня двери убежища
        a = i / teeth * math.tau
        x, y = cx + math.cos(a) * (r + 8), cy + math.sin(a) * (r + 8)
        pygame.draw.circle(s, (160, 150, 120), (x, y), 22)
    pygame.draw.circle(s, (170, 160, 130), (cx, cy), r)
    pygame.draw.circle(s, (140, 130, 105), (cx, cy), r - 24)
    pygame.draw.circle(s, (170, 160, 130), (cx, cy), r - 60)
    font = fontlib.get("dejavusans", 110, bold=True)
    t = font.render("57", True, (60, 55, 45))
    s.blit(t, t.get_rect(center=(cx, cy)))
    for i in range(6):
        a = i / 6 * math.tau + 0.3
        pygame.draw.line(s, (120, 110, 90), (cx + math.cos(a) * (r - 60), cy + math.sin(a) * (r - 60)),
                         (cx + math.cos(a) * (r - 24), cy + math.sin(a) * (r - 24)), 6)


def art_first_years(s, rnd, game):
    _sky(s, (110, 80, 50), (190, 150, 100))
    for _ in range(40):  # пылевая буря
        y = rnd.randrange(H)
        pygame.draw.line(s, (210, 180, 130), (rnd.randrange(W), y), (rnd.randrange(W), y + rnd.randint(-6, 6)), 1)
    _skyline(s, rnd, H - 110, (80, 60, 45), ruined=True)
    pygame.draw.rect(s, (70, 55, 40), (0, H - 110, W, 110))
    # костёр и люди у огня
    fx, fy = W // 2, H - 50
    g = pygame.Surface((240, 160), pygame.SRCALPHA)
    pygame.draw.ellipse(g, (255, 200, 120, 70), g.get_rect())
    s.blit(g, (fx - 120, fy - 100))
    pygame.draw.polygon(s, (255, 220, 140), [(fx - 16, fy), (fx, fy - 44), (fx + 16, fy)])
    for dx in (-110, -60, 70, 120):
        pygame.draw.ellipse(s, (30, 24, 20), (fx + dx - 16, fy - 70, 32, 36))
        pygame.draw.rect(s, (30, 24, 20), (fx + dx - 20, fy - 40, 40, 44), border_radius=8)


def art_letter(s, rnd, game):
    s.fill((60, 45, 30))
    paper = pygame.Rect(W // 2 - 230, 30, 460, H - 50)
    pygame.draw.rect(s, (20, 15, 10), paper.move(8, 8))
    pygame.draw.rect(s, (225, 210, 170), paper)
    font = fontlib.get("dejavuserif", 24, italic=True)
    lines = ["Внук.", "", "Приезжай в Пятнадцатую.", "Есть разговор, который", "я откладывал", "сорок четыре года.",
             "", "Твой дед, сержант Э. Рид"]
    y = paper.y + 30
    for line in lines:
        s.blit(font.render(line, True, (60, 45, 30)), (paper.x + 40, y))
        y += 34


def art_arrival(s, rnd, game):
    if game is not None:  # настоящий въезд в город — кусок карты
        lvl = game.level
        cam = pygame.Vector2(0, 31 * 48 - H // 2 - 40)
        view = pygame.Surface((W, H))
        view.fill((20, 17, 14))
        lvl.draw(view, cam)
        for y, img, pos in sorted(lvl.drawables(cam), key=lambda i: i[0]):
            view.blit(img, pos)
        s.blit(view, (0, 0))
        frame = game.player.anim.frames_by_action.get("idle_right", [None])[0]
        if frame is not None:
            big = pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2))
            s.blit(big, big.get_rect(midbottom=(160, H - 150)))
        return
    _sky(s, (120, 90, 60), (200, 160, 110))


def art_baker(s, rnd, game):
    _sky(s, (70, 40, 40), (220, 140, 80))
    pygame.draw.rect(s, (90, 60, 40), (0, H - 80, W, 80))
    # Термометр: высокий столб со шкалой
    x = W // 2 + 140
    pygame.draw.rect(s, (40, 30, 26), (x - 26, 20, 52, H - 90), border_radius=12)
    pygame.draw.rect(s, (230, 225, 200), (x - 16, 36, 32, H - 120), border_radius=8)
    for y in range(50, H - 100, 16):
        pygame.draw.line(s, (60, 50, 40), (x - 16, y), (x - 6, y), 2)
    pygame.draw.rect(s, (200, 50, 40), (x - 6, 150, 12, H - 240))
    pygame.draw.circle(s, (200, 50, 40), (x, H - 80), 20)
    # шатры миссии у подножия
    for i, tx in enumerate((x - 330, x - 240, x - 150)):
        pygame.draw.polygon(s, (235, 225, 205), [(tx - 50, H - 80), (tx, H - 150 - i * 6), (tx + 50, H - 80)])
        pygame.draw.polygon(s, (190, 175, 150), [(tx, H - 150 - i * 6), (tx + 50, H - 80), (tx + 10, H - 80)])


def art_barstow(s, rnd, game):
    _sky(s, (40, 26, 44), (170, 90, 70))
    _skyline(s, rnd, H - 120, (30, 24, 26), ruined=True)
    pygame.draw.rect(s, (70, 56, 44), (0, H - 120, W, 120))
    for x in range(0, W, 26):   # рельсы и шпалы
        pygame.draw.rect(s, (90, 70, 50), (x, H - 70, 14, 20))
    pygame.draw.line(s, (170, 170, 160), (0, H - 64), (W, H - 64), 3)
    pygame.draw.line(s, (170, 170, 160), (0, H - 56), (W, H - 56), 3)
    font = pygame.font.Font(None, 56)
    for text, pos, col in (("MOTEL", (120, H - 250), (255, 90, 190)), ("МИРАЖ", (W - 330, H - 290), (255, 70, 150))):
        glow = font.render(text, True, col)
        for d in (-3, 3):
            g = glow.copy()
            g.set_alpha(70)
            s.blit(g, (pos[0] + d, pos[1] + d))
        s.blit(glow, pos)
    if game is not None:   # Дэкс — выживший с винтовкой
        try:
            from ..iso import load_char
            frames, _ = load_char("hero")
            f = frames["idle_se"][0]
            big = pygame.transform.smoothscale(f, (f.get_width() * 2, f.get_height() * 2))
            s.blit(big, big.get_rect(midbottom=(W // 2, H - 40)))
        except (OSError, KeyError, pygame.error):
            pass


ARTS = {"barstow": art_barstow, "war": art_war, "alaska": art_alaska, "mariposa": art_mariposa, "bombs": art_bombs, "vault": art_vault,
        "first_years": art_first_years, "letter": art_letter, "arrival": art_arrival, "baker": art_baker}


def _tint(img):
    """Янтарная тонировка + зерно + царапины + виньетка — стиль старого слайда."""
    g = pygame.transform.grayscale(img)
    g.fill((255, 205, 130), special_flags=pygame.BLEND_RGB_MULT)
    rnd = random.Random(7)
    grain = pygame.Surface(g.get_size(), pygame.SRCALPHA)
    for _ in range(W * H // 40):
        v = rnd.randint(0, 60)
        grain.set_at((rnd.randrange(W), rnd.randrange(H)), (v, v // 2, 0, 50))
    for _ in range(5):  # царапины на плёнке
        x = rnd.randrange(W)
        pygame.draw.line(grain, (255, 230, 180, 40), (x, 0), (x + rnd.randint(-6, 6), H), 1)
    g.blit(grain, (0, 0))
    vig = pygame.Surface(g.get_size(), pygame.SRCALPHA)
    for i in range(40):
        pygame.draw.rect(vig, (0, 0, 0, 7), (i * 3, i * 2, W - i * 6, H - i * 4), 4, border_radius=30)
    g.blit(vig, (0, 0))
    return g


def slide_image(name, game=None):
    if name not in _CACHE:
        s = pygame.Surface((W, H))
        path = os.path.join("assets", "slides", f"{name}.png")
        if os.path.isfile(path):
            s.blit(pygame.transform.smoothscale(pygame.image.load(path).convert(), (W, H)), (0, 0))
        else:
            ARTS.get(name, art_war)(s, random.Random(hash(name) & 0xFFFF), game)
        _CACHE[name] = _tint(s)
    return _CACHE[name]
