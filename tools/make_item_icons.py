"""
Иконки предметов: оружие из листа npc/raw/weapons.png и всё остальное — из наборов иконок
бандла Cute SCKR (Wasteland Survival Game Icons, Post-Apocalyptic Survival Icon; исходники вне git,
../tilesets_sckr). Иконки на листах находятся по альфе и нумеруются по рядам; номер листа — по
порядку SHEETS (0–2 — wasteland icons, 3–9 — survival icon).

Сначала — иконки оружия из листа npc/raw/weapons.png (3547×1493, оружие вразброс на прозрачном фоне).

Объекты на листе находятся по альфе и сортируются по рядам (как в сводке, которую
печатает --catalog), каждой иконке — номер объекта. Иконка — квадрат 64×64, оружие
вписано по ширине и стоит по центру: игра масштабирует иконку в квадрат (src/loader.item_icon),
и вытянутое оружие не сплющивается.

Запуск из папки game_project:  .venv/bin/python tools/make_item_icons.py
"""
import os
import sys

import pygame

SRC = os.path.join("npc", "raw", "weapons.png")
OUT = os.path.join("assets", "items")
SIZE = 64

# icon (поле в data/items.json) -> номер объекта на листе
ICONS = {
    "shotgun": 20,         # помповый дробовик
    "assault_rifle": 72,   # автомат с деревянным прикладом
    "pistol10": 81,        # армейский пистолет деда
    "hunting_rifle": 3,    # охотничья винтовка Дэкса
    # арсенал (src/weapons.py)
    "sawedoff": 122, "combat_shotgun": 95, "beauty": 95, "gauss": 61, "plasma_rifle": 44,
    "laser_rifle": 23, "stargazer": 23, "flamer": 107, "lmg": 88, "rocket_launcher": 67,
    "minigun": 94, "mommy": 94, "plasma_grenade": 34, "pulse_grenade": 34,
    "alien_blaster": 119,
}
# тонирование (умножение цвета): энергооружие светится, легенды — в золоте
TINTS = {
    "beauty": (255, 215, 120), "gauss": (150, 220, 255), "plasma_rifle": (140, 255, 150),
    "laser_rifle": (255, 140, 130), "stargazer": (255, 220, 140), "flamer": (255, 170, 110),
    "mommy": (255, 190, 210), "plasma_grenade": (130, 255, 140), "pulse_grenade": (140, 180, 255),
    "laser_pistol": (255, 140, 130), "plasma_pistol": (140, 255, 150), "power_fist": (170, 190, 230),
    "super_sledge": (255, 200, 110), "combat_armor": (120, 150, 110), "pa_t45": (190, 200, 215),
    "pa_t51": (235, 205, 140), "pa_enclave": (110, 110, 125), "leather_armor": (190, 130, 85), "combat_helmet": (120, 150, 110),
    "pa_helmet": (190, 200, 215), "enclave_helmet": (110, 110, 125), "spear": (230, 200, 150),
    "boathook": (150, 220, 210), "justice": (255, 215, 120), "voice": (150, 200, 140), "curator_coat": (190, 140, 230),
    "hazmat": (255, 230, 90), "ranger_armor": (205, 175, 120),
    "alien_blaster": (150, 255, 210), "alien_cell": (230, 130, 255), "holy_grenade": (255, 220, 110),
}


