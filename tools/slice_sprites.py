"""
Нарезка спрайт-листов персонажей в кадры для игры.

Лист — 4×4 кадра по 48×48 (как в npc/*.png):
  строка 0 — спиной (идёт вверх), 1 — вправо, 2 — лицом (вниз), 3 — влево;
  столбцы — фазы шага (1 и 3 — стоит, 0 и 2 — шагает).

Результат: assets/sprites/<папка>/{up,right,down,left}/0.png..3.png.
Все кадры листа обрезаются по общей рамке (по самому широкому/высокому
кадру), так что персонаж не «прыгает» между кадрами, а ноги стоят на
нижнем крае картинки — игра рисует спрайт от ног.

Запуск из папки game_project:
    .venv/bin/python tools/slice_sprites.py
Добавить персонажа — строка в SHEETS ниже, потом перезапустить.
"""
import os
import sys

import pygame

FRAME = 48
ROWS = ["up", "right", "down", "left"]

# лист в npc/ -> папка в assets/sprites/ (её имя = id персонажа в игре)
SHEETS = {
    "hero_01.png": "player",                 # главный герой
    "npc_02_office_mutant.png": "gena",      # Ржавый Гена, торговец
    "npc_03_blondie.png.png": "blondie",     # квестовый персонаж
    "npc_04_raider.png": "loner",            # квестовый персонаж
    "npc_05_ratman.png": "ratman",           # враг: крысолюд
    "npc_05_ratman_boss.png": "ratman_boss", # враг: вожак крысолюдов
    "npc_06_mutant.png": "rad_mutant",       # враг: медленный радиоактивный мутант
    "npc_07_mutant_turtle.png": "turtle",    # мирный: Черепан, мутант-черепаха
}


def slice_sheet(src, dst):
    sheet = pygame.image.load(src)
    cells = [[sheet.subsurface((c * FRAME, r * FRAME, FRAME, FRAME)) for c in range(4)] for r in range(4)]
    boxes = [cell.get_bounding_rect(min_alpha=10) for row in cells for cell in row]
    crop = boxes[0].unionall(boxes[1:])
    for r, direction in enumerate(ROWS):
        folder = os.path.join(dst, direction)
        os.makedirs(folder, exist_ok=True)
        for c in range(4):
            pygame.image.save(cells[r][c].subsurface(crop), os.path.join(folder, f"{c}.png"))
    return crop


# листы другого формата: крупные кадры, свой порядок строк, свой масштаб
SPECIAL = {
    "dog.png": {"name": "dog", "cell": 128, "cols": 4,
                "rows": {"down": 0, "right": 1, "up": 2, "left": 3},  # дальше — позы сидя/лёжа
                "height": 40},  # пёс — примерно по колено человеку (герой в игре 74 px)
}

# листы, собранные tools/import_sheets.py из картинок npc/raw/: 4×4 квадратные клетки,
# строки up, right, down, left. id -> рост в игре (герой — 74 px)
IMPORTED = {
    # первый акт: Бейкер, Зайзикс, Нидлс (культист и Ансельм рисуются кодом — tools/make_robes.py)
    "amos": 70,          # дед Эймос Рид, сержант в отставке
    "detective": 72,     # человек в шляпе с фонарём (предатель в Бейкере / агент Ордена)
    "healer": 66,        # «целитель» Зайзикса — старик в тюрбане
    "barkeep": 74,       # здоровяк-бармен
    "desert_guard": 74,  # охранник в пустынной броне (блокпост на мосту)
    "soldier": 72,       # солдат в каске (повязка перекрашена)
    "acolyte": 68,       # послушница в оранжевом
    "seer": 66,          # женщина в фиолетовом капюшоне
    "monk": 70, "scout": 72, "redarmor": 72, "visor_punk": 72, "cyborg": 72,
    "kid": 56, "girl_pink": 64, "girl_hood": 64,
    **{f"folk_{c}": 70 for c in "cdefghij"},     # жители
    # враги
    "robot_guard": 86,   # охранный робот склада «Бейкер-7»
    "robot_skel": 72,    # робот-скелет
    "mech_green": 90,    # шагающая броня
    "sand_golem": 84,    # песчаный голем (Зайзикс)
    "river_lizard": 72,  # речной ящер (Нидлс)
    "beast": 76,         # фиолетовый зверь-мутант
}
SPECIAL.update({f"{cid}.png": {"name": cid, "cell": None, "cols": 4, "height": h,
                               "rows": {"up": 0, "right": 1, "down": 2, "left": 3}}
                for cid, h in IMPORTED.items()})


