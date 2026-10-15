"""
Общие приёмы для убежищ: лампы с цветным светом и мелкие декали (tools/make_vault_decals.py).
Использование: from vaultkit import Lamps; L = Lamps(city); L.lamp(m, "warm", x, y); L.decal(m, "x_vd_wet0", x, y)
"""
COLORS = {"warm": [255, 190, 110], "cold": [150, 190, 230], "red": [255, 50, 40], "green": [120, 230, 150],
          "violet": [190, 120, 255], "amber": [255, 150, 40]}


class Lamps:
    def __init__(self, city):
        self.city = city
        for k, c in COLORS.items():
            city.prop(f"vk_lamp_{k}", "p2_088", block=False,
                      light={"r": 150, "color": c, "at": [0.5, 0.5], "flicker": 0.25 if k == "red" else 0.06})

    def lamp(self, m, kind, x, y):
        m.maybe(f"vk_lamp_{kind}", x, y, check=False, allow_reserved=True)

    def lamps(self, m, kind, pts):
        for x, y in pts:
            self.lamp(m, kind, x, y)

    def decal(self, m, name, x, y):
        m.maybe(name, x, y, check=False, allow_reserved=True)

    def decals(self, m, name, pts):
        for x, y in pts:
            self.decal(m, name, x, y)
