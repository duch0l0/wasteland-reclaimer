"""
Испытания Ордена Тайн (терминал святилища под «Миражом», Барстоу): укради, не убив; обмани, не солгав;
спаси, не будучи увиденным — засчитываются по делам в разных городах, знак ложи открывает концовку «Пепел».

    .venv/bin/python tests/test_order.py
"""
import os
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

from src.game import Game, saveload  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def press(g, part):
    g.open_terminal("order")
    entries = g.term_entries()
    idx = next((k for k, (_, e) in enumerate(entries) if part in e.get("label", "")), None)
    if idx is not None:
        g.term_open_entry(idx)
    g.close_terminal()
    return idx is not None


g = Game(intro=False)
press(g, "Приветствие")
ok(g.flags.get("order_found"), "святилище: Орден знает о герое")
ok(not press(g, "Испытание I"), "испытание не засчитать без дела")
g.flags.update({"gizmo_exposed": True, "nipton_mayor_drawn": True, "darnell_free": True})
for t in ("Испытание I", "Испытание II", "Испытание III"):
    ok(press(g, t), f"засчитано: {t}")
ok(press(g, "Принять знак"), "три испытания — знак ложи")
ok(g.flags.get("order_member") and g.flags.get("order_contact") and g.inventory.has("золотой знак Ордена"),
   "герой — член ложи; у пульта Марипозы откроется «Пепел»")
print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
