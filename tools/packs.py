"""
Наборы Cute SCKR (бандл, 480+ наборов) -> картинки игры. Нарезается только то, что нужно
городу: `slice_pack(slug, short)` по одному набору.

Исходники — ../tilesets_sckr/<автор>/<slug>/extracted/<архив>/*.png (вне git: лицензия
запрещает распространять исходники; распаковка — ../tilesets_sckr/extract.sh). Страницы трёх видов:

  объекты (tile-B-*.png, 1.png, page_*.png; 768×768) — дома, мебель, машины, деревья: каждый
      объект стоит порознь на прозрачном фоне, находим по альфе (как tools/slice_town.py);
  земля A2 (Tile_A2*.png, 768×576) — 32 автотайла RPG Maker по 96×144: верх 96×48 —
      превью и внутренние углы, низ 96×96 — «остров» 2×2 с краями; середина острова —
      бесшовная заливка 48×48 (пол, песок, асфальт);
  стены A4 (Auto-tile-A4-walls*.png, 768×720) — 8 столбцов × 3 ряда пар: «потолок» —
      автотайл 96×144 (верх стены, тёмный с окантовкой), под ним фасад стены 96×96.

Результат: assets/packs/<short>/
  props/<short>_<стр>_<n>.png   объекты (одинаковые — один раз)
  pages/p<N>.png                страницы целиком — из них берутся куски по клеткам 48
  floor/<short>_f<стр>_<n>.png  заливки 48×48 и floor/<…>_auto.png — весь автотайл 96×144
  walls/<short>_w<стр>_<n>_top.png (96×144) и _face.png (96×96)
  index.json                    размеры всех картинок
Сводки для подбора — ../tilesets_sckr/_catalog/<short>_p<N>.png: страница с сеткой 48 (номера клеток
по краям) и рамками авто-объектов; <short>_floor.png, <short>_walls.png — полы и стены плиткой.

Запуск из папки game_project:
  .venv/bin/python tools/packs.py find <слово>          — какие наборы есть по слову
  .venv/bin/python tools/packs.py slice <slug> <short>  — нарезать набор (и сводки)
  .venv/bin/python tools/packs.py sync-git              — в git только используемое (перед коммитом)
"""
import glob
import hashlib
import json
import os
import re
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(ROOT), "tilesets_sckr")
OUT = os.path.join(ROOT, "assets", "packs")
CATALOG = os.path.join(SRC, "_catalog")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def pack_dir(slug):
    hits = glob.glob(os.path.join(SRC, "*", slug))
    if not hits:
        raise FileNotFoundError(f"нет набора {slug} в {SRC}")
    return hits[0]


def find(word):
    word = word.lower()
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(SRC, "*", "*"))
                  if os.path.isdir(p) and word in os.path.basename(p).lower())


def pages(slug):
    """{'objects': [...], 'floor': [...], 'walls': [...]} — пути страниц набора."""
    out = {"objects": [], "floor": [], "walls": []}
    for p in sorted(glob.glob(os.path.join(pack_dir(slug), "extracted", "**", "*.png"), recursive=True)):
        name = os.path.basename(p).lower()
        try:
            w, h = pygame.image.load(p).get_size()
        except pygame.error:
            continue
        if "a4" in name and (w, h) == (768, 720):
            out["walls"].append(p)
        elif "a2" in name and (w, h) == (768, 576):
            out["floor"].append(p)
        elif (w, h) == (768, 768):
            out["objects"].append(p)
    return out


def _tag(path, i):
    """Короткий номер страницы для имени файла: tile-B-03 -> 3, 'Tile_A2-1 (2)' -> 1b…"""
    nums = re.findall(r"\d+", os.path.basename(path))
    return (nums[-1] if nums else str(i)).lstrip("0") or "0"


def _save(img, folder, name, index):
    os.makedirs(folder, exist_ok=True)
    pygame.image.save(img, os.path.join(folder, name + ".png"))
    index[name] = {"size": list(img.get_size()), "dir": os.path.basename(folder)}


