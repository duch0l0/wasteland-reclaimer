"""
Экскурсия по городам: обойти каждую локацию, снять карту целиком сверху и собрать замечания о визуале и
атмосфере — как придирчивый игрок, который не торопится по квестам, а гуляет.

  .venv/bin/python tools/city_tour.py <папка> [локация …]

На выходе: <папка>/<локация>.png — вся карта, уменьшенная до ~1600 px по ширине, и <папка>/tour.md — отчёт:
  пустыри      — участки 8×8 проходимых клеток без единого объекта, жителя, ящика;
  плотность    — объектов на 100 проходимых клеток (меньше 6 — голо, больше 45 — свалка);
  жители       — сколько, у кого одна реплика («картонные»), «близнецы» (тот же лист и вариант в 6 клетках);
  голоса       — сколько слухов у города (barks @город) и своих реплик у жителей;
  заглушки     — жители и враги без нарисованных кадров;
  ящики        — пустые контейнеры;
  ночь/свет    — ночные карты без источников света, интерьеры без музыки.
"""
import json
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402
from src.combat import tile_of  # noqa: E402
from src.location import LOCATION_DEFS, NPC_SPRITES, npc_variant  # noqa: E402
from src.game.reputation import town_of  # noqa: E402
from src.ui.common import PANEL_H  # noqa: E402
from src import settings as S  # noqa: E402

T = S.TILE
BARKS = json.load(open("data/barks.json", encoding="utf-8"))
DLG = json.load(open("data/dialogues.json", encoding="utf-8"))


def stitch(g, out_w=1600):
    """Вся карта: камера шагает по сетке, кадры склеиваются (без панели), потом уменьшение."""
    lvl = g.level
    if getattr(lvl, "iso", False):
        g.update(16)
        g.draw()
        return g.screen.subsurface((0, 0, S.SCREEN_W, S.SCREEN_H - PANEL_H)).copy()
    W, H = lvl.width * T, lvl.height * T
    vw, vh = S.SCREEN_W, S.SCREEN_H - PANEL_H
    big = pygame.Surface((W, H))
    g.zoom = 1
    g.apply_view()
    g.minimap.mode = "off"
    for y in range(0, H, vh):
        for x in range(0, W, vw):
            g.cam.x, g.cam.y = min(x, max(0, W - vw)), min(y, max(0, H - vh))
            g.draw()
            big.blit(g.screen.subsurface((0, 0, min(vw, W), min(vh, H))), (g.cam.x, g.cam.y))
    k = min(1.0, out_w / W)
    return pygame.transform.smoothscale(big, (int(W * k), int(H * k)))


