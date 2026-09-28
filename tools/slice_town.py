"""
Нарезка набора «wasteland town» (5 страниц 768×768) в отдельные картинки.

  страница 1 — земля (клетки 48×48 по сетке), стены, заборы, дома, пятна земли:
               куски стоят вплотную, поэтому режем по координатам (PAGE1 ниже);
               боковых стен в наборе нет — собираем их из фасадов (make_vwall);
  страницы 2–5 — мебель, хлам, бочки, палатки, знаки, трава: объекты стоят
               порознь на прозрачном фоне — находим их автоматически по альфе.

Результат:
  assets/town/ground/<имя>.png   — клетки земли 48×48
  assets/town/props/<id>.png     — объекты (id: p1_<имя> или p<стр>_<номер>)
  assets/town/index.json         — откуда какой объект вырезан и его размер

Какой объект что означает в игре (имя, проходимость, обыск) — data/props.json.
Запуск из папки game_project:  .venv/bin/python tools/slice_town.py
"""
import json
import os
import sys

import pygame

SRC = "wasteland town"
OUT = os.path.join("assets", "town")

# ---- страница 1: клетки земли (x, y) по сетке 48
GROUND = {
    **{f"asphalt_{i}": (x, y) for i, (x, y) in enumerate(
        [(0, 432), (48, 432), (96, 432), (144, 432), (0, 480), (48, 480), (96, 480), (144, 480)])},
    "asphalt_line": (48, 528),                   # разметка (вертикальная полоса)
    **{f"gravel_{i}": (x, y) for i, (x, y) in enumerate(
        [(240, 432), (288, 432), (240, 480), (288, 480)])},
}

# ---- страница 1: объекты (x, y, w, h); картинка потом обрезается по непрозрачному
PAGE1 = {
    # стены: фасады высотой 96 px (две клетки)
    "wall_brick_long": (0, 96, 192, 96),
    "wall_brick_frag_l": (0, 0, 96, 96),
    "wall_brick_frag_r": (96, 0, 96, 96),
    "wall_concrete_broken2": (192, 0, 96, 96),
    "wall_concrete_brick": (288, 0, 96, 96),
    "wall_concrete_broken": (192, 96, 96, 96),
    "wall_concrete": (288, 96, 96, 96),
    "wall_grey_broken": (0, 192, 192, 96),
    "wall_brick_crumble": (0, 288, 192, 96),
    "wall_metal": (192, 192, 96, 96),
    "wall_corrugated": (288, 192, 96, 96),
    "wall_corrugated2": (192, 288, 96, 96),
    "wall_metal2": (288, 288, 96, 96),
    "wall_planks": (384, 0, 96, 96),
    "wall_planks_blue": (480, 0, 96, 96),
    "wall_corrugated_rust": (576, 0, 96, 96),
    "wall_corrugated_small": (672, 0, 96, 96),
    "wall_planks_dark": (384, 96, 96, 96),
    "fence_picket": (480, 96, 96, 96),
    "fence_broken": (576, 96, 96, 96),
    "fence_picket2": (672, 96, 96, 96),
    # руины и дома
    "ruin_facade_a": (384, 192, 192, 192),
    "ruin_facade_b": (576, 192, 192, 192),
    "house_a": (0, 576, 192, 192),
    "house_b": (192, 576, 192, 192),
    # пятна земли и завалы
    "rubble_heap": (384, 384, 96, 96),
    "dirt_planks": (480, 384, 96, 96),
    "dirt_patch": (384, 480, 96, 96),
    "dirt_slabs": (480, 480, 96, 48),
    "cobble": (528, 528, 48, 48),
    # сетка-рабица, доски, профлист — низкие заборы по 96×48
    "chain_a": (576, 384, 96, 48),
    "post_fence_a": (672, 384, 96, 48),
    "post_fence_b": (672, 432, 96, 48),
    "chain_broken_a": (576, 480, 96, 48),
    "chain_broken_b": (672, 480, 96, 48),
    "chain_broken_c": (576, 528, 96, 48),
    "chain_b": (672, 528, 96, 48),
    "chain_c": (384, 576, 96, 48),
    "plank_fence_a": (480, 576, 48, 48),
    "plank_fence_b": (480, 624, 96, 48),
    "chain_broken_d": (576, 576, 96, 48),
    "bar_fence_a": (672, 576, 96, 48),
    "bar_fence_b": (672, 624, 96, 48),
    "chain_d": (384, 672, 96, 48),
    "chain_broken_e": (480, 672, 96, 48),
    "chain_broken_f": (576, 672, 96, 48),
    "corrugated_panel": (672, 672, 96, 48),
    "bar_fence_c": (384, 720, 96, 48),
    "chain_e": (480, 720, 96, 48),
    "corrugated_b": (576, 720, 96, 48),
    "metal_sheet": (672, 720, 96, 48),
}