def slice_objects(paths, short, folder, index):
    from slice_town import detect, cut_object
    seen, made = set(), []
    for i, p in enumerate(paths):
        im = pygame.image.load(p)
        soft = pygame.mask.from_surface(im, 8)
        soft_parts = [(pygame.Rect(c.get_bounding_rects()[0]), c) for c in soft.connected_components(4)]
        tag = f"{i + 1}"
        for n, r in enumerate(detect(im)):
            img = cut_object(im, r, soft_parts)
            h = hashlib.md5(pygame.image.tobytes(img, "RGBA") + bytes(str(img.get_size()), "ascii")).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            name = f"{short}_{tag}_{n:03d}"
            _save(img, folder, name, index)
            made.append((name, p, r))
    return made


def copy_pages(paths, short, index):
    """Страницы объектов целиком: многие — готовые композиции (земля с дорожками, озеро с берегом,
    дом на песке), автоматически их не разрезать. Из страницы берётся любой прямоугольник по клеткам 48:
    картинка «pk:<short>/p<N>/<x>,<y>,<ш>,<в>» (см. src/props.py)."""
    folder = os.path.join(OUT, short, "pages")
    os.makedirs(folder, exist_ok=True)
    for i, p in enumerate(paths):
        img = pygame.image.load(p)
        pygame.image.save(img, os.path.join(folder, f"p{i + 1}.png"))
        index[f"p{i + 1}"] = {"size": list(img.get_size()), "dir": "pages"}


