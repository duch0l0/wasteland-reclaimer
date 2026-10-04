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
}


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
        pygame.image.save(icon(sheet, rects[idx]), os.path.join(OUT, f"{name}.png"))
        print(f"{name}: объект {idx} {tuple(rects[idx])}")
    sheets = pack_icons()
    if not sheets:
        print("наборов иконок нет (../tilesets_sckr) — оставлены прежние")
        return 0
    for name, (k, idx) in PACK_ICONS.items():
        im, rs = sheets[k]
        pygame.image.save(icon(im, rs[idx]), os.path.join(OUT, f"{name}.png"))
    print(f"иконок из наборов: {len(PACK_ICONS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
