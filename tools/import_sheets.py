"""
Спрайт-листы из интернета (npc/raw/) -> чистые листы в формате игры (npc/<id>.png).

Картинки из сети разного вида: jpg с белым или зелёным фоном, gif, листы RPG Maker
(3 кадра на направление), растянутые при пересохранении. Здесь для каждого листа:
  1. фон (цвет угла или заданный) -> прозрачность: заливка от краёв по похожему цвету,
     плюс крупные «окна» фона внутри (между ног, под рукой);
  2. фигуры находятся как связные куски; строки и столбцы сетки — по промежуткам
     между ними (сетку заранее знаем: rows × cols), мелкие обрывки — к ближайшей клетке;
  3. персонаж — блок клеток (block: строк × столбцов), порядок строк — order;
  4. результат — лист 4×4 квадратных клеток: строки up, right, down, left, кадры шага
     0, 1, 2, 1 (у RPG Maker 3 кадра); ноги — по нижнему краю, по центру.

Дальше npc/<id>.png режет tools/slice_sprites.py (SPECIAL) в assets/sprites/<id>/.

Запуск из папки game_project:  .venv/bin/python tools/import_sheets.py [--preview]
--preview — сводка npc/raw/preview_<лист>.png: найденные клетки с номерами (для проверки).
"""
import os
import sys

import pygame

RAW = os.path.join("npc", "raw")
OUT = "npc"
DIRS = ["up", "right", "down", "left"]

# лист -> как его читать
#   key: цвет фона (None — цвет левого верхнего угла), tol: допуск цвета фона
#   rows, cols: сетка кадров на листе; block: (строк, столбцов) на одного персонажа
#   order: какое направление в какой строке блока; frames: какие столбцы блока брать
#   chars: {(блок_строка, блок_столбец): id}; flip: направление, которое получить отражением
#   fix: правка цветов после вырезания (см. FIXES)
SOURCES = {
    "chibi_town.jpg": {
        "key": (255, 255, 255), "tol": 40, "rows": 8, "cols": 12, "block": (4, 3),
        "order": ["down", "left", "right", "up"],
        "chars": {(0, 0): "kid", (0, 1): "girl_pink", (0, 2): "monk", (0, 3): "girl_hood",
                  (1, 0): "amos", (1, 1): "acolyte", (1, 2): "healer", (1, 3): "seer"},
    },
    "chibi_waste.jpeg": {
        "key": None, "tol": 60, "rows": 8, "cols": 12, "block": (4, 3),
        "order": ["down", "left", "right", "up"],
        "chars": {(0, 0): "barkeep", (0, 1): "scout", (0, 2): "redarmor", (0, 3): "desert_guard",
                  (1, 0): "robot_skel", (1, 1): "visor_punk", (1, 2): "cyborg", (1, 3): "beast"},
    },
    "chibi_folk.png": {
        "key": None, "tol": 40, "rows": 8, "cols": 12, "block": (4, 3),
        "order": ["down", "left", "right", "up"],
        "chars": {(0, 0): "folk_c", (0, 1): "folk_d", (0, 2): "folk_e", (0, 3): "folk_f",
                  (1, 0): "folk_g", (1, 1): "folk_h", (1, 2): "folk_i", (1, 3): "folk_j"},
    },
    "robot_white.png": {
        "key": (255, 255, 255), "tol": 30, "rows": 4, "cols": 3, "block": (4, 3),
        "order": ["down", "left", "right", "up"], "chars": {(0, 0): "robot_guard"},
    },
    "golem.png": {
        "key": None, "tol": 30, "rows": 4, "cols": 4, "block": (4, 4),
        "order": ["down", "left", "right", "up"], "frames": [0, 1, 2, 3], "chars": {(0, 0): "sand_golem"},
    },
    "mech_green.png": {
        "key": None, "tol": 30, "rows": 4, "cols": 4, "block": (4, 4),
        "order": ["down", "left", "right", "up"], "frames": [0, 1, 2, 3], "chars": {(0, 0): "mech_green"},
    },
    # точная сетка (grid: ширина, высота клетки; origin — левый верхний угол сетки)
    "soldier.png": {   # 7 кадров + 2 полупрозрачных (исчезает); повязка на рукаве — перекрашивается
        "grid": (150, 117), "rows": 4, "cols": 11, "block": (4, 11), "frames": [0, 2, 4, 6],
        "order": ["down", "up", "left", "right"], "chars": {(0, 0): "soldier"}, "fix": "armband",
    },
    "detective.png": {
        "key": (255, 255, 255), "tol": 40, "grid": (64, 64), "rows": 4, "cols": 9, "block": (4, 9),
        "frames": [0, 2, 4, 6], "order": ["up", "left", "down", "right"],
        "chars": {(0, 0): "detective"},
    },
    # кадры вразброс: строки фигур сверху вниз (figrows: направление -> (строка, [фигуры в ней]))
    "lizard.gif": {
        "key": None, "tol": 30, "figrows": {"right": (3, [0, 1, 2, 3]), "down": (4, [0, 1, 2, 3]),
                                            "up": (7, [0, 1, 2, 3])},
        "flip": {"left": "right"}, "chars": {(0, 0): "river_lizard"},
    },
}

