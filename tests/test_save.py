"""
Проверка меню и сохранений без окна: главное меню, пауза, сохранение,
изменения после него, загрузка — и что всё вернулось как было.

    .venv/bin/python tests/test_save.py
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

saveload.SAVE_DIR = tempfile.mkdtemp(prefix="wr_saves_")  # не трогаем настоящие сохранения
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


# ---------------------------------------------------------------- меню
g = Game()
ok(g.menu and g.menu["screen"] == "main", "при запуске — главное меню")
labels = {lbl: en for lbl, _, en in g.menu_items()}
ok(not labels["Продолжить"] and not labels["Загрузить"], "без сохранений «Продолжить» и «Загрузить» недоступны")
g.draw()
g.menu_items()[1][1]()  # «Новая игра»
ok(g.slides and g.slides["id"] == "prologue" and not g.menu, "«Новая игра» — пролог")
g.handle_key(pygame.K_ESCAPE)
ok(g.inventory.has("письмо деда") and g.stage("mq_grandpa") == 10, "пролог пропущен — письмо, квест")
fr(g)
g.handle_key(pygame.K_ESCAPE)
ok(g.menu and g.menu["screen"] == "pause", "Esc в игре — пауза")
t0 = g.play_ms
fr(g, 30)
ok(g.play_ms == t0, "в паузе время стоит")
g.handle_key(pygame.K_ESCAPE)
ok(g.menu is None, "Esc в паузе — обратно в игру")

# ---------------------------------------------------------------- наиграть и сохранить
random.seed(4)
g.player.max_hp = g.player.hp = 500
eye = next(p for p in g.level.pickups if p["kind"] == "чей-то глаз")
g.player.rect.topleft = rect_pos_for_tile(g.player, (eye["rect"].x // 48, eye["rect"].y // 48))
fr(g)
g.handle_key(pygame.K_e)
g.open_terminal("grandpa")
g.term_open_entry(4)
g.close_terminal()
rats = [e for e in g.enemies if e.type_id == "rat"]
for e in rats[:2]:
    e.apply_damage(999)
    g.on_enemy_killed(e)
while g.perk_choices or g.player.pending_perks:
    fr(g, 1)
body = g.level.corpses[0]
g.open_container(body)
g.loot_take_all()
g.close_loot()
g.inventory.add("крышки", 33)
g.flags["test_flag"] = True
g.player.hp = 123
g.player.rect.topleft = rect_pos_for_tile(g.player, (20, 31))
fr(g, 3)
g.level.stains = [(100, 100, 3, (150, 14, 12))]
snap = {
    "inv": dict(g.inventory.items), "quests": dict(g.quests), "flags": dict(g.flags),
    "hp": g.player.hp, "lvl": g.player.level_sys.level, "xp": g.player.level_sys.xp, "perks": dict(g.player.perks),
    "pos": tuple(g.player.rect.topleft), "alive": [e.alive for e in g.loc.enemies_all],
    "corpses": [(c["name"], dict(c["loot"])) for c in g.level.corpses],
    "pickups": len(g.level.pickups), "explored": len(g.level.explored), "met": set(g.level.met),
    "stains": len(g.level.stains),
}
g.combat.active = True
ok(g.can_save() is not None, "в бою сохраняться нельзя")
g.combat.active = False
g.handle_key(pygame.K_ESCAPE)
g.menu_items()[1][1]()  # «Сохранить»
ok(g.menu["screen"] == "save", "пауза → экран сохранения")
g.draw()
g.menu_items()[0][1]()  # слот 1
ok(g.menu is None and os.path.isfile(os.path.join(saveload.SAVE_DIR, "1.json")), "сохранено в слот 1")
ok(os.path.isfile(os.path.join(saveload.SAVE_DIR, "1.png")), "есть миниатюра")

# ---------------------------------------------------------------- испортить всё
g.inventory.items.clear()
g.flags.clear()
g.quests.clear()
for e in g.enemies:
    e.apply_damage(999)
g.player.hp = 1
g.player.level_sys.level = 9
g.go_world_map()
g.worldmap.known.add("baker")

# ---------------------------------------------------------------- загрузить
g.handle_key(pygame.K_ESCAPE)
g.menu_items()[2][1]()  # «Загрузить»
ok(g.menu["screen"] == "load", "пауза → экран загрузки")
g.draw()
items = g.menu_items()
ok(items[0][2] is False and items[1][2] is True, "быстрый слот пуст, слот 1 доступен")
items[1][1]()
ok(g.menu is None and g.mode == "local" and g.loc.id == "ruins", "загрузка: снова в Пятнадцатой")
ok(dict(g.inventory.items) == snap["inv"], "рюкзак восстановлен")
ok(g.quests == snap["quests"] and g.flags == snap["flags"], "квесты и флаги восстановлены")
ok((g.player.hp, g.player.level_sys.level, g.player.level_sys.xp, g.player.perks) ==
   (snap["hp"], snap["lvl"], snap["xp"], snap["perks"]), "герой: HP, уровень, опыт, перки")
ok(tuple(g.player.rect.topleft) == snap["pos"], "герой на том же месте")
ok([e.alive for e in g.loc.enemies_all] == snap["alive"], "живые и убитые враги — как были")
ok([(c["name"], dict(c["loot"])) for c in g.level.corpses] == snap["corpses"], "тела и что на них осталось")
ok(len(g.level.pickups) == snap["pickups"], "подобранное не вернулось на землю")
ok(len(g.level.explored) >= snap["explored"] and g.level.met == snap["met"], "разведанное на миникарте")
ok(len(g.level.stains) == snap["stains"], "пятна крови на месте")
ok("baker" not in g.worldmap.known, "карта мира — как при сохранении")
fr(g, 5)

# ---------------------------------------------------------------- быстрое, карта мира, заправка
g.reveal_location("station")
g.enter_location("station")
fr(g, 3)
shram = next(e for e in g.loc.enemies_all if e.talk)
g.flags["gang_left"] = True
g.apply_effect({"type": "gang_leave"})
g.go_world_map()
g.handle_key(pygame.K_F5)
ok(saveload.slot_info("quick") is not None, "F5 — быстрое сохранение на карте мира")
g.enter_location("station")
g.handle_key(pygame.K_F9)
ok(g.mode == "world", "F9 — загрузка: снова на карте мира")
g.enter_location("station")
ok(not g.enemies, "банда, ушедшая по уговору, после загрузки не вернулась")
g.menu = None
g.open_menu("main")
ok(g.latest_save() == "quick", "«Продолжить» — самое свежее сохранение")

# ---------------------------------------------------------------- звук
print("— звук")
a = g.audio
ok(a.ok and {"shot", "melee", "hit"} <= set(a.sounds), f"звуки загружены: {len(a.sounds)} (свои + Fallout 2, если найден)")
if a.f2 is not None and (a.f2.install or a.f2.status == "done"):   # есть папка звуков или Fallout 2
    import time as _t
    for _ in range(600):
        if a.f2.status == "done":
            break
        _t.sleep(0.1)
    a.poll()
    ok({"ghoul_hurt", "human_death", "levelup", "combat_start"} <= set(a.sounds), "звуки Fallout 2 подключены")
    ok(a._music_file("desert").endswith("07desert.ogg"), "музыка Пятнадцатой — «Desert» из Fallout 2")
else:
    print("     (папки fallout2_sounds нет — играют свои звуки)")
g.menu = None
g.handle_key(pygame.K_ESCAPE)
labels = [lbl for lbl, _, _ in g.menu_items()]
ok("Звук" in labels, "в паузе есть пункт «Звук»")
g.menu_items()[labels.index("Звук")][1]()
ok(g.menu["screen"] == "sound", "экран «Звук»")
g.draw()
m0 = a.volume["music"]
g.menu["sel"] = 0
g.handle_key(pygame.K_RIGHT)
ok(abs(a.volume["music"] - min(1.0, m0 + 0.1)) < 1e-6, f"→ прибавляет музыку: {m0} → {a.volume['music']}")
g.menu["sel"] = 1
for _ in range(20):
    g.handle_key(pygame.K_LEFT)
ok(a.volume["sfx"] == 0.0, "звуки можно выключить совсем")
from src.audio import Audio  # noqa: E402
ok(Audio().volume == a.volume, "громкость запоминается между запусками (settings.json)")
a.set_volume("sfx", 0.8)
played = []
orig = a.play
a.play = lambda name, *args, **kw: played.append(name) or orig(name, *args, **kw)
g.menu = None
g.enter_location("ruins")
rat = next(e for e in g.loc.enemies_all if e.alive and e.type_id == "rad_mutant")
g.player.rect.topleft = rect_pos_for_tile(g.player, (tile_of(rat)[0] - 1, tile_of(rat)[1]))
g.combat.start(player_first=True)
g.player.ap = 8
g.combat.busy_ms = 0
g.combat.target = rat
rnd = random.randint
random.randint = lambda lo, hi: lo  # попадание
g.combat.attack(g.player, rat)
random.randint = rnd
ok("melee" in played and "hit" in played and played.index("melee") < played.index("hit"),
   f"удар ломом по мутанту: взмах, потом попадание ({played})")
g.inventory.add("самопал")
g.inventory.add("патроны", 3)
g.switch_weapon("pistol")
played.clear()
g.player.ap = 8
g.combat.attack(g.player, rat)
ok(any(p in ("shot", "shot_pipe") for p in played), f"выстрел: {played[:2]}")
fr(g, 20)

print(f"не прошло: {len(failed)}")
sys.exit(1 if failed else 0)
