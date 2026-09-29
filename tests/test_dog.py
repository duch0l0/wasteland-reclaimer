"""
Пёс-спутник без окна: пёс на цепи в лагере рейдеров, после зачистки лагеря
герой говорит «Такая вот хуйня, собачка....» — пёс идёт следом, кусает врагов
в бою, враги бьют и его, после боя он встаёт; сохраняется и загружается.

    .venv/bin/python tests/test_dog.py
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
from src.combat import tile_of, rect_pos_for_tile, chebyshev  # noqa: E402

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


def stand_near(g, t):
    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1)):
        c = (t[0] + dx, t[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            g.snap_camera()
            return


def options(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


random.seed(5)
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
dog = next((n for n in g.npcs if n.npc_id == "dog"), None)
ok(dog is not None, "пёс сидит на карте города")
dog_tile = tile_of(dog)
raiders = [e for e in g.enemies if e.type_id == "raider"]
ok(len(raiders) >= 2 and all(chebyshev(tile_of(r), dog_tile) <= 8 for r in raiders), "пёс — в лагере рейдеров")

# пока рейдеры живы — только посмотреть
aggro = {id(e): e.aggro for e in g.enemies}
for e in g.enemies:
    e.aggro = 0
fr(g, 60)
ok(tile_of(dog) == dog_tile, "пёс на цепи не бродит")
stand_near(g, dog_tile)
g.handle_key(pygame.K_e)
ok(g.dialogue.is_active() and not any("собачка" in o for o in options(g)), "пока рейдеры живы, пса не забрать")
g.handle_key(pygame.K_1)
fr(g)
ok(g.stage("sq_dog") == 10, "квест «Пёс на цепи» в журнале")

# рейдеров больше нет
for r in raiders:
    r.hp = 0
    r.alive = False
    g.on_enemy_killed(r)
ok(g.flags.get("raiders_dead") and g.stage("sq_dog") == 50, "лагерь зачищен — стадия 50")
stand_near(g, dog_tile)
g.handle_key(pygame.K_e)
opts = options(g)
ok("Такая вот хуйня, собачка...." in opts, f"фраза героя в диалоге: {opts}")
g.handle_key(pygame.K_1 + opts.index("Такая вот хуйня, собачка...."))
fr(g, 3)
ok(g.companion is not None and not any(n.npc_id == "dog" for n in g.npcs), "пёс стал спутником")
ok(g.speech and "собачка" in g.speech["text"], "герой сказал фразу вслух (облачко)")
ok(g.stage("sq_dog") == 100, "квест выполнен")
g.handle_key(pygame.K_1)
fr(g)
pygame.image.save(g.screen, os.path.join(saveload.SAVE_DIR, "dog_join.png"))

# идёт следом
start = tile_of(g.player)
for i in range(8):
    x, y = tile_of(g.player)
    if not g.level.is_wall(x - 1, y):
        g.player.rect.topleft = rect_pos_for_tile(g.player, (x - 1, y))
    fr(g, 25)
ok(chebyshev(tile_of(g.companion), tile_of(g.player)) <= 2, "пёс идёт следом за героем")
g.enter_location("station")
fr(g, 5)
ok(chebyshev(tile_of(g.companion), tile_of(g.player)) <= 2, "пёс переходит в другую локацию вместе с героем")

# бой: пёс в очереди, кусает, враги его тоже бьют
g.enter_location("ruins")
fr(g, 3)
enemy = next(e for e in g.enemies if e.alive)
enemy.hp = enemy.max_hp = 400
enemy.aggro = aggro[id(enemy)]
et = tile_of(enemy)
stand_near(g, et)
from src import companion  # noqa: E402
companion.place_near_player(g)
g.combat.start(player_first=True)
ok(g.companion in g.combat.order, "пёс в очереди хода")
bites = 0
hits_on_dog = 0
dog_hp = g.companion.hp
for _ in range(6000):
    c = g.combat
    if not c.active:
        break
    if c.player_can_act():
        c.end_turn()
    fr(g, 1)
    bites = sum("вцепляется" in l or "щёлкает зубами" in l for l in g.log_lines)
    if g.companion.hp < dog_hp or g.companion.down:
        hits_on_dog = 1
    if bites >= 2 and (hits_on_dog or g.companion.down):
        break
ok(bites >= 1, f"пёс атакует врага в бою ({bites})")
ok(enemy.hp < 400, "пёс ранит врага")
pygame.image.save(g.screen, os.path.join(saveload.SAVE_DIR, "dog_fight.png"))
g.companion.hp = 1
g.combat.attack(enemy, g.companion) if g.combat.active else None
# выбывший пёс после боя встаёт
g.companion.down, g.companion.hp = True, 0
g.combat.active = False
fr(g, 3)
ok(not g.companion.down and g.companion.hp >= 1, "после боя пёс поднимается")

# сохранение
g.companion.hp = 17
g.save_game("1")
g2 = Game(intro=False)
ok(g2.companion is None, "в новой игре пса нет")
g2.load_game("1")
fr(g2, 3)
ok(g2.companion is not None and g2.companion.hp == 17, "пёс сохраняется и загружается")
ok(chebyshev(tile_of(g2.companion), tile_of(g2.player)) <= 2, "после загрузки пёс рядом с героем")
ok(not any(n.npc_id == "dog" for n in g2.npcs), "на цепи после загрузки пса нет")

print("\nВСЁ ОК" if not failed else f"\nПРОВАЛЕНО: {len(failed)}")
print("скриншоты:", saveload.SAVE_DIR)
sys.exit(1 if failed else 0)
