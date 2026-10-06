"""
У всех жителей и врагов на обычных (не изометрических) картах есть кадры — никаких цветных заглушек.

    .venv/bin/python tests/test_sprites.py
"""
import glob
import json
import os
import re
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src.location import NPC_SPRITES, ENEMY_DEFS  # noqa: E402

SPECIAL = {"robot"}          # робот-почтальон рисуется отдельно (src/location.py)
missing = []
enemies = set(re.findall(r'"(\w+)"', open("src/encounters.py", encoding="utf-8").read())) & set(ENEMY_DEFS)
for f in glob.glob("data/maps/*.json"):
    m = json.load(open(f, encoding="utf-8"))
    if m.get("iso"):
        continue
    enemies |= {e[0] for e in m.get("enemies", [])}
    for nid, *_ in m.get("npcs", []):
        if nid not in SPECIAL and not os.path.isdir(f"assets/sprites/{NPC_SPRITES.get(nid, nid)}"):
            missing.append(f"житель {nid} ({os.path.basename(f)})")
for t in sorted(enemies):
    if not os.path.isdir(f"assets/sprites/{ENEMY_DEFS[t].get('sprite_dir', t)}"):
        missing.append(f"враг {t}")
for m in missing:
    print("FAIL без кадров:", m)
print("ИТОГ:", "всё прошло" if not missing else f"провалов: {len(missing)}")
sys.exit(1 if missing else 0)
