"""
Общие приёмы для убежищ: лампы с цветным светом и мелкие декали (tools/make_vault_decals.py).
Использование: LM = Lamps(city); LM.lamp(m, "warm", x, y); LM.decal(m, "x_vd_wet0", x, y)
Лампа на стене (клетка — стена) — настенный плафон в решётке, на полу — торшер. Свои спрайты x_vd_wl_*, x_vd_stand_*.
"""


class Lamps:
    def __init__(self, city):
        self.city = city

    def lamp(self, m, kind, x, y):
        wall = m.ground[y][x] in m.walls or m.ground[y][x] in ("_", "x")
        name = f"x_vd_wl_{kind}" if wall else f"x_vd_stand_{kind}"
        m.maybe(name, x, y, check=False, allow_reserved=True)

    def lamps(self, m, kind, pts):
        for x, y in pts:
            self.lamp(m, kind, x, y)

    def decal(self, m, name, x, y):
        m.maybe(name, x, y, check=False, allow_reserved=True)

    def decals(self, m, name, pts):
        for x, y in pts:
            self.decal(m, name, x, y)

    def doors(self, m):
        """Рамы во всех проёмах карты (m.opening): стойки по краям, над северным проходом — перемычка с индикатором."""
        for x0, y0, x1, y1 in getattr(m, "openings", []):
            if (y1 - y0) >= (x1 - x0):                      # проход с севера на юг (в толще стены три ряда)
                for y in range(y0, y1 + 1):
                    self.decal(m, "x_vd_fr_l", x0, y)
                    self.decal(m, "x_vd_fr_r", x1, y)
                for x in range(x0, x1 + 1):
                    self.decal(m, "x_vd_fr_hdr", x, y0)
            else:                                           # с запада на восток: по краям — верхняя и нижняя кромка
                for x in range(x0, x1 + 1):
                    self.decal(m, "x_vd_fr_t", x, y0)
                    self.decal(m, "x_vd_fr_b", x, y1)


# освещение интерьеров по умолчанию: цвет темноты и лампы сеткой на свободном полу (по музыке карты — характер места)
COLORS_RGB = {"warm": (255, 190, 110), "cold": (160, 200, 235), "amber": (255, 160, 60), "red": (255, 60, 50), "green": (130, 235, 160),
              "violet": (200, 130, 255)}
AMBIENT = {"hub": ([132, 118, 104], "warm"), "reno": ([126, 108, 120], "amber"), "desert": ([134, 120, 108], "warm"),
           "lab": ([112, 118, 132], "cold"), "vats": ([88, 96, 108], "amber"), "caves": ([84, 84, 98], "amber"),
           "junktown": ([130, 116, 104], "warm")}