def slice_special(src, dst, spec):
    """Кадры в игровом размере (игра их больше не увеличивает — файл native)."""
    sheet = pygame.image.load(src)
    cell = spec["cell"] or sheet.get_width() // spec["cols"]
    cells = {d: [sheet.subsurface((c * cell, r * cell, cell, cell)) for c in range(spec["cols"])]
             for d, r in spec["rows"].items()}
    boxes = [f.get_bounding_rect(min_alpha=10) for fr in cells.values() for f in fr]
    crop = boxes[0].unionall(boxes[1:])
    k = spec["height"] / crop.h
    size = (max(1, round(crop.w * k)), spec["height"])
    for d, frames in cells.items():
        folder = os.path.join(dst, d)
        os.makedirs(folder, exist_ok=True)
        for i, f in enumerate(frames):
            img = f.subsurface(crop).copy()
            while img.get_height() < size[1]:   # мелкий пиксель-арт: сперва scale2x, чтобы не размыть
                img = pygame.transform.scale2x(img)
            pygame.image.save(pygame.transform.smoothscale(img, size), os.path.join(folder, f"{i}.png"))
    with open(os.path.join(dst, "native"), "w") as fh:
        fh.write("кадры уже в игровом размере\n")
    return size


# картинки из интернета: фон — нарисованная «шахматка» прозрачности (белый и светло-серый)
CHECKER = {(255, 255, 255), (230, 230, 230)}

# лист кадров вразброс (без сетки): кадры ищутся как отдельные фигуры
LOOSE = {
    # ящер-мутант, 13 кадров: 10 в профиль (смотрит вправо) — шаг, 2 в профиль стоя, 1 анфас.
    # В игре — крысюк: мелкая злобная тварь из руин (раньше рисовался заглушкой)
    "rat_boss.png": {"name": "rat", "height": 24, "walk": [0, 2, 4, 6], "front": 11, "stand": 10},
    # шагающий мех с пилотом, один кадр (пушкой влево) — враг для станции Анклава «Посейдон-7»
    "warrior.png": {"name": "mech", "height": 52, "single": True},
}


def clean_checker(img):
    """Фон-шахматку — в прозрачность: заливка от краёв по цветам шахматки, потом
    закрытые «окна» шахматки внутри (между лап, под рукой), если в них оба цвета."""
    src = img
    img = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    img.blit(src, (0, 0))
    w, h = img.get_size()
    bg = [[tuple(img.get_at((x, y)))[:3] in CHECKER for x in range(w)] for y in range(h)]
    seen = [[False] * w for _ in range(h)]

    def region(sx, sy):
        stack, out = [(sx, sy)], []
        seen[sy][sx] = True
        while stack:
            x, y = stack.pop()
            out.append((x, y))
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and bg[ny][nx]:
                    seen[ny][nx] = True
                    stack.append((nx, ny))
        return out

    for y in range(h):
        for x in range(w):
            if bg[y][x] and not seen[y][x]:
                reg = region(x, y)
                border = any(px in (0, w - 1) or py in (0, h - 1) for px, py in reg)
                colors = {tuple(img.get_at(p))[:3] for p in reg[:400]}
                if border or (len(reg) >= 24 and len(colors) == 2):
                    for p in reg:
                        img.set_at(p, (0, 0, 0, 0))
    return img