def slice_floors(paths, short, folder, index):
    made = []
    for i, p in enumerate(paths):
        im = pygame.image.load(p)
        for k in range(32):
            cx, cy = (k % 8) * 96, (k // 8) * 144
            block = im.subsurface((cx, cy, 96, 144))
            if pygame.mask.from_surface(block, 250).count() < 96 * 144 * 0.9:
                continue                                    # пустая ячейка страницы
            name = f"{short}_f{i + 1}_{k:02d}"
            _save(block.subsurface((24, 72, 48, 48)).copy(), folder, name, index)   # середина острова
            _save(block.copy(), folder, name + "_auto", index)
            made.append(name)
    return made


def slice_walls(paths, short, folder, index):
    made = []
    for i, p in enumerate(paths):
        im = pygame.image.load(p)
        for row in range(3):
            for col in range(8):
                x, y = col * 96, row * 240
                top = im.subsurface((x, y, 96, 144))
                face = im.subsurface((x, y + 144, 96, 96))
                if pygame.mask.from_surface(face, 250).count() < 96 * 96 * 0.9:
                    continue
                name = f"{short}_w{i + 1}_{row * 8 + col:02d}"
                _save(top.copy(), folder, name + "_top", index)
                _save(face.copy(), folder, name + "_face", index)
                made.append(name)
    return made


def catalog(short, objects, floors, walls, pages_list=()):
    """Сводки с номерами: объекты по страницам (как на исходнике), полы и стены — плиткой."""
    os.makedirs(CATALOG, exist_ok=True)
    font = pygame.font.SysFont(None, 16)
    by_page = {p: [] for p in pages_list}
    for name, p, r in objects:
        by_page.setdefault(p, []).append((name, r))
    for k, (p, items) in enumerate(by_page.items()):
        im = pygame.image.load(p)
        sheet = pygame.Surface(im.get_size())
        sheet.fill((90, 80, 70))
        sheet.blit(im, (0, 0))
        grid = pygame.Surface(im.get_size(), pygame.SRCALPHA)   # сетка 48 с номерами клеток
        for g in range(0, im.get_width(), 48):
            pygame.draw.line(grid, (0, 255, 255, 70), (g, 0), (g, im.get_height()))
            pygame.draw.line(grid, (0, 255, 255, 70), (0, g), (im.get_width(), g))
            grid.blit(font.render(str(g // 48), True, (0, 255, 255)), (g + 2, 2))
            grid.blit(font.render(str(g // 48), True, (0, 255, 255)), (2, g + 2))
        sheet.blit(grid, (0, 0))
        for name, r in items:
            pygame.draw.rect(sheet, (255, 255, 0), r, 1)
            sheet.blit(font.render(name.split("_", 1)[1], True, (255, 255, 255), (0, 0, 0)), r.topleft)
        pygame.image.save(sheet, os.path.join(CATALOG, f"{short}_p{k + 1}.png"))
    for kind, names, folder, suffix, size in (("floor", floors, "floor", "", (48, 48)),
                                              ("walls", walls, "walls", "_face", (96, 96))):
        if not names:
            continue
        cols = 8
        cw, ch = size[0] + 8, size[1] + 18
        sheet = pygame.Surface((cols * cw, ((len(names) + cols - 1) // cols) * ch))
        sheet.fill((60, 56, 50))
        for i, n in enumerate(names):
            img = pygame.image.load(os.path.join(OUT, short, folder, n + suffix + ".png"))
            x, y = (i % cols) * cw, (i // cols) * ch
            sheet.blit(img, (x + 4, y + 16))
            sheet.blit(font.render(n.split("_", 1)[1], True, (255, 255, 255)), (x + 2, y + 2))
        pygame.image.save(sheet, os.path.join(CATALOG, f"{short}_{kind}.png"))


def slice_pack(slug, short):
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))
    pg = pages(slug)
    base = os.path.join(OUT, short)
    index_path = os.path.join(base, "index.json")
    index = {}
    objs = slice_objects(pg["objects"], short, os.path.join(base, "props"), index)
    floors = slice_floors(pg["floor"], short, os.path.join(base, "floor"), index)
    walls = slice_walls(pg["walls"], short, os.path.join(base, "walls"), index)
    os.makedirs(base, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"slug": slug, "items": index}, f, ensure_ascii=False, indent=0)
    copy_pages(pg["objects"], short, index)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({"slug": slug, "items": index}, f, ensure_ascii=False, indent=0)
    catalog(short, objs, floors, walls, pg["objects"])
    print(f"{slug} -> {short}: объектов {len(objs)}, страниц {len(pg['objects'])}, полов {len(floors)}, стен {len(walls)}")
    return objs, floors, walls


def used_files():
    """Файлы assets/packs, на которые ссылаются карты и каталоги объектов (картинки «pk:…»)."""
    refs = set()
    for path in glob.glob(os.path.join(ROOT, "data", "props", "*.json")):
        with open(path, encoding="utf-8") as f:
            refs.update(d["img"] for d in json.load(f).get("props", {}).values() if d["img"].startswith("pk:"))
    for path in glob.glob(os.path.join(ROOT, "data", "maps", "*.json")):
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
        for imgs in (m.get("floors") or {}).values():
            refs.update(imgs)
        for w in (m.get("walls") or {}).values():
            refs.update((w + "_top", w + "_face"))
    files = set()
    for ref in refs:
        short, rest = ref[3:].split("/", 1)
        files.add(os.path.join("assets", "packs", short, "index.json"))
        if "/" in rest:                                    # кусок страницы — нужна вся страница
            files.add(os.path.join("assets", "packs", short, "pages", rest.split("/")[0] + ".png"))
        else:
            with open(os.path.join(OUT, short, "index.json"), encoding="utf-8") as f:
                d = json.load(f)["items"][rest]
            files.add(os.path.join("assets", "packs", short, d["dir"], rest + ".png"))
    return sorted(files)


def sync_git():
    """В git — только то, что используется: остальная нарезка лежит на диске (assets/packs в .gitignore)
    и при новой сборке пересоздаётся из бандла. Используемые файлы добавляются принудительно,
    ставшие ненужными — убираются из индекса git (с диска не удаляются)."""
    import subprocess
    used = used_files()
    missing = [f for f in used if not os.path.isfile(os.path.join(ROOT, f))]
    assert not missing, f"нет файлов: {missing[:5]}"
    tracked = subprocess.run(["git", "ls-files", "assets/packs"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.split()
    stale = sorted(set(tracked) - set(used))
    for i in range(0, len(stale), 500):
        subprocess.run(["git", "rm", "--cached", "-q", *stale[i:i + 500]], cwd=ROOT, check=True)
    for i in range(0, len(used), 500):
        subprocess.run(["git", "add", "-f", *used[i:i + 500]], cwd=ROOT, check=True)
    size = sum(os.path.getsize(os.path.join(ROOT, f)) for f in used)
    print(f"в git из наборов: {len(used)} файлов, {size / 1e6:.1f} МБ; убрано из индекса: {len(stale)}")


def main():
    os.chdir(ROOT)
    if len(sys.argv) >= 2 and sys.argv[1] == "sync-git":
        sync_git()
        return
    if len(sys.argv) >= 3 and sys.argv[1] == "find":
        print("\n".join(find(sys.argv[2])))
    elif len(sys.argv) >= 4 and sys.argv[1] == "slice":
        slice_pack(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
