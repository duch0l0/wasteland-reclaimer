"""
Свои плоские тайлы улиц для изометрии (Барстоу): плитка тротуара, бордюр и асфальт с трещинами.
Родные тайлы тротуара набора — толстые кубики со случайным поворотом, из них выходит мозаика «куча кирпичей».
Здесь плиты ровные, швы тонкие, бордюр — светлая полоса с тенью и вертикальной гранью.

  x_walk_0..3        тротуар
  x_curb_<сторона>   тротуар с бордюром со стороны дороги: e (+x), w (-x), s (+y), n (-y)
  x_asph_0..3        асфальт: зерно, трещины, пятна масла, латки

Запуск из папки game_project:  .venv/bin/python tools/make_iso_street.py
"""
import math
import os
import random

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
OUT = "assets/iso/tiles"
CX, CY = 64, 207            # центр ромба в тайле 128×256
SIDE = {"e": (1, 0), "w": (-1, 0), "s": (0, 1), "n": (0, -1)}


def uv(px, py):
    dx, dy = (px - CX) / 64, (py - CY) / 32
    return (dx + dy) / 2, (dy - dx) / 2        # u вдоль +x клетки, v вдоль +y; в ромбе |u|,|v| ≤ 0.5


def inside(px, py):
    return abs(px - CX) / 64 + abs(py - CY) / 32 <= 1.0


def walk(seed, curb=None):
    rnd = random.Random(seed)
    img = pygame.Surface((128, 256), pygame.SRCALPHA)
    slab = {}
    for a in (0, 1):
        for b in (0, 1):
            slab[(a, b)] = rnd.uniform(0.93, 1.07)
    cracks = []
    for _ in range(rnd.choice((0, 1, 1, 2))):
        u, v = rnd.uniform(-0.45, 0.45), rnd.uniform(-0.45, 0.45)
        pts = [(u, v)]
        ang = rnd.uniform(0, 6.28)
        for _ in range(5):
            ang += rnd.uniform(-0.8, 0.8)
            u += math.cos(ang) * 0.08
            v += math.sin(ang) * 0.08
            pts.append((u, v))
        cracks.append(pts)
    for py in range(CY - 34, CY + 34):
        for px in range(128):
            if not inside(px, py):
                continue
            u, v = uv(px, py)
            k = slab[(int(u >= 0), int(v >= 0))]
            n = rnd.uniform(0.95, 1.05)
            base = 98 * k * n
            col = [base * 1.04, base * 0.99, base * 0.90]
            # швы между плитами 2×2: тонкие, с бликом с одной стороны
            du, dv = abs(u), abs(v)
            if du < 0.016 or dv < 0.016:
                col = [c * 0.55 for c in col]
            elif u > 0 and u < 0.034 or v > 0 and v < 0.034:
                col = [c * 1.1 for c in col]
            if curb:
                sx, sy = SIDE[curb]
                d = 0.5 - (u * sx + v * sy)          # расстояние до края со стороны дороги, 0..1
                if d < 0.035:
                    col = [c * 0.42 for c in col]     # тёмная кромка у асфальта
                elif d < 0.17:
                    col = [c * 1.15 for c in col]     # верх бордюра светлее
                elif d < 0.2:
                    col = [c * 0.62 for c in col]     # линия между бордюром и плитой
            img.set_at((px, py), tuple(min(255, int(c)) for c in col) + (255,))
    for pts in cracks:
        for (u1, v1), (u2, v2) in zip(pts, pts[1:]):
            p1 = (CX + (u1 - v1) * 64, CY + (u1 + v1) * 32)
            p2 = (CX + (u2 - v2) * 64, CY + (u2 + v2) * 32)
            pygame.draw.line(img, (44, 40, 36, 255), p1, p2)
    if curb in ("e", "s"):                         # вертикальная грань бордюра, видная зрителю
        for step in range(5):
            shade = 0.5 - step * 0.05
            for px in range(128):
                for py in range(CY - 34, CY + 34):
                    if inside(px, py) and not inside(px, py + 1):
                        u, v = uv(px, py)
                        sx, sy = SIDE[curb]
                        if 0.5 - (u * sx + v * sy) < 0.06:
                            c = img.get_at((px, py))
                            img.set_at((px, py + 1 + step), (int(115 * shade * 1.6), int(110 * shade * 1.6), int(100 * shade * 1.6), 255))
    return img


def asphalt(seed):
    rnd = random.Random(seed)
    img = pygame.Surface((128, 256), pygame.SRCALPHA)
    spots = [(rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), rnd.uniform(0.05, 0.14), rnd.choice((0.8, 0.8, 1.25))) for _ in range(rnd.choice((1, 2, 3)))]
    cracks = []
    for _ in range(rnd.choice((0, 1, 2))):
        u, v = rnd.uniform(-0.45, 0.45), rnd.uniform(-0.45, 0.45)
        ang, pts = rnd.uniform(0, 6.28), [(u, v)]
        for _ in range(7):
            ang += rnd.uniform(-0.7, 0.7)
            u += math.cos(ang) * 0.09
            v += math.sin(ang) * 0.09
            pts.append((u, v))
        cracks.append(pts)
    for py in range(CY - 34, CY + 34):
        for px in range(128):
            if not inside(px, py):
                continue
            u, v = uv(px, py)
            b = 34 * rnd.uniform(0.9, 1.1)
            for su, sv, r, k in spots:
                if (u - su) ** 2 + (v - sv) ** 2 < r * r:
                    b *= k
            img.set_at((px, py), (int(b), int(b), int(b * 1.04), 255))
    for pts in cracks:
        for (u1, v1), (u2, v2) in zip(pts, pts[1:]):
            pygame.draw.line(img, (12, 12, 13, 255), (CX + (u1 - v1) * 64, CY + (u1 + v1) * 32), (CX + (u2 - v2) * 64, CY + (u2 + v2) * 32))
    return img


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i in range(4):
        pygame.image.save(walk(i), f"{OUT}/x_walk_{i}.png")
        pygame.image.save(asphalt(10 + i), f"{OUT}/x_asph_{i}.png")
    for i, s in enumerate(SIDE):
        pygame.image.save(walk(20 + i, s), f"{OUT}/x_curb_{s}.png")
    print("нарисовано: 12 тайлов")