def figures(img, min_px=400):
    """Отдельные фигуры на листе (8-связность) — прямоугольники, по строкам сверху вниз."""
    w, h = img.get_size()
    solid = [[img.get_at((x, y)).a > 10 for x in range(w)] for y in range(h)]
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        for x in range(w):
            if solid[y][x] and not seen[y][x]:
                stack, n = [(x, y)], 0
                seen[y][x] = True
                x0 = x1 = x
                y0 = y1 = y
                while stack:
                    cx, cy = stack.pop()
                    n += 1
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h and solid[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if n >= min_px:
                    boxes.append(pygame.Rect(x0, y0, x1 - x0 + 1, y1 - y0 + 1))
    boxes.sort(key=lambda r: (r.centery // 120, r.x))
    return boxes


def slice_loose(src, dst, spec):
    """Кадры с листа «вразброс» — в пиксельный размер игры (игра увеличит их вдвое).
    Нет вида со спины — вверх идёт профиль; нет шага анфас — анфас покачивается."""
    import shutil
    sheet = clean_checker(pygame.image.load(src))
    boxes = figures(sheet)
    frames = [sheet.subsurface(b).copy() for b in boxes]
    k = spec["height"] / max(f.get_height() for f in frames)

    def small(f):
        return pygame.transform.smoothscale(f, (max(1, round(f.get_width() * k)), max(1, round(f.get_height() * k))))

    def canvas(fs):
        """Все кадры одного размера, ноги на нижнем крае, по центру."""
        cw, ch = max(f.get_width() for f in fs), max(f.get_height() for f in fs)
        out = []
        for f in fs:
            c = pygame.Surface((cw, ch), pygame.SRCALPHA)
            c.blit(f, ((cw - f.get_width()) // 2, ch - f.get_height()))
            out.append(c)
        return out

    if spec.get("single"):
        base = small(frames[0])
        left = [base] * 4
        right = [pygame.transform.flip(base, True, False)] * 4
        down = up = [base] * 4
    else:
        side = [small(frames[i]) for i in spec["walk"]]
        stand = small(frames[spec["stand"]])
        front = small(frames[spec["front"]])
        right = side[:4]
        left = [pygame.transform.flip(f, True, False) for f in right]
        up = right
        down = [front, front, front, front]
    shutil.rmtree(dst, ignore_errors=True)
    allf = canvas(right + left + up + down)
    for n, d in enumerate(("right", "left", "up", "down")):
        folder = os.path.join(dst, d)
        os.makedirs(folder, exist_ok=True)
        for i in range(4):
            f = allf[n * 4 + i]
            if d == "down" and not spec.get("single") and i % 2:   # анфас дышит: чуть ниже на пиксель
                g = pygame.Surface(f.get_size(), pygame.SRCALPHA)
                g.blit(f, (0, 1))
                f = g
            pygame.image.save(f, os.path.join(folder, f"{i}.png"))
    return allf[0].get_size(), len(frames)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    missing = [f for f in SHEETS if not os.path.isfile(os.path.join("npc", f))]
    for f in missing:
        print(f"нет файла npc/{f} — пропускаю")
    for f, name in SHEETS.items():
        if f in missing:
            continue
        crop = slice_sheet(os.path.join("npc", f), os.path.join("assets", "sprites", name))
        print(f"npc/{f} -> assets/sprites/{name}/  (кадр {crop.w}×{crop.h})")
    for f, spec in SPECIAL.items():
        path = os.path.join("npc", f)
        if os.path.isfile(path):
            size = slice_special(path, os.path.join("assets", "sprites", spec["name"]), spec)
            print(f"npc/{f} -> assets/sprites/{spec['name']}/  (кадр {size[0]}×{size[1]}, без увеличения)")
    for f, spec in LOOSE.items():
        path = os.path.join("npc", f)
        if os.path.isfile(path):
            size, n = slice_loose(path, os.path.join("assets", "sprites", spec["name"]), spec)
            print(f"npc/{f} -> assets/sprites/{spec['name']}/  (фигур на листе: {n}, кадр {size[0]}×{size[1]})")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