# правки цвета после вырезания
ARMBAND = (96, 100, 64)   # повязка — просто оливковая ткань


def fix_armband(frame):
    """Красная повязка с белым кругом и знаком -> однотонная оливковая повязка (со светотенью)."""
    m = pygame.mask.from_threshold(frame, (200, 40, 40, 255), (70, 50, 50, 255))
    for comp in m.connected_components(4):
        r = pygame.Rect(comp.get_bounding_rects()[0]).inflate(2, 2).clip(frame.get_rect())
        for y in range(r.top, r.bottom):
            for x in range(r.left, r.right):
                c = frame.get_at((x, y))
                if c.a < 200:
                    continue
                red = c.r > 120 and c.g < 110 and c.b < 110
                white = min(c.r, c.g, c.b) > 170
                black = max(c.r, c.g, c.b) < 60 and r.inflate(-4, -4).collidepoint(x, y)   # знак, не контур
                if red or white or black:
                    k = 0.8 if black else (1.1 if white else 1.0)
                    frame.set_at((x, y), (*(min(255, int(v * k)) for v in ARMBAND), 255))
    return frame


FIXES = {"armband": fix_armband}


def white_robe(sheet):
    """Красный балахон -> белый с тёплым оттенком (брат Ансельм, глава миссии)."""
    out = sheet.copy()
    w, h = out.get_size()
    for y in range(h):
        for x in range(w):
            c = out.get_at((x, y))
            if c.a and c.r > c.g + 30 and c.r > c.b + 30:
                v = min(255, int(c.r * 1.15 + 25))
                out.set_at((x, y), (v, int(v * 0.96), int(v * 0.86), c.a))
    return out


def _recolor(sheet, pick, paint):
    """Перекрасить ткань: pick(цвет) — этот ли пиксель, paint(яркость 0..1, альфа) -> новый цвет."""
    out = sheet.copy()
    w, h = out.get_size()
    for y in range(h):
        for x in range(w):
            c = out.get_at((x, y))
            if c.a and pick(c):
                out.set_at((x, y), paint(max(c.r, c.g, c.b) / 255, c.a))
    return out


def red_robe(sheet):
    """Культист «Детей Единства»: фиолетовый капюшон провидицы -> тёмно-красный балахон."""
    return _recolor(sheet, lambda c: c.b > c.g + 12 and c.r > c.g,
                    lambda v, a: (min(255, int(30 + v * 260)), int(14 + v * 40), int(14 + v * 36), a))


def white_robe_monk(sheet):
    """Брат Ансельм: коричневая ряса монаха -> белая с тёплым оттенком."""
    return _recolor(sheet, lambda c: c.r > c.b + 25 and c.g > c.b + 8 and max(c.r, c.g, c.b) < 215,
                    lambda v, a: (min(255, int(110 + v * 190)), min(255, int(104 + v * 186)),
                                  min(255, int(92 + v * 170)), a))


# листы, перекрашенные из уже собранных: id -> (из какого, чем).
# Культист — из провидицы в капюшоне, Ансельм — из монаха: тот же размер и стиль, что у остальных жителей
# (маленький лист npc/raw/cultist.png при увеличении выходил крупными квадратами — больше не используется)
DERIVED = {}   # культист и Ансельм теперь рисуются кодом: tools/make_robes.py


