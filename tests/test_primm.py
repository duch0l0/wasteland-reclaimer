"""
Примм (tools/build_primm.py) — без окна: расследование «Шериф умер дважды»: улики, признание вдовы,
код на фишке, лагерь культа и мальчик Тоби; письмо деда 2077 года.

    .venv/bin/python tests/test_primm.py
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
from src.combat import tile_of, rect_pos_for_tile  # noqa: E402

saveload.SAVE_DIR = tempfile.mkdtemp()
failed = []


def ok(cond, msg):
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        failed.append(msg)


def fr(g, n=3):
    for _ in range(n):
        g.update(16)
        g.draw()
        while g.perk_choices:          # новый уровень за квесты — выбрать первое
            g.handle_key(pygame.K_1)


def goto(g, t):
    g.player.rect.topleft = rect_pos_for_tile(g.player, t)
    g.snap_camera()
    fr(g)


def portal(g, to):
    return next(p for p in g.level.portals if p["to"] == to)


def stand_near(g, t):
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (t[0] + dx, t[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            g.snap_camera()
            return


g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6


def say(part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def talk(nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    stand_near(g, tile_of(npc))
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid









g.enter_location("vault4")
fr(g)
g.sync_story()
ok("primm" in g.worldmap.known, "после Убежища 4 на карте — Примм (акт III)")
g.enter_location("primm")
fr(g)
ok(g.loc.id == "primm" and len(g.npcs) >= 8, "Примм: трасса, отель, казино, горки")
for to in ("primm_bison", "primm_vikki"):
    goto(g, sorted(portal(g, to)["tiles"])[0])
    ok(g.loc.id == to, f"вход: {g.loc.name}")
    g.dialogue.active_node = None
    goto(g, sorted(next(p for p in g.level.portals if p["to"] == "primm")["tiles"])[0])

# расследование: помощник, гробовщик, бармен
talk("deputy_baxter")
say("не убивал")
say("Найду")
g.dialogue.active_node = None
talk("pr_undertaker")
say("Интересно")
ok(g.flags.get("clue_gun"), "улика: Ривз застрелен из своего кольта")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "primm_vikki")["tiles"])[0])
g.player.skills["speech"] = 70
talk("barkeep_slim")
say("хорошим человеком")
say("Спасибо")
ok(g.flags.get("clue_shawl") and g.flags.get("mae_suspect"), "улика: женщина в синей шали — вдова под подозрением")
g.dialogue.active_node = None
goto(g, sorted(portal(g, "primm_cellar")["tiles"])[0])
ok(g.loc.id == "primm_cellar", "подвал казино: камеры и архив")
g.open_terminal("reeves_archive")
g.term_open_entry(1)
g.term_open_entry(2)
g.close_terminal()
ok(g.flags.get("know_zero") and g.flags.get("know_amos_manifest"), "архив: хранилище «Ноль» и накладная деда")

# признание вдовы — обещание вернуть сына
goto(g, sorted(portal(g, "primm_vikki")["tiles"])[0])
goto(g, sorted(portal(g, "primm")["tiles"])[0])
goto(g, sorted(portal(g, "primm_bison")["tiles"])[0])
talk("mae_reeves")
say("женщину в шали")
say("верну Тоби")
say("успею")
ok(g.flags.get("mae_confessed") and g.inventory.has("фишка Ривза"), "Мэй призналась и отдала код на фишке")

# лагерь: Красноречием — мальчика отпускают без кода и без крови
g.dialogue.active_node = None
goto(g, sorted(portal(g, "primm")["tiles"])[0])
goto(g, sorted(portal(g, "primm_camp")["tiles"])[0])
ok(g.loc.id == "primm_camp", "лагерь культа у горок")
talk("brother_job")
say("Отдайте его")
say("Примм придёт")
say("Надеюсь")
ok(g.flags.get("tobi_home") and g.inventory.has("фишка Ривза"), "Тоби отпущен, код остался у героя")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
