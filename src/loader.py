"""
Загрузка спрайтов с автоматическим фолбэком на плейсхолдер-графику,
если настоящих файлов ещё нет в assets/.

Ожидаемый формат реальных ассетов (см. README.md):
  assets/sprites/<персонаж>/{down,left,right,up}/0.png..  — кадры по направлениям
      (нарезаются из листов скриптом tools/slice_sprites.py), либо по-старому:
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
SPRITE_SCALE = 2  # пиксель-арт персонажей увеличиваем без сглаживания


def _sorted_frames(folder):
    return sorted(
        (f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".bmp"))),
        # 2.png раньше 10.png: сортируем по номеру, а не по строке
        key=lambda f: (int(os.path.splitext(f)[0]) if os.path.splitext(f)[0].isdigit() else 10**9, f),
    )


def load_directional_animations(root_dir):
    """Кадры по четырём направлениям (root_dir/down, left, right, up) или None.
    Фазы шага: 0 и 2 — шаг, 1 и 3 — стоит; стоячий кадр идёт в idle."""
    result = {}
    for d in ("down", "left", "right", "up"):
        folder = os.path.join(root_dir, d)
        if not os.path.isdir(folder):
            return None
        frames = []
        for f in _sorted_frames(folder):
            try:
                img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
            except Exception:
                continue
            w, h = img.get_size()
            frames.append(pygame.transform.scale(img, (w * SPRITE_SCALE, h * SPRITE_SCALE)))
        if not frames:
            return None
        result[f"walk_{d}"] = frames
        result[f"idle_{d}"] = [frames[1 % len(frames)]]
        result[f"attack_{d}"] = frames  # отдельных кадров удара в листах нет — рывок шагом
    result["idle"] = result["idle_down"]
    return result


def _load_frame_folder(folder, size):
    if not os.path.isdir(folder):
        return None
    files = _sorted_frames(folder)
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
    """Возвращает dict {'idle': [surf,...], 'walk': [...], 'attack': [...]}
    или анимации по направлениям, если они нарезаны."""
    directional = load_directional_animations(root_dir)
    if directional:
        return directional
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
    directional = load_directional_animations(root_dir)
    if directional:
        return directional
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


# Иконки предметов: assets/items/<icon>.png (icon — поле в data/items.json) или плейсхолдер.
_ITEM_CACHE = {}


def item_icon(kind, size=(34, 34), halo=True):
    """halo — тёмное пятно под предметом (для лежащих на земле)."""
    from . import items  # items читает data/ при импорте
    key = (kind, size, halo)
    if key not in _ITEM_CACHE:
        icon_id = items.icon_id(kind)
        path = os.path.join("assets", "items", f"{icon_id}.png")
        icon = None
        if os.path.isfile(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                icon = (pygame.transform.scale(img, size) if size[0] % img.get_width() == 0
                        else pygame.transform.smoothscale(img, size))
            except Exception:
                icon = None
        _ITEM_CACHE[key] = icon or pa.make_item_icon(icon_id, size, halo)
    return _ITEM_CACHE[key]


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
