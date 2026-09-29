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
    scale = 1 if os.path.isfile(os.path.join(root_dir, "native")) else SPRITE_SCALE  # крупные листы (пёс)
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
            frames.append(pygame.transform.scale(img, (w * scale, h * scale)) if scale != 1 else img)
        if not frames:
            return None
        result[f"walk_{d}"] = frames
        result[f"idle_{d}"] = [frames[1 % len(frames)]]
        result[f"attack_{d}"] = frames  # отдельных кадров удара в листах нет — рывок шагом
        # боевые кадры, если нарисованы (tools/make_hero_anims.py): root/melee/<сторона>/, root/shoot/<сторона>/
        for action in ("melee", "shoot"):
            extra = _load_scaled(os.path.join(root_dir, action, d))
            if extra:
                result[f"{action}_{d}"] = extra
        if f"melee_{d}" in result:
            result[f"attack_{d}"] = result[f"melee_{d}"]
        result[f"hit_{d}"], result[f"dodge_{d}"] = make_reactions(result[f"idle_{d}"][0], d)
        result[f"attack_melee_{d}"], result[f"attack_ranged_{d}"] = make_attacks(result[f"idle_{d}"][0], d)
    result["idle"] = result["idle_down"]
    return result


def add_flat_combat_frames(result):
    """Плейсхолдерам без сторон — те же боевые кадры, нарисованные «вправо»
    (влево аниматор их отражает)."""
    idle = result["idle"][0]
    result["hit"], result["dodge"] = make_reactions(idle, "right")
    result["attack_melee"], result["attack_ranged"] = make_attacks(idle, "right")
    return result


def _load_scaled(folder):
    if not os.path.isdir(folder):
        return None
    frames = []
    for f in _sorted_frames(folder):
        img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
        w, h = img.get_size()
        frames.append(pygame.transform.scale(img, (w * SPRITE_SCALE, h * SPRITE_SCALE)))
    return frames or None


# куда отшатывается персонаж, смотрящий в сторону d (от удара — назад)
_BACK = {"right": (-1, 0), "left": (1, 0), "down": (0, -1), "up": (0, 1)}
_SIDE = {"right": (0, 0), "left": (0, 0), "down": (1, 0), "up": (-1, 0)}


def make_reactions(idle, d):
    """Реакции для любого персонажа из его стоячего кадра:
    hit — отброс назад и красная вспышка, dodge — отскок (враг промахнулся)."""
    w, h = idle.get_size()
    pad = 8 * SPRITE_SCALE
    bx, by = _BACK[d]
    sx, sy = _SIDE[d]

    def frame(dx, dy, tint=None):
        s = pygame.Surface((w + pad * 2, h + pad), pygame.SRCALPHA)
        img = idle
        if tint:
            img = idle.copy()
            img.fill(tint[0], special_flags=pygame.BLEND_RGBA_MULT)
            img.fill(tint[1], special_flags=pygame.BLEND_RGB_ADD)
        s.blit(img, (pad + dx, pad + dy))
        return s

    k = SPRITE_SCALE
    red = ((255, 150, 140, 255), (90, 0, 0))
    pale = ((255, 210, 200, 255), (40, 0, 0))
    hit = [frame(bx * 3 * k, by * 2 * k, red), frame(bx * 2 * k, by * k, pale), frame(bx * k, 0)]
    if sx or sy:  # анфас/спиной — уворот вбок
        dodge = [frame(sx * 3 * k, k), frame(sx * 4 * k, k), frame(sx * 2 * k, 0)]
    else:         # в профиль — отскок назад с приседанием
        dodge = [frame(bx * 3 * k, k), frame(bx * 4 * k, 2 * k), frame(bx * 2 * k, 0)]
    return hit, dodge


