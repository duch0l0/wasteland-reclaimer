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
