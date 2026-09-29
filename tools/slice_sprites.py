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


def slice_special(src, dst, spec):
    """Кадры в игровом размере (игра их больше не увеличивает — файл native)."""
    sheet = pygame.image.load(src)
    cell = spec["cell"]
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
            pygame.image.save(pygame.transform.smoothscale(f.subsurface(crop).copy(), size),
                              os.path.join(folder, f"{i}.png"))
    with open(os.path.join(dst, "native"), "w") as fh:
        fh.write("кадры уже в игровом размере\n")
    return size


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
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