def critique(g, lid):
    lvl = g.level
    notes, stats = [], {}
    walk = {(x, y) for x in range(lvl.width) for y in range(lvl.height) if not lvl.is_wall(x, y)}
    things = set()
    for o in getattr(lvl, "objects", []):
        if not o.get("hidden"):
            things.update(o["foot"])
            fx, fy = o["foot"][0]
            things.update({(fx + dx, fy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)})
    things.update(tile_of(n) for n in g.npcs)
    things.update(tile_of(e) for e in g.enemies)
    for c in getattr(lvl, "containers", []):
        things.update(c.get("tiles", []))
    props = len([o for o in getattr(lvl, "objects", []) if not o.get("hidden")])
    dens = 100 * props / max(1, len(walk))
    stats["density"] = round(dens, 1)
    if getattr(lvl, "iso", False):
        stats["iso"] = True
    elif dens < 6 and hasattr(lvl, "objects"):
        notes.append(f"голо: {dens:.1f} объектов на 100 клеток — улица выглядит пустой")
    elif dens > 45:
        notes.append(f"свалка: {dens:.1f} объектов на 100 клеток — тесно, глаз не цепляется")
    empty = []
    if not getattr(lvl, "iso", False) and hasattr(lvl, "objects"):
        for by in range(0, lvl.height - 7, 4):
            for bx in range(0, lvl.width - 7, 4):
                block = {(bx + i, by + j) for i in range(8) for j in range(8)}
                if len(block & walk) >= 56 and not block & things:
                    empty.append((bx, by))
    stats["empty_8x8"] = len(empty)
    if len(empty) >= 6:
        notes.append(f"пустыри: {len(empty)} участков 8×8 без единой детали (например, у {empty[0]})")
    # жители
    npcs = list(g.npcs)
    stats["npcs"] = len(npcs)
    flat = [n.npc_id for n in npcs if n.npc_id in DLG and len(DLG[n.npc_id]["nodes"]) <= 1
            and len(DLG[n.npc_id]["nodes"][next(iter(DLG[n.npc_id]["nodes"]))]["options"]) <= 2]
    if flat:
        notes.append(f"картонные жители (одна реплика): {', '.join(flat[:8])}" + (" …" if len(flat) > 8 else ""))
    no_dlg = [n.npc_id for n in npcs if n.npc_id not in DLG]
    if no_dlg:
        notes.append(f"жители без диалога: {', '.join(no_dlg)}")
    twins = set()
    for i, a in enumerate(npcs):
        for b in npcs[i + 1:]:
            sa, sb = NPC_SPRITES.get(a.npc_id, a.npc_id), NPC_SPRITES.get(b.npc_id, b.npc_id)
            if sa == sb and npc_variant(a.npc_id) == npc_variant(b.npc_id) and \
                    max(abs(tile_of(a)[0] - tile_of(b)[0]), abs(tile_of(a)[1] - tile_of(b)[1])) <= 6:
                twins.add(f"{a.npc_id}+{b.npc_id}")
    if twins:
        notes.append(f"близнецы рядом: {', '.join(sorted(twins))}")
    town = town_of(lid)
    rumors = len(BARKS.get(f"@{town}", [])) if town else 0
    own = sum(len(BARKS.get(n.npc_id, [])) for n in npcs)
    stats["rumors"], stats["own_barks"] = rumors, own
    if npcs and town and rumors < 5:
        notes.append(f"тихий город: всего {rumors} слухов на «{town}» — жители почти не обсуждают события")
    if len(npcs) >= 4 and own == 0 and not rumors:
        notes.append("никто не бормочет на ходу — ни своих реплик, ни слухов")
    # заглушки и ящики
    from src.location import npc_animations  # noqa
    ph = [n.npc_id for n in npcs
          if not os.path.isdir(os.path.join(S.ASSET_ROOT, "sprites", NPC_SPRITES.get(n.npc_id, n.npc_id)))]
    if ph:
        notes.append(f"заглушки вместо спрайтов: {', '.join(ph)}")
    empty_boxes = [c["name"] for c in getattr(lvl, "containers", []) if not c.get("loot") and not c.get("corpse")]
    stats["boxes"], stats["empty_boxes"] = len(getattr(lvl, "containers", [])), len(empty_boxes)
    if len(empty_boxes) >= 4 and len(empty_boxes) > len(lvl.containers) // 2:
        notes.append(f"пустые ящики: {len(empty_boxes)} из {stats['boxes']} — обыскивать скучно")
    d = LOCATION_DEFS[lid]
    from src.lighting import light_sources
    if getattr(lvl, "night", None) and not light_sources(lvl):
        notes.append("ночная карта без источников света — темно и плоско")
    if not d.get("music"):
        notes.append("нет своей музыки")
    stats["enemies"] = len(g.enemies)
    stats["terminals"] = len(getattr(lvl, "terminals", []))
    return notes, stats


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    only = sys.argv[2:]
    saveload.SAVE_DIR = tempfile.mkdtemp()
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 6
    report = ["# Экскурсия по городам\n"]
    ids = [lid for lid, d in LOCATION_DEFS.items() if not lid.startswith("_") and (d.get("map") or d.get("scene"))]
    for lid in ids:
        if only and not any(lid.startswith(o) for o in only):
            continue
        try:
            g.enter_location(lid)
        except Exception as ex:   # noqa: BLE001 — экскурсия не падает на одной карте
            report.append(f"## {lid}\n- НЕ ЗАГРУЗИЛАСЬ: {ex}\n")
            continue
        g.slides = None
        g.dialogue.active_node = None
        for _ in range(3):
            g.update(16)
        notes, stats = critique(g, lid)
        img = stitch(g)
        pygame.image.save(img, os.path.join(out, f"{lid}.png"))
        report.append(f"## {lid} — {g.loc.name}\n`{json.dumps(stats, ensure_ascii=False)}`\n")
        report += [f"- {n}" for n in notes] or ["- замечаний нет"]
        report.append("")
        print(lid, len(notes), flush=True)
    open(os.path.join(out, "tour.md"), "w", encoding="utf-8").write("\n".join(report))


if __name__ == "__main__":
    main()
