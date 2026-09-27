"""
Загрузка спрайтов с автоматическим фолбэком на плейсхолдер-графику,
если настоящих файлов ещё нет в assets/.

Ожидаемый формат реальных ассетов (см. README.md):
  assets/sprites/player/idle/0.png, 1.png, ...
  assets/sprites/player/walk/0.png, ...
  assets/sprites/player/attack/0.png, ...
  assets/sprites/enemy/idle/0.png ...
  assets/tiles/ground.png, wall.png, scrap.png
  assets/bg/layer0.png ... layer3.png  (0 = самый дальний слой)

Если папка/файл не найден — генерируется анимация плейсхолдером
(placeholder_art.py), игра при этом не падает и не требует правок кода.
"""
import os
import pygame

from . import placeholder_art as pa

FRAME_SIZE = (48, 64)
TILE_SIZE = (48, 48)


def _load_frame_folder(folder, size):
    if not os.path.isdir(folder):
        return None
    files = sorted(
        (f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".bmp"))),
        # 2.png раньше 10.png: сортируем по номеру, а не по строке
        key=lambda f: (int(os.path.splitext(f)[0]) if os.path.splitext(f)[0].isdigit() else 10**9, f),
    )
    if not files:
        return None
    frames = []
    for f in files:
        try:
            img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
            frames.append(pygame.transform.smoothscale(img, size))
        except Exception:
            continue
    return frames or None


def load_humanoid_animations(root_dir, size, base_color, accent_color, frames_per_action=6):
    """Возвращает dict {'idle': [surf,...], 'walk': [...], 'attack': [...]}."""
    result = {}
    for action in ("idle", "walk", "attack"):
        real = _load_frame_folder(os.path.join(root_dir, action), size)
        if real:
            result[action] = real
        else:
            n = frames_per_action if action != "attack" else max(3, frames_per_action - 2)
            result[action] = [
                pa.make_humanoid_frame(size, base_color, accent_color, i / n, action=action)
                for i in range(n)
            ]
    return result


def load_creature_animations(root_dir, size, base_color, accent_color, kind="mutant", frames_per_action=6):
    """Анимации существа по типу плейсхолдера: humanoid / mutant / beetle."""
    if kind == "humanoid":
        return load_humanoid_animations(root_dir, size, base_color, accent_color, frames_per_action)
    if kind == "beetle":
        make = pa.make_beetle_frame
    else:
        make = pa.make_mutant_frame
    result = {}
    for action in ("idle", "walk"):
        real = _load_frame_folder(os.path.join(root_dir, action), size)
        result[action] = real or [make(size, base_color, accent_color, i / frames_per_action)
                                  for i in range(frames_per_action)]
    result["attack"] = _load_frame_folder(os.path.join(root_dir, "attack"), size) or result["walk"]
    return result


# Иконки предметов на земле: assets/items/<id>.png или плейсхолдер
ITEM_IDS = {"лом": "scrap", "химикаты": "chems", "ткань": "cloth", "патроны": "ammo", "самопал": "pistol"}
_ITEM_CACHE = {}


def item_icon(kind, size=(34, 34)):
    if kind not in _ITEM_CACHE:
        item_id = ITEM_IDS.get(kind, "misc")
        path = os.path.join("assets", "items", f"{item_id}.png")
        icon = None
        if os.path.isfile(path):
            try:
                icon = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), size)
            except Exception:
                icon = None
        _ITEM_CACHE[kind] = icon or pa.make_item_icon(item_id, size)
    return _ITEM_CACHE[kind]


def load_tile(tile_dir, name, kind, size, base_color):
    path = os.path.join(tile_dir, f"{name}.png")
    if os.path.isfile(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except Exception:
            pass
    return pa.make_tile_surface(size, base_color, kind=kind)


def load_parallax_layers(bg_dir, screen_size, layer_defs):
    """layer_defs: список dict(name, top_color, bottom_color, speed)."""
    layers = []
    w, h = screen_size
    for i, d in enumerate(layer_defs):
        path = os.path.join(bg_dir, f"layer{i}.png")
        surf = None
        if os.path.isfile(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                scale = h / img.get_height()
                surf = pygame.transform.smoothscale(img, (int(img.get_width() * scale), h))
            except Exception:
                surf = None
        if surf is None:
            wide = w * 2
            surf = pa.make_parallax_layer((wide, h), d["top_color"], d["bottom_color"], seed=i * 17 + 3,
                                          fill_sky=(i == 0), baseline_ratio=d.get("baseline", 0.72))
        layers.append({"surface": surf, "speed": d["speed"]})
    return layers


# Клетки-объекты: контейнер, дверь, выход (assets/tiles/container.png и т.д.)
SPECIAL_TILE_NAMES = {"X": "container", "D": "door", ">": "exit"}
_SPECIAL_CACHE = {}


def special_tile(ch, size=(48, 48)):
    if ch not in _SPECIAL_CACHE:
        name = SPECIAL_TILE_NAMES[ch]
        path = os.path.join("assets", "tiles", f"{name}.png")
        surf = None
        if os.path.isfile(path):
            try:
                surf = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), size)
            except Exception:
                surf = None
        _SPECIAL_CACHE[ch] = surf or pa.make_special_tile(name, size)
    return _SPECIAL_CACHE[ch]