def tint(img, rgb):
    out = img.copy()
    out.fill((*rgb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def objects(sheet):
    m = pygame.mask.from_surface(sheet, 60)
    rects = [pygame.Rect(c.get_bounding_rects()[0]) for c in m.connected_components(400)]
    rects = [r for r in rects if r.w > 60]
    rects.sort(key=lambda r: (r.y // 120, r.x))
    return rects


def icon(sheet, rect):
    img = sheet.subsurface(rect).copy()
    k = (SIZE - 4) / max(rect.w, rect.h)
    img = pygame.transform.smoothscale(img, (max(1, round(rect.w * k)), max(1, round(rect.h * k))))
    out = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    out.blit(img, ((SIZE - img.get_width()) // 2, (SIZE - img.get_height()) // 2))
    return out


PACK = os.path.join("..", "tilesets_sckr", "comshadow")
SHEETS = ([os.path.join(PACK, "wasteland-survival-game-icons-pack", "extracted", "wasteland icons", f"{i}.png")
           for i in (1, 2, 3)] +
          [os.path.join(PACK, "post-apocalyptic-survival-icon", "extracted", "survival icon", "survival icon", f"{i}.png")
           for i in range(1, 8)])
# icon (data/items.json) -> (лист, номер иконки на листе)
PACK_ICONS = {
    "scrap": (3, 1), "sharp_scrap": (2, 42), "chems": (0, 7), "cloth": (0, 14), "ammo": (3, 43),
    "pistol": (1, 7), "lockpick": (0, 1), "bandage": (2, 35), "kit": (3, 11), "tonic": (2, 29),
    "jacket": (3, 29), "sign_vest": (2, 5), "hardhat": (3, 10), "moto_helmet": (2, 4), "shovel": (3, 46),
    "bottle": (0, 45), "stash": (3, 49), "shells": (1, 16),
    # новые предметы
    "stim": (0, 18), "pills": (2, 31), "water": (3, 4), "canned": (3, 3), "gasmask": (3, 0),
    "batteries": (3, 13), "tape": (0, 8), "flashlight": (3, 37), "radio": (3, 44), "binoculars": (3, 30),
    "rope": (2, 8), "matches": (2, 10), "energy_bar": (2, 20), "jerky": (2, 23), "purifier": (3, 47),
    "cigarettes": (3, 28), "teddy": (3, 24), "map": (3, 33), "motor_oil": (0, 6), "spring": (0, 19),
    "wrench": (0, 0), "gloves": (3, 14), "boots": (3, 15), "lighter": (2, 11), "lantern": (2, 12),
    "gunpowder": (1, 43), "toolbox": (3, 36), "knife": (2, 39), "keys": (2, 9), "medkit_big": (2, 26), "army_vest": (3, 32),
    # арсенал и броня
    "machete": (2, 38), "fire_axe": (3, 8), "sledge": (3, 6), "super_sledge": (3, 6), "power_fist": (3, 14),
    "throw_knife": (3, 5), "spear": (0, 43), "smg": (1, 4), "revolver": (1, 5), "sniper": (1, 3),
    "laser_pistol": (1, 8), "plasma_pistol": (1, 7), "cell": (1, 36), "mfc": (1, 37), "fuel": (3, 45),
    "rocket": (1, 35), "gauss_ammo": (1, 47), "leather_armor": (3, 32), "metal_armor": (3, 35),
    "combat_armor": (3, 32), "pa_t45": (3, 32), "pa_t51": (3, 32), "pa_enclave": (3, 32),
    "army_helmet": (2, 4), "combat_helmet": (2, 4), "pa_helmet": (2, 4), "enclave_helmet": (2, 4),
    # награды головоломок
    "boathook": (0, 43), "justice": (1, 5), "voice": (1, 3), "curator_coat": (0, 14), "hazmat": (3, 0),
    "ranger_armor": (3, 32), "alien_cell": (1, 36), "holy_grenade": (2, 50),
}


def pack_icons():
    out = {}
    for k, path in enumerate(SHEETS):
        if not os.path.isfile(path):
            return {}
        im = pygame.image.load(path)
        m = pygame.mask.from_surface(im, 40)
        rs = [pygame.Rect(c.get_bounding_rects()[0]) for c in m.connected_components(200)]
        rs = [r for r in rs if r.w > 30 and r.h > 30]
        rs.sort(key=lambda r: (r.centery // (im.get_height() // 10), r.x))
        out[k] = (im, rs)
    return out


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    sheet = pygame.image.load(SRC)
    rects = objects(sheet)
    os.makedirs(OUT, exist_ok=True)
    for name, idx in ICONS.items():
        img = icon(sheet, rects[idx])
        if name in TINTS:
            img = tint(img, TINTS[name])
        pygame.image.save(img, os.path.join(OUT, f"{name}.png"))
        print(f"{name}: объект {idx} {tuple(rects[idx])}")
    sheets = pack_icons()
    if not sheets:
        print("наборов иконок нет (../tilesets_sckr) — оставлены прежние")
        return 0
    for name, (k, idx) in PACK_ICONS.items():
        im, rs = sheets[k]
        img = icon(im, rs[idx])
        if name in TINTS:
            img = tint(img, TINTS[name])
        pygame.image.save(img, os.path.join(OUT, f"{name}.png"))
    print(f"иконок из наборов: {len(PACK_ICONS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