def auto_ambient(m, step=6):
    step = 9 if AMBIENT.get(m.music, AMBIENT["hub"])[1] == "cold" else step
    """Интерьеру без своего света: ночной фон и настенные плафоны вдоль северных стен каждой комнаты
    (стена с полом под ней), по характеру места (music карты) — цвет света."""
    if not m.interior or m.night:
        return 0
    night, kind = AMBIENT.get(m.music, AMBIENT["hub"])
    m.night = night
    n = 0
    last = {}
    for y in range(1, m.H - 1):
        for x in range(1, m.W - 1):
            g = m.ground[y][x]
            below = m.ground[y + 1][x] if y + 1 < m.H else "_"
            if g in m.walls and below not in m.walls and below not in ("_", "x") and (x, y + 1) not in m.reserved:
                if x - last.get(y, -99) >= step:
                    if m.maybe(f"x_vd_wl_{kind}", x, y, check=False, allow_reserved=True):
                        last[y] = x
                        n += 1
    # потолочные светильники в глубине комнат: не сеткой, а с разбросом, и только там, где своих источников света нет
    import random
    from src import props as P_
    rnd = random.Random(m.W * 131 + m.H * 7)
    have = [(x, y) for p in m.props if P_.CATALOG.get(p[0], {}).get("light") for x, y in [(p[1], p[2])]]
    have += [(int(L[0]) // 48, int(L[1]) // 48) for L in getattr(m, "lights", [])]
    col = tuple(int(c * (0.62 if kind == "cold" else 0.8)) for c in COLORS_RGB[kind])
    gx, gy = (9, 7) if kind == "cold" else (7, 6)
    for y in range(6, m.H - 3, gy):
        for x in range(5 + (y // gy) % 2 * (gx // 2), m.W - 4, gx):
            x += rnd.randint(-2, 2)
            y2 = y + rnd.randint(-1, 1)
            if not (3 <= x < m.W - 3 and 3 <= y2 < m.H - 3):
                continue
            if any(abs(x - hx) + abs(y2 - hy) < 6 for hx, hy in have):
                continue
            if all(m.ground[y2 + dy][x + dx] not in m.walls and m.ground[y2 + dy][x + dx] not in ("_", "x")
                   for dx in (-2, 0, 2) for dy in (-2, 0, 2) if 0 <= y2 + dy < m.H and 0 <= x + dx < m.W):
                m.ceiling(x, y2, rnd.choice((190, 220, 250)), tuple(int(c * 0.7) for c in col), rnd.choice((0.0, 0.0, 0.04, 0.1)))
                have.append((x, y2))
                n += 1
    return n


def entry_door(city, m, x, y=3, width=2):
    """Тамбур у верхнего края интерьера (пол в толще стены, дальше чернота): стена закрывается, портал-выход
    переносится на линию стены — обычный проём без дверей, в который не нужно «проходить сквозь створки»."""
    wall = m.ground[1][x - 1]
    for yy in range(1, y):
        for dx in range(width):
            m.ground[yy][x + dx] = wall
    tiles = {(x + dx, yy) for dx in range(width) for yy in range(1, y)}
    for p in m.portals:
        p["tiles"] = [[tx, y] if (tx, ty) in tiles else [tx, ty] for tx, ty in p["tiles"]]
        seen = []
        for t in p["tiles"]:
            if t not in seen:
                seen.append(t)
        p["tiles"] = seen


# ------------------------------------------------------------------ порядок с лампами: не посреди тропы, не в проёмах
def _solid(m, x, y):
    if not (0 <= x < m.W and 0 <= y < m.H):
        return True
    c = m.ground[y][x]
    return c in ("x", "_") or c in getattr(m, "walls", {})


def doorway_cells(m):
    """Клетки проёмов и узких проходов (короткий отрезок свободных клеток поперёк при длинном вдоль)."""
    out = set()
    for y in range(m.H):
        for x in range(m.W):
            if _solid(m, x, y):
                continue
            hl = vl = 1
            i = x - 1
            while not _solid(m, i, y) and hl < 6:
                hl += 1
                i -= 1
            i = x + 1
            while not _solid(m, i, y) and hl < 6:
                hl += 1
                i += 1
            j = y - 1
            while not _solid(m, x, j) and vl < 6:
                vl += 1
                j -= 1
            j = y + 1
            while not _solid(m, x, j) and vl < 6:
                vl += 1
                j += 1
            if (hl <= 3 and vl >= 5) or (vl <= 3 and hl >= 5):
                out.add((x, y))
    return out


def tidy_lamps(m):
    """Напольные лампы (x_vd_stand_*) — только у стены и не в проёме: лампа посреди тропы мешает и выглядит случайной.
    Лампе без стены рядом ищется место у ближайшей стены (до 5 клеток); нет такого — вместо лампы потолочный светильник
    (круг света без предмета). Возвращает (сдвинуто, заменено)."""
    from src import props as P_
    if hasattr(m, "interior") and not m.interior:
        return 0, 0                                # на улице лампа у тропы — столб, не комнатный торшер
    doors = doorway_cells(m)
    near_door = {(x + dx, y + dy) for x, y in doors for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    ports = {tuple(t) for p in getattr(m, "portals", []) for t in p["tiles"]} | {tuple(t) for t in getattr(m, "exits", [])}
    occupied = set(getattr(m, "blocked", set()))
    for e in m.props:
        try:
            if P_.info(e[0])["block"]:
                occupied.update(m.footprint(e[0], e[1], e[2]))
        except Exception:
            pass
    lamp_cells = {(e[1], e[2]) for e in m.props if e[0].startswith("x_vd_stand_")}

    def good(c):
        x, y = c
        if _solid(m, x, y) or c in occupied or c in near_door or c in ports or c in lamp_cells:
            return False
        return any(_solid(m, x + dx, y + dy) for dx, dy in ((0, -1), (1, 0), (-1, 0), (0, 1)))

    moved = replaced = 0
    drop = []
    for e in list(m.props):                       # настенный декор (вывески, схемы, «15», счёты) не висит в проёме
        if e[0].startswith(("x_vd_plaque", "x_vd_num", "x_vd_map", "x_vd_sheet", "x_vd_tally", "x_vd_drawing", "x_vd_nine",
                            "x_vd_exit", "x_vd_wl_")) and (e[1], e[2]) in near_door:
            drop.append(next(i for i, q in enumerate(m.props) if q is e))
    for e in list(m.props):
        if not e[0].startswith("x_vd_stand_"):
            continue
        x, y = e[1], e[2]
        if good((x, y)) or ((x, y) not in near_door and any(_solid(m, x + dx, y + dy) for dx, dy in ((0, -1), (1, 0), (-1, 0), (0, 1))
                                                          ) and (x, y) not in ports):
            continue
        lamp_cells.discard((x, y))
        best = None
        for r in range(1, 6):
            cand = [(x + dx, y + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r and good((x + dx, y + dy))]
            cand.sort(key=lambda c: (0 if _solid(m, c[0], c[1] - 1) else 1, abs(c[0] - x) + abs(c[1] - y)))
            if cand:
                best = cand[0]
                break
        if best:
            e[1], e[2] = best
            lamp_cells.add(best)
            moved += 1
        else:
            drop.append(next(i for i, q in enumerate(m.props) if q is e))
            kind = e[0].split("_")[-1]
            col = COLORS_RGB.get(kind, (255, 190, 110))
            if hasattr(m, "ceiling"):
                m.ceiling(x, y, 150, tuple(int(c * 0.7) for c in col))
            else:                                  # MapKit без ceiling(): список ламп забирает вызывающий (extra lights=)
                if not hasattr(m, "lights"):
                    m.lights = []
                m.lights.append([x * 48 + 24, y * 48 + 24, 150, [int(c * 0.7) for c in col], 0.04, "nh"])
            replaced += 1
    drop = sorted(set(drop))
    if drop:                                       # убрали записи из props — индексы ящиков, терминалов и гермодверей сдвигаются
        gone = sorted(drop)
        for ref in list(getattr(m, "containers", [])) + list(getattr(m, "terminals", [])) + list(getattr(m, "gates", [])):
            if "prop" in ref:
                ref["prop"] -= sum(1 for g_ in gone if g_ < ref["prop"])
        for i in reversed(gone):
            del m.props[i]
    return moved, replaced


def exit_glow(m):
    """Выход на южной кромке интерьера: за ним пустота — кладём свет дня на пол перед порогом (см. make_vault_decals.exit_glow)."""
    if hasattr(m, "interior") and not m.interior:
        return 0
    n = 0
    for p in getattr(m, "portals", []):
        for tx, ty in p["tiles"]:
            if ty >= m.H - 1 and not _solid(m, tx, ty):
                m.props.append(["x_vd_exitlight", tx, ty])
                if ty - 1 >= 0 and not _solid(m, tx, ty - 1):
                    m.props.append(["x_vd_exitlight_far", tx, ty - 1])
                n += 1
    return n


KEEP = ("vwall_", "wall_", "x_cliff", "x_vault", "x_mesa", "x_ladder", "x_manhole", "x_door", "x_vd_", "bk_sign", "x_pipe",
        "nc_subway")      # вход в метро — само здание портала, стоит над ним


def clear_exits(m, radius=2):
    """Перед выходом/лестницей интерьера ничего не стоит (скамья, бочка, шкаф): предметы в radius клетках от клетки перехода
    переезжают на ближайшее свободное место. Ящики и терминалы не трогаем (их место выбирал сюжет) — об этом только пишем."""
    from src import props as P_
    if hasattr(m, "interior") and not m.interior:
        return 0
    ports = {tuple(t) for p in getattr(m, "portals", []) for t in p["tiles"]}
    if not ports:
        return 0
    zone = {(x + dx, y + dy) for x, y in ports for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1)}
    refs = {r["prop"] for r in list(getattr(m, "containers", [])) + list(getattr(m, "terminals", [])) + list(getattr(m, "gates", []))
            if "prop" in r}
    doors = doorway_cells(m)
    occupied = set(getattr(m, "blocked", set()))
    for e in m.props:
        try:
            if P_.info(e[0])["block"]:
                occupied.update(m.footprint(e[0], e[1], e[2]))
        except Exception:
            pass
    moved = 0
    for i, e in enumerate(m.props):
        name = e[0]
        if i in refs or name.startswith(KEEP):
            continue
        try:
            inf = P_.info(name)
        except Exception:
            continue
        if inf.get("layer") == "floor":
            continue
        cells = m.footprint(name, e[1], e[2])
        if not any(c in zone for c in cells) or any(_solid(m, *c) for c in cells):
            continue
        fw, fh = inf["foot"]
        found = None
        for r in range(2, 9):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    nx, ny = e[1] + dx, e[2] + dy
                    nc = [(nx + a, ny + b) for a in range(fw) for b in range(fh)]
                    if all(not _solid(m, *c) and c not in zone and c not in occupied and c not in doors for c in nc) and \
                            (not inf["block"] or any(_solid(m, c[0], c[1] - 1) or _solid(m, c[0] - 1, c[1]) or _solid(m, c[0] + 1, c[1]) for c in nc)) and \
                            not (inf["block"] and hasattr(m, "hides") and m.hides(name, nx, ny, skip=e)):
                        found = (nx, ny)
                        break
                if found:
                    break
            if found:
                break
        if found:
            if inf["block"]:
                occupied.difference_update(cells)
                occupied.update((found[0] + a, found[1] + b) for a in range(fw) for b in range(fh))
            e[1], e[2] = found
            moved += 1
    return moved
