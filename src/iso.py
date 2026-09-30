"""
Изометрическая проекция, как в Fallout.

Игровой мир (клетки, пути, бой, столкновения) остаётся прежним: клетка S.TILE×S.TILE
«логических» пикселей. Меняется только то, как он ложится на экран:

    клетка (u, v)  ->  ромб 128×64 на экране:  x = (u − v)·64,  y = (u + v)·32

Камера (Camera) переводит точку мира в точку холста и обратно — одинаково для
изометрических карт и старых прямых (там это просто сдвиг). Весь код отрисовки
и мыши спрашивает положение у камеры: cam.p(wx, wy) / cam.inv(sx, sy).
"""
import json
import math
import os

import pygame

from . import settings as S
from .animator import Animator

HW, HH = 64, 32          # половина ромба клетки на экране (тайлы набора — 128×64)
T = S.TILE


def w2i(wx, wy):
    """Точка мира (логические пиксели) -> точка изометрического пространства."""
    u, v = wx / T, wy / T
    return (u - v) * HW, (u + v) * HH


def i2w(ix, iy):
    """Обратно: точка на земле изометрического пространства -> точка мира."""
    a, b = ix / HW, iy / HH
    return (a + b) / 2 * T, (b - a) / 2 * T


def tile_center_iso(tx, ty):
    return w2i((tx + 0.5) * T, (ty + 0.5) * T)


class Camera:
    """Левый верхний угол видимой области в пространстве отрисовки (прямом или изометрическом)."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.iso = False

    def p(self, wx, wy):
        """Мир -> холст."""
        if self.iso:
            ix, iy = w2i(wx, wy)
            return ix - self.x, iy - self.y
        return wx - self.x, wy - self.y

    def inv(self, sx, sy):
        """Холст -> мир (на уровне земли)."""
        if self.iso:
            return i2w(sx + self.x, sy + self.y)
        return sx + self.x, sy + self.y

    def foot(self, ent):
        """Где на холсте стоят ноги персонажа: в изометрии — центр его клетки."""
        if self.iso:
            return self.p(ent.rect.centerx, ent.rect.bottom - T // 2 + 2)
        return self.p(ent.rect.centerx, ent.rect.bottom)


# ------------------------------------------------------------ 8 направлений
DIR8 = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]


def screen_dir(dx, dy):
    """Направление на экране (одно из 8) для шага (dx, dy) в мире."""
    sx, sy = (dx - dy) * HW, (dx + dy) * HH
    a = math.degrees(math.atan2(sy, sx)) % 360
    return DIR8[int((a + 22.5) // 45) % 8]


def input_to_world(sx, sy):
    """Направление с клавиш (вправо/вверх по экрану) -> направление в мире."""
    du = (sx / HW + sy / HH) / 2
    dv = (sy / HH - sx / HW) / 2
    n = math.hypot(du, dv)
    return (du / n, dv / n) if n else (0.0, 0.0)


class IsoAnimator(Animator):
    """Анимации в 8 направлениях (кадры из tools/slice_iso.py): action_s, action_ne..."""

    def __init__(self, frames_by_action, foot, frame_ms=S.ANIM_FRAME_MS):
        super().__init__(frames_by_action, frame_ms)
        self.direction = "s"
        self.directional = True
        self.foot = foot          # где в кадре ноги

    def face(self, dx, dy):
        if dx or dy:
            self.direction = screen_dir(dx, dy)

    def current_frame(self, flip=False):
        frames = self.frames()
        return frames[self.index % len(frames)]


# Набор нарисован тёмным (ночной зомби-город); пустошь — днём под солнцем.
TILE_GAIN, TILE_WARM = 1.45, (10, 6, 0)      # тайлы: светлее и чуть теплее
CHAR_GAIN = 1.55                             # персонажи ещё светлее, чтобы не сливались с землёй
OUTLINE = (18, 14, 12, 230)                  # тонкий тёмный контур вокруг персонажа


def brighten(img, gain, warm=(0, 0, 0)):
    """Осветлить картинку: + (gain − 1) её же цвета, + тёплый оттенок; прозрачность не трогаем."""
    out = img.copy()
    extra = img.copy()
    k = int(255 * (gain - 1))
    extra.fill((k, k, k, 255), special_flags=pygame.BLEND_RGBA_MULT)
    out.blit(extra, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    if any(warm):
        tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        tint.fill((*warm, 0))
        out.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return out


def outlined(img):
    """Персонаж с контуром в 1 пиксель — читается на пёстрой земле, как в Fallout."""
    mask = pygame.mask.from_surface(img, 110)
    sil = mask.to_surface(setcolor=OUTLINE, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(sil, (dx, dy))
    out.blit(img, (0, 0))
    return out


_CHAR_CACHE = {}


def load_char(cid):
    """Кадры изометрического персонажа: {'walk_se': [...], ..., 'idle': [...]}, точка ног."""
    if cid not in _CHAR_CACHE:
        root = os.path.join(S.ASSET_ROOT, "iso", "chars", cid)
        with open(os.path.join(root, "anchor.json")) as f:
            foot = tuple(json.load(f)["foot"])
        frames = {}
        for act in sorted(os.listdir(root)):
            path = os.path.join(root, act)
            if not os.path.isdir(path):
                continue
            for d in DIR8:
                folder = os.path.join(path, d)
                files = sorted(os.listdir(folder), key=lambda n: int(n.split(".")[0]))
                frames[f"{act}_{d}"] = [outlined(brighten(pygame.image.load(os.path.join(folder, n)).convert_alpha(),
                                                          CHAR_GAIN)) for n in files]
        frames["idle"] = frames["idle_s"]
        _CHAR_CACHE[cid] = (frames, foot)
    return _CHAR_CACHE[cid]


def char_animator(cid):
    frames, foot = load_char(cid)
    return IsoAnimator(frames, foot)


_TILE_CACHE = {}


def tile_image(tid):
    """Тайл набора (assets/iso/tiles/<id>.png), 128×256: ромб пола — внизу, центр ромба в (64, 207)."""
    if tid not in _TILE_CACHE:
        img = pygame.image.load(os.path.join(S.ASSET_ROOT, "iso", "tiles", tid + ".png")).convert_alpha()
        _TILE_CACHE[tid] = brighten(img, TILE_GAIN, TILE_WARM)
    return _TILE_CACHE[tid]


TILE_ANCHOR = (64, 207)   # центр ромба пола в картинке тайла 128×256