# ------------------------------------------------------------ фон
def remove_background(img, key, tol):
    rgba = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    rgba.blit(img, (0, 0))
    img = rgba
    w, h = img.get_size()
    if key is None:
        key = tuple(img.get_at((0, 0)))[:3]
    bg = pygame.mask.from_threshold(img, (*key, 255), (tol, tol, tol, 255))
    # прозрачные пиксели — тоже фон
    opaque = pygame.mask.from_surface(img, 10)
    opaque.invert()
    bg.draw(opaque, (0, 0))
    kill = pygame.mask.Mask((w, h))
    for comp in bg.connected_components(1):
        r = comp.get_bounding_rects()[0]
        if r.x == 0 or r.y == 0 or r.right == w or r.bottom == h or comp.count() >= 30:
            kill.draw(comp, (0, 0))
    out = img.copy()
    clear = kill.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(255, 255, 255, 255))
    out.blit(clear, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


# ------------------------------------------------------------ сетка
def best_cut(mask, pos, horizontal, span=7):
    """Линия разреза рядом с pos, где меньше всего непрозрачных пикселей."""
    w, h = mask.get_size()
    best = None
    for p in range(max(1, int(pos) - span), min((h if horizontal else w) - 1, int(pos) + span) + 1):
        if horizontal:
            n = sum(mask.get_at((x, p)) for x in range(0, w, 1))
        else:
            n = sum(mask.get_at((p, y)) for y in range(0, h, 1))
        if best is None or n < best[0] or (n == best[0] and abs(p - pos) < abs(best[1] - pos)):
            best = (n, p)
    return best[1]


def grid_cells(img, rows, cols):
    """{(r, c): картинка клетки}. Сетка равномерная: общую рамку фигур делим поровну,
    каждую линию разреза сдвигаем на самое пустое место рядом (фигуры бывают вплотную)."""
    mask = pygame.mask.from_surface(img, 40)
    comps = [m for m in mask.connected_components(60)]
    rects = [pygame.Rect(m.get_bounding_rects()[0]) for m in comps]
    area = rects[0].unionall(rects[1:])
    ys = [area.y] + [best_cut(mask, area.y + area.h * i / rows, True) for i in range(1, rows)] + [area.bottom]
    xs = [area.x] + [best_cut(mask, area.x + area.w * i / cols, False) for i in range(1, cols)] + [area.right]
    cells = {}
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(xs[c], ys[r], xs[c + 1] - xs[c], ys[r + 1] - ys[r])
            cells[(r, c)] = clean_cell(img.subsurface(rect).copy())
    return cells


def clean_cell(cell):
    """Оставить фигуру: самый крупный кусок и всё, что рядом с ним; обрывки соседей у края — прочь."""
    m = pygame.mask.from_surface(cell, 40)
    comps = sorted(m.connected_components(1), key=lambda c: -c.count())
    if not comps:
        return cell
    main = pygame.Rect(comps[0].get_bounding_rects()[0]).inflate(6, 6)
    keep = pygame.mask.Mask(cell.get_size())
    for c in comps:
        r = pygame.Rect(c.get_bounding_rects()[0])
        if c is comps[0] or (main.colliderect(r) and c.count() >= 3) or c.count() >= comps[0].count() * 0.15:
            keep.draw(c, (0, 0))
    stencil = keep.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    cell.blit(stencil, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    r = cell.get_bounding_rect(min_alpha=10)
    return cell.subsurface(r).copy()


# ------------------------------------------------------------ сборка
def build_sheet(frames):
    """frames: {направление: [кадры]} -> лист 4×4 квадратных клеток (ноги внизу по центру)."""
    cw = max(f.get_width() for fs in frames.values() for f in fs)
    ch = max(f.get_height() for fs in frames.values() for f in fs)
    cell = max(cw, ch) + 2
    sheet = pygame.Surface((cell * 4, cell * 4), pygame.SRCALPHA)
    for r, d in enumerate(DIRS):
        fs = frames[d]
        seq = [fs[0], fs[1], fs[2], fs[1]] if len(fs) == 3 else fs[:4]
        for c, f in enumerate(seq):
            sheet.blit(f, (c * cell + (cell - f.get_width()) // 2, r * cell + cell - 1 - f.get_height()))
    return sheet, cell


def exact_cells(img, spec):
    cw, ch = spec["grid"]
    ox, oy = spec.get("origin", (0, 0))
    return {(r, c): clean_cell(img.subsurface((ox + c * cw, oy + r * ch, cw, ch)).copy())
            for r in range(spec["rows"]) for c in range(spec["cols"])}


def figure_rows(img, min_px=150):
    """Фигуры листа по строкам (сверху вниз), в строке — слева направо."""
    m = pygame.mask.from_surface(img, 40)
    rs = sorted((pygame.Rect(c.get_bounding_rects()[0]) for c in m.connected_components(min_px)),
                key=lambda r: (r.centery, r.x))
    rows = []
    for r in rs:
        if rows and abs(rows[-1][0].centery - r.centery) < 25:
            rows[-1].append(r)
        else:
            rows.append([r])
    return [sorted(row, key=lambda r: r.x) for row in rows]


def convert(name, spec, preview=False):
    img = pygame.image.load(os.path.join(RAW, name))
    if "crop" in spec:
        img = img.subsurface(spec["crop"]).copy()
    if "key" in spec:
        img = remove_background(img, spec.get("key"), spec.get("tol", 30))
    if "figrows" in spec:
        rows = figure_rows(img)
        frames = {d: [clean_cell(img.subsurface(rows[r][i].inflate(4, 4).clip(img.get_rect())).copy()) for i in idx]
                  for d, (r, idx) in spec["figrows"].items()}
        for d, src in spec.get("flip", {}).items():
            frames[d] = [pygame.transform.flip(f, True, False) for f in frames[src]]
        cid = spec["chars"][(0, 0)]
        sheet, cell = build_sheet(frames)
        pygame.image.save(sheet, os.path.join(OUT, f"{cid}.png"))
        return {cid: cell}
    cells = exact_cells(img, spec) if "grid" in spec else grid_cells(img, spec["rows"], spec["cols"])
    if preview:
        font = pygame.font.SysFont(None, 14)
        cw = max(im.get_width() for im in cells.values()) + 8
        ch = max(im.get_height() for im in cells.values()) + 8
        pv = pygame.Surface((cw * spec["cols"], ch * spec["rows"]))
        pv.fill((60, 50, 70))
        for (r, c), im in cells.items():
            pv.blit(im, (c * cw, r * ch))
            pygame.draw.rect(pv, (255, 255, 0), (c * cw, r * ch, im.get_width(), im.get_height()), 1)
            pv.blit(font.render(f"{r},{c}", True, (255, 255, 255)), (c * cw, r * ch))
        pygame.image.save(pv, os.path.join(RAW, f"preview_{os.path.splitext(name)[0]}.png"))
    br, bc = spec["block"]
    made = {}
    for (cr, cc), cid in spec["chars"].items():
        frames = {}
        for i, d in enumerate(spec["order"]):
            cols = spec.get("frames", list(range(bc)))
            frames[d] = [cells[(cr * br + i, cc * bc + k)] for k in cols]
        for d, src in spec.get("flip", {}).items():
            frames[d] = [pygame.transform.flip(f, True, False) for f in frames[src]]
        if spec.get("fix"):
            frames = {d: [FIXES[spec["fix"]](f) for f in fs] for d, fs in frames.items()}
        sheet, cell = build_sheet(frames)
        pygame.image.save(sheet, os.path.join(OUT, f"{cid}.png"))
        made[cid] = cell
    return made


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    preview = "--preview" in sys.argv
    for name, spec in SOURCES.items():
        made = convert(name, spec, preview)
        print(f"{name}: " + ", ".join(f"{k} ({v}px)" for k, v in made.items()))
    for cid, (src, fn) in DERIVED.items():
        pygame.image.save(fn(pygame.image.load(os.path.join(OUT, f"{src}.png"))), os.path.join(OUT, f"{cid}.png"))
        print(f"{cid}: перекрашен из {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
