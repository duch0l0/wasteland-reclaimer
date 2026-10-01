"""
Нападение на мирных и реакция города (src/game/crime.py) — без окна.

  - в миссии убил послушника — на шум сбегается весь двор, а не только сосед;
  - Shift + клик по жителю на трассе Бейкера: житель — враг, бойцы города (Ник, Холлис…)
    враждебны, мирные не разговаривают;
  - город помнит: ушёл и вернулся / загрузил сохранение — стража снова стреляет, убитые мертвы;
  - в Пятнадцатой нападение на Марту поднимает шерифа и Дейла.

    .venv/bin/python tests/test_crime.py
"""
import os
import random
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


def fr(g, n=2):
    for _ in range(n):
        g.update(16)
        g.draw()
        if g.perk_choices:
            g.handle_key(pygame.K_1)


def stand_near(g, tile):
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (tile[0] + dx, tile[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            g.snap_camera()
            return


def new_game(loc):
    random.seed(2)
    g = Game(intro=False)
    g.player.max_hp = g.player.hp = 10 ** 6
    g.player.base_damage = 60
    g.set_stage("mq_grandpa", 60)
    g.enter_location(loc)
    while g.slides:
        g.update(5000)
        g.slides_next()
    for e in g.enemies:
        e.wander_wait = 10 ** 9
    for n in g.npcs:
        n.wander_wait = 10 ** 9
    return g


def kill_all_in_combat(g):
    n = 0
    while g.combat.active and n < 200:
        for e in g.combat.enemies_in_combat():
            e.hp = 0
            e.alive = False
            g.on_enemy_killed(e)
        fr(g, 2)
        n += 1


# ------------------------------------------------------------ слух: весь двор миссии сбегается
g = new_game("baker")
g.enter_location("baker_mission")
victim = next(e for e in g.enemies if e.type_id == "cultist" and tile_of(e)[1] > 25)
stand_near(g, tile_of(victim))
fr(g, 1)
g.combat.target = victim
g.combat.start(player_first=True)
cult_in_fight = [e for e in g.combat.order if getattr(e, "faction", None) == "cult"]
ok(len(cult_in_fight) >= 4, f"на шум сбежался весь двор, не только сосед ({len(cult_in_fight)})")

# ------------------------------------------------------------ Shift + клик по жителю на трассе
g = new_game("baker")
hattie = next(n for n in g.npcs if n.npc_id == "hattie")
nick = next(n for n in g.npcs if n.npc_id == "nick")
stand_near(g, tile_of(nick))
g.attack_npc(nick)
fr(g, 1)
ok(g.flags.get("town_hostile_baker") and g.combat.active, "напал на Ника — город враждебен, бой")
ok(not any(n.npc_id == "nick" for n in g.npcs) and any(getattr(e, "npc_id", "") == "nick" for e in g.enemies),
   "Ник теперь враг")
ok(hattie in g.npcs, "Хэтти — мирная, в бой не лезет")
g.combat.active = False
g.talk_to(hattie, "hattie")
ok(not g.dialogue.is_active() and g.speech and "Убийца" in g.speech["text"], "мирные с убийцей не разговаривают")
nick_enemy = next(e for e in g.enemies if getattr(e, "npc_id", "") == "nick")
nick_enemy.hp, nick_enemy.alive = 0, False
g.on_enemy_killed(nick_enemy)
ok(g.flags.get("killed_nick"), "Ник убит — навсегда")
g.save_game("1")
g.enter_location("baker_outskirts")
ok(not g.flags.get("town_hostile_baker_outskirts"), "окраина — другой район, своя память")
g.enter_location("baker")
ok(not any(n.npc_id == "nick" for n in g.npcs), "вернулся — Ника нет")
g2 = Game(intro=False)
g2.load_game("1")
fr(g2, 1)
ok(g2.flags.get("town_hostile_baker") and not any(n.npc_id == "nick" for n in g2.npcs),
   "после загрузки город помнит, Ник мёртв")

# ------------------------------------------------------------ Пятнадцатая: шериф и Дейл
g = new_game("ruins")
marta = next(n for n in g.npcs if n.npc_id == "marta")
stand_near(g, tile_of(marta))
g.attack_npc(marta)
fr(g, 1)
guards = {getattr(e, "npc_id", "") for e in g.enemies if e.hostile}
ok({"sheriff", "dale", "mo"} <= guards, f"шериф, Дейл и Мо взялись за оружие ({sorted(guards)[:6]})")
ok(any(n.npc_id == "gena" for n in g.npcs), "Гена — мирный, прячется")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
