"""
Особые встречи в пустоши (как в Fallout 2): Хранитель моста, кит с петунией, синяя будка, летающая тарелка,
скелет из Убежища 13. Каждая — один раз за игру, у каждой своя награда.

    .venv/bin/python tests/test_specials.py
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
        while g.perk_choices:
            g.handle_key(pygame.K_1)


def talk(g, nid):
    g.dialogue.active_node = None
    npc = next(n for n in g.npcs if n.npc_id == nid)
    for dx, dy in ((-1, 0), (0, 1), (0, -1), (1, 0)):
        c = (tile_of(npc)[0] + dx, tile_of(npc)[1] + dy)
        if not g.level.is_wall(*c):
            g.player.rect.topleft = rect_pos_for_tile(g.player, c)
            break
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), nid


def say(g, part):
    opts = [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]
    idx = next((i for i, l in enumerate(opts) if part in l), None)
    assert idx is not None, f"нет реплики «{part}» среди {opts}"
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)


def take(g, title):
    box = next(c for c in g.level.containers if c["name"] == title)
    for t in box["tiles"]:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, -1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in box["tiles"]:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.handle_key(pygame.K_e)
                fr(g, 1)
                if g.loot:
                    g.handle_key(pygame.K_r)
                    g.loot = None
                return box
    return box


def visit(g, enc_id):
    entry = next(e for e in encounters.ENCOUNTERS if e[1] == enc_id)
    real = encounters.roll
    encounters.roll = lambda *a, **k: entry
    loc, text = encounters.make_encounter(g.flags, level=10, survival=0)
    encounters.roll = real
    g.loc = loc                                   # как в WorldMixin: встреча — временная локация
    g.apply_view()
    g.place_player(g.level.player_spawn)
    g.mode = "local"
    fr(g)
    return loc, text


from src import encounters  # noqa: E402

g = Game(intro=False)
g.player.max_hp = g.player.hp = 300
for sid in encounters.SPECIALS:
    ok(any(e[1] == sid for e in encounters.ENCOUNTERS), f"встреча «{sid}» в таблице")

# Хранитель моста: неверный ответ — в каньон
loc, text = visit(g, "bridge")
ok("три вопроса" in text and g.flags.get("enc_bridge"), "встреча у моста — один раз за игру")
ok(not any(e[1] == "bridge" for e in encounters.ENCOUNTERS if e[5] is None or e[5](g.flags, 10, "mojave")),
   "второй раз мост не выпадет")
hp = g.player.hp
talk(g, "bridge_keeper"); say(g, "Спрашивай"); say(g, "Внук"); say(g, "деда"); say(g, "Сорок миль")
ok(g.player.hp == hp - 25 and g.flags.get("bridge_lost"), "неверный ответ — в каньон, −25 HP")
box = take(g, "сундук хранителя")
ok(not g.inventory.has("святая ручная граната"), "сундук без ответа не открыть")
g.dialogue.active_node = None
talk(g, "bridge_keeper"); say(g, "Попробую"); say(g, "Ланселот"); say(g, "Грааль"); say(g, "африканского"); say(g, "Надо знать")
ok(g.flags.get("bridge_won") and not any(n.npc_id == "bridge_keeper" for n in g.npcs), "«африканского или европейского?» — хранитель улетел в каньон")
take(g, "сундук хранителя")
ok(g.inventory.has("святая ручная граната"), "сундук хранителя — святая ручная граната")
ok(any(t[0] == "grail" for t in g.titles()), "звание «Рыцарь Моста»")

# кит с петунией
loc, text = visit(g, "whale")
take(g, "туша кита"); take(g, "горшок с петунией")
ok(g.inventory.has("амбра") and g.inventory.count("китовое мясо") == 5 and g.inventory.has("записка петунии"), "кит: мясо, амбра, «О нет, только не снова»")

# синяя будка
loc, text = visit(g, "police_box")
take(g, "синяя будка")
s0 = g.player.skill("science")
g.item_action("звуковая отвёртка")[1]()
ok(g.player.skill("science") == s0 + 10, "звуковая отвёртка: +10 к Науке")

# тарелка
loc, text = visit(g, "saucer")
take(g, "тело пришельца")
ok(g.inventory.has("инопланетный бластер") and g.inventory.count("инопланетная батарея") == 24, "тарелка: бластер и 24 батареи")

# Убежище 13
loc, text = visit(g, "vault13")
take(g, "скелет курьера Vault-Tec")
ok(g.inventory.has("водяной чип (Убежище 13)"), "скелет курьера Vault-Tec — водяной чип для Убежища 13")

# кафе «Несбывшиеся надежды»: странник «13» просит закопать чип
loc, text = visit(g, "cafe")
ok("Несбывшиеся надежды" in text and g.flags.get("enc_cafe"), "кафе, которого нет на картах — один раз")
talk(g, "cafe_dog"); say(g, "Пойдёшь"); say(g, "...")
talk(g, "cafe_stranger"); say(g, "водяной чип"); say(g, "закопать"); say(g, "...")
ok(g.flags.get("chip_buried") and g.inventory.has("кожанка с «13»") and not g.inventory.has("водяной чип (Убежище 13)"),
   "чип закопан под вывеской — кожанка с «13» на время")

# Оружейники: сильное, дорогое, не по руке
loc, text = visit(g, "gunrunners")
talk(g, "gun_runner"); say(g, "Покажи товар")
stock = g.traders["gun_runner"]["stock"] if g.trade else {}
ok(g.trade and g.trade["id"] == "gun_runner" and "снайперская винтовка" in stock and "плазменный пистолет" in stock,
   "у Оружейников — снайперская винтовка и плазма")
g.trade = None

# каратели культа: только тому, кто дважды встал у культа на пути
from src.encounters import _cult_angry  # noqa: E402
ok(not _cult_angry({"blue_arrested": True}, 10, "mojave"), "одна обида — карателей нет")
ok(_cult_angry({"blue_arrested": True, "bell_blown": True}, 10, "mojave"), "две обиды — каратели вышли на дорогу")
loc, text = visit(g, "punishers")
ok(g.enemies and all(e.hostile for e in g.enemies), "каратели нападают сразу")
for e in g.enemies:
    e.alive = False
take(g, "сумка старшего карателя")
ok(g.inventory.has("письмо карателям"), "письмо брата Т.: «принесите его в Марипозу целым»")
ok(not _cult_angry(dict(g.flags, blue_arrested=True, bell_blown=True), 10, "mojave"), "каратели — один раз")

# святая граната рвёт сильнее всех
e = encounters.Location  # noqa
from src.location import make_enemy  # noqa: E402
m = make_enemy((0, 0), "super_mutant")
m.rect.topleft = rect_pos_for_tile(m, (tile_of(g.player)[0] + 3, tile_of(g.player)[1]))
g.enemies[:] = [m]
hp = m.hp
g.combat.explode(tile_of(m), "holy")
ok(hp - m.hp >= 45, f"святая ручная граната: {hp - m.hp} урона супермутанту")


# ------------------------------------------------------------ «Письма почтальона»
gl = Game(intro=False)
gl.player.max_hp = gl.player.hp = 300
loc, text = visit(gl, "robot")
talk(gl, "robot"); say(gl, "недоставленное"); say(gl, "Доставлю")
letters = [k for k in gl.inventory.nonzero() if k.startswith("письмо:")]
ok(len(letters) == 8 and gl.stage("sq_letters") == 10, f"Почтальон-3000 отдал мешок: {len(letters)} писем")
k0 = gl.karma
gl.item_action("письмо: Ривзам, Примм")[1]()
gl.close_terminal()
ok(gl.karma == k0 - 2 and gl.flags.get("mail_opened_reeves"), "вскрыл чужое письмо — карма −2")
gl.enter_location("junktown_hall"); fr(gl)
gl.slides = None
caps = gl.inventory.count("крышки")
talk(gl, "mayor_darkwater"); say(gl, "письмо"); say(gl, "...")
ok(gl.flags.get("mail_done_darkwater") and gl.inventory.count("крышки") == caps + 120, "Дарквотер хохочет над банковским требованием — 120 крышек")
gl.enter_location("vault15_atrium"); fr(gl)
talk(gl, "beatrice"); say(gl, "письмо"); say(gl, "...")
gl.enter_location("aradesh_hall"); fr(gl)
talk(gl, "aradesh_wife"); say(gl, "Беатрис знает"); say(gl, "Передам")
ok(gl.flags.get("sisters_reconciled"), "записка Vault-Tec — и Лейла идёт мириться с Беатрис")
gl.enter_location("vegas_strip"); fr(gl)
gl.open_terminal("lucky38_door")
idx = next(k for k, (_, e) in enumerate(gl.term_entries()) if "щель" in e["label"])
gl.term_open_entry(idx)
gl.close_terminal()
ok(gl.flags.get("mail_done_house") and gl.inventory.has("фишка «Лаки 38»"), "Хаус получил письмо — фишка «Лаки 38»")

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
