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
