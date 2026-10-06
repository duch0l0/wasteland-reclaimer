"""
Жители-гули для Некрополя: готовые листы жителей (assets/sprites/<id>/, кадры в игровом размере)
перекрашиваются так же, как мисс Лейн (tools/make_variants.py → make_ghoul_lady): кожа — серо-зелёная
в язвах, тёмные волосы — седые клочья, ткань — выцветшая.

  ghoul_a      из folk_c   — гуль-горожанин
  ghoul_b      из folk_e   — гуль в куртке
  ghoul_c      из folk_g   — старый гуль
  ghoul_d      из folk_h   — гуль-женщина
  ghoul_e      из folk_i   — гуль-работяга
  ghoul_set    из seer     — Сет, правитель Некрополя: балахон
  ghoul_cobbs  из soldier  — капрал Коббс: армейская форма
  ghoul_child  из kid      — гулёнок
  ghoul_cooper из sheriff  — Купер Говард, гуль в ковбойской шляпе и пыльнике
  spore_carrier из ghoul_c — споровик Убежища 22: тело проросло грибом
  super_mutant из soldier  — супермутант Создателя: на треть крупнее, серо-зелёная кожа

Запуск из папки game_project:
    .venv/bin/python tools/make_ghouls.py            — сделать кадры
    .venv/bin/python tools/make_ghouls.py preview    — и превью в assets/_preview_ghouls.png
"""
import os
import random
import shutil
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES = os.path.join(ROOT, "assets", "sprites")
DIRS = ("down", "right", "up", "left")

# id: (исходник, зерно, красить ли тёмные волосы — у каски Коббса и капюшона Сета не надо)
GHOULS = {"ghoul_a": ("folk_c", 11, True), "ghoul_b": ("folk_e", 12, True), "ghoul_c": ("folk_g", 13, True),
          "ghoul_d": ("folk_h", 14, True), "ghoul_e": ("folk_i", 15, True), "ghoul_set": ("seer", 16, False),
          "ghoul_cobbs": ("soldier", 17, False), "ghoul_child": ("kid", 18, True),
          "ghoul_cooper": ("sheriff", 19, False)}


def load(sid):
    out = {}
    for d in DIRS:
        folder = os.path.join(SPRITES, sid, d)
        names = sorted(os.listdir(folder), key=lambda n: int(n.split(".")[0]))
        out[d] = [pygame.image.load(os.path.join(folder, n)).convert_alpha() for n in names]
    return out


def ghoulify(src, seed, hair=True):
    r = random.Random(seed)
    out = {}
    for d, frames in load(src).items():
        out[d] = []
        for f in frames:
            img = f.copy()
            w, h = img.get_size()
            for y in range(h):
                for x in range(w):
                    c = img.get_at((x, y))
                    if c.a < 40:
                        continue
                    lum = (c.r + c.g + c.b) / 3
                    if c.r > 150 and c.r > c.g > c.b and c.r - c.b > 40:          # кожа
                        k = lum / 255
                        g = (int(110 + 70 * k), int(118 + 66 * k), int(84 + 40 * k))
                        if r.random() < 0.06:
                            g = (int(g[0] * 0.7), int(g[1] * 0.62), int(g[2] * 0.6))   # язвы
                        img.set_at((x, y), (*g, c.a))
                    elif hair and lum < 110 and abs(c.r - c.g) < 30 and y < h * 0.4:   # тёмные волосы -> седина
                        v = int(110 + lum * 0.6)
                        img.set_at((x, y), (v, v, int(v * 0.92), c.a))
                    elif lum > 40:                                                # ткань выцвела
                        img.set_at((x, y), (int(c.r * 0.8 + lum * 0.2), int(c.g * 0.8 + lum * 0.2),
                                            int(c.b * 0.75 + lum * 0.2), c.a))
            out[d].append(img)
    return out


def sporify(frames, seed=23):
    """Споровик (Убежище 22): тело проросло грибом — зелёные пятна и светящиеся бугорки."""
    r = random.Random(seed)
    out = {}
    for d, lst in frames.items():
        out[d] = []
        for f in lst:
            img = f.copy()
            w, h = img.get_size()
            for y in range(h):
                for x in range(w):
                    c = img.get_at((x, y))
                    if c.a < 40:
                        continue
                    lum = (c.r + c.g + c.b) / 3
                    g = (int(lum * 0.55), int(min(255, lum * 1.05 + 30)), int(lum * 0.45))
                    if r.random() < 0.05:
                        g = (200, 255, 140)              # светящиеся шляпки
                    img.set_at((x, y), (*g, c.a))
            out[d].append(img)
    return out


def supermutant(frames, k=1.35):
    """Супермутант Создателя (Марипоза): тот же боец, но на треть крупнее, кожа серо-зелёная, ткань — грязная."""
    out = {}
    for d, lst in frames.items():
        out[d] = []
        for f in lst:
            w, h = f.get_size()
            img = pygame.transform.scale(f, (round(w * k), round(h * k)))
            for y in range(img.get_height()):
                for x in range(img.get_width()):
                    c = img.get_at((x, y))
                    if c.a < 40:
                        continue
                    lum = (c.r + c.g + c.b) / 3
                    if c.r > 150 and c.r > c.g > c.b and c.r - c.b > 40:          # кожа -> серо-зелёная
                        q = lum / 255
                        img.set_at((x, y), (int(86 + 60 * q), int(112 + 70 * q), int(70 + 40 * q), c.a))
                    elif lum > 40:                                                # ткань и металл — грязнее
                        img.set_at((x, y), (int(c.r * 0.7 + 18), int(c.g * 0.7 + 16), int(c.b * 0.6 + 10), c.a))
            out[d].append(img)
    return out


def save(sid, frames, native=True):
    dst = os.path.join(SPRITES, sid)
    shutil.rmtree(dst, ignore_errors=True)
    for d, lst in frames.items():
        os.makedirs(os.path.join(dst, d), exist_ok=True)
        for i, img in enumerate(lst):
            pygame.image.save(img, os.path.join(dst, d, f"{i}.png"))
    if native:
        with open(os.path.join(dst, "native"), "w") as fh:
            fh.write("кадры уже в игровом размере\n")


def preview(ids, path):
    z = 3
    frames = [load(sid) for sid in ids]
    cw = max(i.get_width() for fr in frames for l in fr.values() for i in l) * z + 8
    ch = max(i.get_height() for fr in frames for l in fr.values() for i in l) * z + 8
    sheet = pygame.Surface((cw * 4, ch * len(ids)))
    sheet.fill((112, 100, 84))
    for r, fr in enumerate(frames):
        for c, d in enumerate(DIRS):
            s = pygame.transform.scale_by(fr[d][0], z)
            sheet.blit(s, (c * cw + 4, r * ch + ch - s.get_height() - 4))
    pygame.image.save(sheet, path)


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for sid, (src, seed, hair) in GHOULS.items():
        save(sid, ghoulify(src, seed, hair), os.path.isfile(os.path.join(SPRITES, src, "native")))
        print("готово:", sid)
    save("spore_carrier", sporify(load("ghoul_c")))
    print("готово: spore_carrier")
    save("super_mutant", supermutant(load("soldier"), 1.4))
    print("готово: super_mutant")
    if "preview" in sys.argv:
        path = sys.argv[sys.argv.index("preview") + 1] if len(sys.argv) > sys.argv.index("preview") + 1 \
            else os.path.join(ROOT, "assets", "_preview_ghouls.png")
        preview(list(GHOULS), path)
        print("превью:", path)


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
