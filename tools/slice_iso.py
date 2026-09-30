"""
Изометрическая графика из набора «2D HD Zombie City Tileset» (SmallScaleInt, папка iso/ — в git не
кладётся, лицензия запрещает выкладывать исходники) в игровые файлы assets/iso/.

  Тайлы (128×256, ромб пола 128×64): копируются по требованию генератора карты —
      need_tile("Wall D1_N") -> assets/iso/tiles/wall_d1_n.png
  Персонажи (кадры 128×128, 8 направлений, 15 кадров): режутся этим скриптом —
      assets/iso/chars/<id>/<действие>/<направление>/<i>.png, направления s sw w nw n ne e se.
      Берём каждый второй кадр (8 из 15), обрезаем по общим границам всех кадров персонажа
      и увеличиваем в CHAR_SCALE раз: в наборе человек почти вчетверо ниже стены, а в Fallout — вдвое.

Запуск из папки game_project:  .venv/bin/python tools/slice_iso.py
"""
import glob
import json
import os
import shutil
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "iso", "2D HD Zombie City Tileset")
TILES_SRC = os.path.join(PACK, "Isometric Tiles")
SPRITES_SRC = os.path.join(PACK, "Animations", "Individual sprites")
OUT = os.path.join(ROOT, "assets", "iso")
CHAR_SCALE = 1.6
DIRS = {"S": "s", "SW": "sw", "W": "w", "NW": "nw", "N": "n", "NE": "ne", "E": "e", "SE": "se"}

# персонаж -> (папка в наборе, {наше действие: действие набора})
CHARS = {
    "hero": ("Survivor", {"idle": "Idle", "walk": "Run", "shoot": "Attack1", "melee": "Attack2",
                          "die": "Die", "runshoot": "AttackRun", "flash": "GunFire"}),
    "zombie1": ("CityZombie 1", {"idle": "Idle", "walk": "Walk", "run": "Run", "attack_melee": "Attack1",
                                 "hit": "TakeDamage", "die": "Die"}),
    "zombie3": ("CityZombie 3", {"idle": "Idle", "walk": "Walk", "run": "Run", "attack_melee": "Attack1",
                                 "hit": "TakeDamage", "die": "Die"}),
    "zombie5": ("CityZombie 5", {"idle": "Idle", "walk": "Walk", "run": "Run", "attack_melee": "Attack1",
                                 "hit": "TakeDamage", "die": "Die"}),
}


def tile_id(name):
    """«Wall D1_N» -> «wall_d1_n»."""
    return name.lower().replace(" ", "_")


# перекраски: «Ground D1_N@dust» — тёмная земля набора, высветленная в пыльный песок пустоши
TINTS = {
    "dust": {"mix": (150, 120, 86), "k": 0.3, "gain": 2.1},   # сохраняем крупинки, поднимаем в песок
}


def _tint(img, t):
    img = img.convert_alpha()
    w, h = img.get_size()
    mr, mg, mb = t["mix"]
    k, gain = t["k"], t["gain"]
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.get_at((x, y))
            if not a:
                continue
            r, g, b = (min(255, int(c * gain)) for c in (r, g, b))
            img.set_at((x, y), (int(r * (1 - k) + mr * k), int(g * (1 - k) + mg * k), int(b * (1 - k) + mb * k), a))
    return img


def need_tile(name):
    """Скопировать тайл набора в игру (если ещё нет). Возвращает id тайла.
    «Имя@перекраска» — копия, перекрашенная по TINTS."""
    base, _, tint = name.partition("@")
    tid = tile_id(base) + (f"_{tint}" if tint else "")
    dst = os.path.join(OUT, "tiles", tid + ".png")
    if not os.path.isfile(dst):
        src = os.path.join(TILES_SRC, base + ".png")
        if not os.path.isfile(src):
            raise FileNotFoundError(f"нет тайла «{base}» в наборе ({src})")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if tint:
            pygame.image.save(_tint(pygame.image.load(src), TINTS[tint]), dst)
        else:
            shutil.copyfile(src, dst)
    return tid


def slice_char(cid, folder, actions):
    src_root = os.path.join(SPRITES_SRC, folder)
    frames = {}
    union = None
    for act, src_act in actions.items():
        for d_src, d in DIRS.items():
            files = sorted(glob.glob(os.path.join(src_root, src_act, d_src, "*.png")))[::2]
            imgs = [pygame.image.load(f).convert_alpha() for f in files]
            frames[(act, d)] = imgs
            for im in imgs:
                bb = im.get_bounding_rect(min_alpha=12)
                union = bb if union is None else union.union(bb)
    dst = os.path.join(OUT, "chars", cid)
    shutil.rmtree(dst, ignore_errors=True)
    size = (round(union.w * CHAR_SCALE), round(union.h * CHAR_SCALE))
    # точка ног: низ стоячих кадров (с тенью) по центру — ею персонаж ставится на клетку
    idle = None
    for d in DIRS.values():
        for im in frames[("idle", d)]:
            bb = im.get_bounding_rect(min_alpha=60)
            idle = bb if idle is None else idle.union(bb)
    foot = (round((idle.centerx - union.x) * CHAR_SCALE), round((idle.bottom - 3 - union.y) * CHAR_SCALE))
    for (act, d), imgs in frames.items():
        folder_out = os.path.join(dst, act, d)
        os.makedirs(folder_out, exist_ok=True)
        for i, im in enumerate(imgs):
            pygame.image.save(pygame.transform.smoothscale(im.subsurface(union), size),
                              os.path.join(folder_out, f"{i}.png"))
    with open(os.path.join(dst, "anchor.json"), "w") as f:
        json.dump({"foot": foot, "size": size}, f)
    return size


def main():
    if not os.path.isdir(PACK):
        print(f"нет набора: {PACK}")
        return 1
    pygame.init()
    pygame.display.set_mode((1, 1))
    for cid, (folder, actions) in CHARS.items():
        size = slice_char(cid, folder, actions)
        print(f"{folder} -> assets/iso/chars/{cid}/  (кадр {size[0]}×{size[1]}, действий {len(actions)})")
    return 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
