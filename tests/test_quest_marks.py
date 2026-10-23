"""
Отметка квестодателя у курсора (Game.quest_mark): «есть дело» — реплика начнёт квест,
«ждёт ответа» — двинет начатый, иначе ничего. Над головой значков нет — только подсказка и контур.

    .venv/bin/python tests/test_quest_marks.py
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

pygame.mouse.get_pos = lambda: (-50, -50)
pygame.mouse.get_focused = lambda: True

from src.game import Game, saveload  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


g = Game(intro=False)
for _ in range(3):
    g.update(16)

ok(g.quest_mark("gena") == "new", "Гена в начале: есть дело (лом)")
ok(g.quest_mark("sheriff") == "new", "шериф в начале: есть дело (крысы)")
ok(g.quest_mark("нет_такого") is None, "житель без дерева диалога — без отметки")

# квест взят, лома нет — Гене пока нечего сказать по делу; принёс — ждёт ответа
g.flags["q_scrap_taken"] = True
g.set_stage("sq_scrap", 10)
g.set_stage("mq_grandpa", 100)            # главный квест здесь не мешает
mark_empty = g.quest_mark("gena")
ok(mark_empty != "turn_in", f"взял задание без лома — не «ждёт ответа» ({mark_empty})")
g.inventory.add("лом", 3)
ok(g.quest_mark("gena") == "turn_in", "три лома в рюкзаке — Гена ждёт ответа")
g.flags["q_scrap_done"] = True
g.set_stage("sq_scrap", 100)
g.inventory.remove("лом", 3)
ok(g.quest_mark("gena") != "turn_in", "сдал — отметка «ждёт ответа» снята")

# подсказка у курсора и контур
from src.game import mouse  # noqa: E402
ok(mouse.QUEST_MARKS["new"] == "есть дело" and mouse.QUEST_OUTLINE != mouse.TALK_OUTLINE,
   "у квестодателя свой контур и строка «есть дело»")

print("\nИТОГ:", "всё прошло" if not failed else f"провалено {len(failed)}")
sys.exit(1 if failed else 0)