def make_attacks(idle, d):
    """Атака для любого персонажа из стоячего кадра:
    attack_melee — замах, рывок вперёд со следом когтей, возврат;
    attack_ranged — вскинуть оружие, выстрел со вспышкой и отдачей, дымок."""
    w, h = idle.get_size()
    k = SPRITE_SCALE
    pad = 14 * k
    bx, by = _BACK[d]
    fx, fy = -bx, -by                     # куда смотрит
    cw, ch = w + pad * 2, h + pad
    cx, chest = pad + w // 2, pad + int(h * 0.45)

    def frame(dx, dy, draw=None):
        s = pygame.Surface((cw, ch), pygame.SRCALPHA)
        if draw and fy < 0:   # со спины оружие и когти за телом — рисуем до него
            draw(s, dx, dy)
        s.blit(idle, (pad + dx, pad + dy))
        if draw and fy >= 0:
            draw(s, dx, dy)
        return s

    def front(dx, dy, dist):
        return (cx + dx + fx * (w // 2 + dist), chest + dy + fy * (h // 3 + dist))

    def claws(s, dx, dy):
        x, y = front(dx, dy, 4 * k)
        layer = pygame.Surface((cw, ch), pygame.SRCALPHA)
        for i in (-1, 0, 1):  # три следа когтей дугой
            ox, oy = (fy * i * 5 * k, fx * i * 5 * k) if fx else (i * 5 * k, 0)
            a = (x + ox - fy * 6 * k - fx * 2 * k, y + oy - fx * 6 * k - fy * 2 * k)
            b = (x + ox + fy * 6 * k + fx * 3 * k, y + oy + fx * 6 * k + fy * 3 * k)
            pygame.draw.line(layer, (255, 235, 220, 200), a, b, 2 * k)
            pygame.draw.line(layer, (210, 40, 30, 150), (a[0] + 1, a[1] + 1), (b[0] + 1, b[1] + 1), k)
        s.blit(layer, (0, 0))

    def gun(s, dx, dy, fire=False, smoke=False):
        x, y = front(dx, dy, 0)
        if fx:
            body = pygame.Rect(0, 0, 9 * k, 3 * k)
            body.center = (x + fx * 3 * k, y)
        else:
            body = pygame.Rect(0, 0, 3 * k, 7 * k)
            body.center = (x, y + fy * 3 * k)
        pygame.draw.rect(s, (20, 18, 22), body.inflate(2 * k, 2 * k))
        pygame.draw.rect(s, (70, 72, 80), body)
        mx = body.right + k if fx > 0 else body.left - k if fx < 0 else body.centerx
        my = body.centery if fx else (body.bottom + k if fy > 0 else body.top - k)
        if fire:
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                pygame.draw.line(s, (255, 236, 140), (mx, my), (mx + ddx * 4 * k, my + ddy * 4 * k), k)
            pygame.draw.circle(s, (255, 255, 230), (mx, my), 2 * k)
        if smoke:
            layer = pygame.Surface((cw, ch), pygame.SRCALPHA)
            pygame.draw.circle(layer, (200, 200, 195, 110), (mx + fx * 3 * k, my - 3 * k), 3 * k)
            s.blit(layer, (0, 0))

    melee = [frame(bx * 3 * k, by * 2 * k),
             frame(fx * 6 * k, fy * 4 * k, claws),
             frame(fx * 2 * k, fy * k)]
    ranged = [frame(0, 0, lambda s, dx, dy: gun(s, dx, dy)),
              frame(bx * 2 * k, by * k, lambda s, dx, dy: gun(s, dx, dy, fire=True)),
              frame(0, 0, lambda s, dx, dy: gun(s, dx, dy, smoke=True))]
    return melee, ranged


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
    return add_flat_combat_frames(result)


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
    return add_flat_combat_frames(result)


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
SPECIAL_TILE_NAMES = {"X": "container", "D": "door", ">": "exit", "%": "terminal"}
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
        if surf is None and name == "terminal":  # терминал — тот же, что в городе
            tpath = os.path.join("assets", "town", "props", "x_terminal.png")
            if os.path.isfile(tpath):
                img = pygame.image.load(tpath).convert_alpha()
                sc = size[0] / img.get_width()
                surf = pygame.transform.smoothscale(img, (size[0], int(img.get_height() * sc)))
        _SPECIAL_CACHE[ch] = surf or pa.make_special_tile(name, size)
    return _SPECIAL_CACHE[ch]