# на странице 4 бочки стоят столбиками вплотную — эти рамки делим пополам по высоте
SPLIT_VERTICAL = {4: {2, 3, 7}}


def trim(surf):
    """Обрезать прозрачные поля."""
    r = surf.get_bounding_rect(min_alpha=8)
    return surf.subsurface(r).copy() if r.w and r.h else surf


def detect(im):
    """Рамки отдельных объектов: связные области плотных пикселей; вложенные
    и сильно перекрытые куски склеиваются, мелкие обрывки — к соседу."""
    mask = pygame.mask.from_surface(im, 128)
    rects = [pygame.Rect(c.get_bounding_rects()[0]) for c in mask.connected_components(30)]
    changed = True
    while changed:
        changed = False
        rects.sort(key=lambda r: -r.w * r.h)
        for i, a in enumerate(rects):
            for j in range(i + 1, len(rects)):
                b = rects[j]
                inter = a.clip(b)
                small = b.w * b.h
                if inter.w * inter.h > 0.4 * small or (a.inflate(4, 4).colliderect(b) and small < 500):
                    rects[i] = a.union(b)
                    rects.pop(j)
                    changed = True
                    break
            if changed:
                break
    rects = [r for r in rects if r.w * r.h >= 150 and r.w >= 8 and r.h >= 8]
    rects.sort(key=lambda r: (r.centery // 48, r.x))
    return rects


def cut_object(im, rect, soft_parts):
    """Вырезать объект вместе с тенью (мягкие пиксели), но без кусков соседей.
    Мягкий кусок целиком рядом с объектом — берём с тенью; если он тянется
    дальше (тени соседей слились) — берём только в пределах рамки объекта."""
    area = rect.inflate(8, 8).clip(im.get_rect())
    out = pygame.Surface(area.size, pygame.SRCALPHA)
    for part_rect, part_mask in soft_parts:
        if not part_rect.colliderect(rect):
            continue
        limit = area if area.contains(part_rect) else rect.inflate(2, 2).clip(im.get_rect())
        clip = part_rect.clip(limit)
        if not clip.w or not clip.h:
            continue
        m = pygame.mask.Mask(clip.size)
        m.draw(part_mask, (-clip.x, -clip.y))  # маски компонент — в координатах всей страницы
        piece = pygame.Surface(clip.size, pygame.SRCALPHA)
        piece.blit(im, (0, 0), clip)
        # пиксели вне маски — прозрачные: умножаем на белое/прозрачное по маске
        stencil = m.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        piece.blit(stencil, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        out.blit(piece, (clip.x - area.x, clip.y - area.y))
    return trim(out)


def split_vertical(rect, im):
    """Разрезать рамку по самой пустой строке у середины (две бочки друг над другом)."""
    best, best_y = None, None
    for y in range(rect.y + rect.h // 3, rect.y + rect.h * 2 // 3):
        filled = sum(1 for x in range(rect.x, rect.right) if im.get_at((x, y)).a > 128)
        if best is None or filled < best:
            best, best_y = filled, y
    return [pygame.Rect(rect.x, rect.y, rect.w, best_y - rect.y),
            pygame.Rect(rect.x, best_y, rect.w, rect.bottom - best_y)]


# боковые стены (идут с севера на юг): в наборе их нет — собираем из фасадов
VWALL_FROM = {"brick": "wall_brick_long", "concrete": "wall_concrete", "metal": "wall_metal", "planks": "wall_planks"}
VWALL_W = 20  # толщина стены в пикселях


def make_vwall(facade, side):
    """Кусок боковой стены на одну клетку, картинка 48×96 (как фасад высотой в 2 клетки).
    Верхняя половина — верх стены (кромка фасада, повёрнутая вдоль стены),
    нижняя — торец (кладка фасада, в тени). Куски, стоящие друг под другом,
    перекрываются так, что торец виден только у самого южного."""
    fw, fh = facade.get_size()
    cap_src = facade.subsurface((fw // 2 - 24, 1, 48, 14)).copy()
    cap = pygame.transform.rotate(cap_src, 90)                 # 14×48
    cap = pygame.transform.scale(cap, (VWALL_W, 48))
    cap.fill((16, 14, 12, 0), special_flags=pygame.BLEND_RGBA_ADD)  # верх стены на свету — чуть светлее
    face = facade.subsurface((fw // 2 - VWALL_W // 2, fh - 48, VWALL_W, 48)).copy()
    face.fill((170, 160, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)  # торец в тени
    strip = pygame.Surface((VWALL_W, 96), pygame.SRCALPHA)
    strip.blit(cap, (0, 0))
    strip.blit(face, (0, 48))
    edge = (45, 36, 28)
    pygame.draw.line(strip, edge, (0, 0), (0, 95))
    pygame.draw.line(strip, edge, (VWALL_W - 1, 0), (VWALL_W - 1, 95))
    pygame.draw.line(strip, edge, (0, 48), (VWALL_W - 1, 48))
    out = pygame.Surface((48, 96), pygame.SRCALPHA)
    out.blit(strip, (0 if side == "w" else 48 - VWALL_W, 0))  # западная стена — у левого края клетки
    return out


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    os.makedirs(os.path.join(OUT, "ground"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "props"), exist_ok=True)
    index = {}

    page1 = pygame.image.load(os.path.join(SRC, "page_01.png"))
    for name, (x, y) in GROUND.items():
        pygame.image.save(page1.subsurface((x, y, 48, 48)), os.path.join(OUT, "ground", f"{name}.png"))
    for name, rect in PAGE1.items():
        img = trim(page1.subsurface(rect).copy())
        pid = f"p1_{name}"
        pygame.image.save(img, os.path.join(OUT, "props", f"{pid}.png"))
        index[pid] = {"page": 1, "rect": list(rect), "size": list(img.get_size())}
    for style, facade in VWALL_FROM.items():
        src = pygame.image.load(os.path.join(OUT, "props", f"p1_{facade}.png"))
        for side in ("w", "e"):
            pid = f"p1_vwall_{style}_{side}"
            pygame.image.save(make_vwall(src, side), os.path.join(OUT, "props", f"{pid}.png"))
            index[pid] = {"page": 1, "rect": None, "size": [48, 96], "made_from": facade}

    for n in range(2, 6):
        im = pygame.image.load(os.path.join(SRC, f"page_0{n}.png"))
        soft = pygame.mask.from_surface(im, 8)
        soft_parts = [(pygame.Rect(c.get_bounding_rects()[0]), c) for c in soft.connected_components(4)]
        rects = []
        for i, r in enumerate(detect(im)):
            rects.extend(split_vertical(r, im) if i in SPLIT_VERTICAL.get(n, ()) else [r])
        for i, r in enumerate(rects):
            img = cut_object(im, r, soft_parts)
            pid = f"p{n}_{i:03d}"
            pygame.image.save(img, os.path.join(OUT, "props", f"{pid}.png"))
            index[pid] = {"page": n, "rect": list(r), "size": list(img.get_size())}
        print(f"стр. {n}: {len(rects)} объектов")

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"земля: {len(GROUND)} клеток, объектов всего: {len(index)} -> {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
