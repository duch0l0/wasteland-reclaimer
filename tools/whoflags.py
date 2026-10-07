"""
Где в игре ставится флаг или выдаётся/забирается предмет: реплики диалогов (жилец@карта/узел),
записи терминалов (терминал@карта) и ящики на картах.

  .venv/bin/python tools/whoflags.py route_lira "голозапись деда"
  .venv/bin/python tools/whoflags.py sq_gang          # где двигаются стадии квеста
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

D = json.load(open("data/dialogues.json", encoding="utf-8"))
T = json.load(open("data/terminals.json", encoding="utf-8"))
MAPS = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in glob.glob("data/maps/*.json")}
TERM_AT = {t.get("id"): mid for mid, m in MAPS.items() for t in m.get("terminals", [])}
NPC_AT = {}
for mid, m in MAPS.items():
    for n in m.get("npcs", []):
        NPC_AT.setdefault(n[0], mid)


def find(key):
    for tid, t in D.items():
        for nid, n in t["nodes"].items():
            for o in n.get("options", []):
                for e in o.get("effects", []):
                    if e.get("flag") == key or e.get("item") == key or (e["type"] == "quest" and e.get("id") == key):
                        print(f"{key:22} {e['type']:9} {tid}@{NPC_AT.get(tid)}/{nid}: {o['label'][:50]!r} if={o.get('if', {})}")
    for section in ("terminals", "docs"):
        for tid, t in T[section].items():
            entries = t.get("entries", [t])
            for e in entries:
                if key in json.dumps(e.get("effects", []) + [e.get("if", {})], ensure_ascii=False):
                    lock = (e.get("lock") or {}).get("password")
                    print(f"{key:22} {section[:-1]:9} {tid}@{TERM_AT.get(tid)} {e.get('label', '')!r} lock={lock}")
    for mid, m in MAPS.items():
        for c in m.get("containers", []):
            if key in (c.get("loot") or {}):
                print(f"{key:22} ящик      {mid}: {c['name']!r} owner={c.get('owner')} requires={c.get('requires')}")


for k in sys.argv[1:]:
    find(k)
