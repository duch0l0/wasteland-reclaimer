"""
«Последний урок» — побочный квест мисс Лейн (школа «Солнечная долина», fifteen_school_in).

  - старт: узел help у мисс Лейн ставит lane_task -> запись в журнале «Последний урок»;
  - учебник «Наша Америка, 5 класс» лежит в библиотеке (шкаф у стеллажей), рядом радтаканы;
  - путь А: отдать учебник -> сцена последнего урока, опыт, классная касса, «Наука» +10 (больше, чем от чтения);
    мясо для детей (вяленое, ящик завхоза) — отдельный отзвук;
  - путь Б: прочитать самому -> +6 «Наука», квест закрывается иначе, Лейн реагирует;
  - путь В: прочитать ДО знакомства -> признание у доски, без тупика;
  - отголоски: барки Лейн, детей и сторожа Уолта, слух Пятнадцатой, строка эпилога.

    .venv/bin/python tests/test_fifteen_lane.py
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
BOOK = "Наша Америка, 5 класс"


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


def goto(g, t):
    g.player.rect.topleft = rect_pos_for_tile(g.player, t)
    g.snap_camera()
    fr(g)


def portal(g, to):
    return next(p for p in g.level.portals if p["to"] == to)


def stand_near(g, tiles):
    tiles = [tuple(t) for t in tiles]
    for t in tiles:
        for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (0, -1)):
            c = (t[0] + dx, t[1] + dy)
            if not g.level.is_wall(*c) and c not in tiles:
                g.player.rect.topleft = rect_pos_for_tile(g.player, c)
                g.snap_camera()
                fr(g, 1)
                return
    raise AssertionError(f"негде встать рядом с {tiles[:2]}")


def talk(g, nid="miss_lane"):
    g.dialogue.close()
    npc = next(n for n in g.npcs if n.npc_id == nid)
    stand_near(g, [tile_of(npc)])
    g.handle_key(pygame.K_e)
    assert g.dialogue.is_active(), f"{nid} не заговорил"
    return npc


def opts(g):
    return [g.dialogue.option_label(o) for o in g.dialogue.visible_options()]


def say(g, part, required=True):
    labels = opts(g)
    idx = next((i for i, l in enumerate(labels) if part in l), None)
    if idx is None:
        if required:
            raise AssertionError(f"нет реплики «{part}» среди {labels}")
        return False
    g.handle_key(pygame.K_1 + idx)
    fr(g, 1)
    return True


def loot(g, title):
    """Открыть ящик по названию (E рядом) и забрать всё — как игрок."""
    box = next(c for c in g.level.containers if c["name"].startswith(title))
    stand_near(g, box["tiles"])
    g.handle_key(pygame.K_e)
    fr(g, 1)
    if g.term and not g.loot:
        g.close_terminal()
        g.open_container(box)
        fr(g, 1)
    assert g.loot and g.loot["box"] is box, f"ящик «{title}» не открылся"
    g.loot_take_all()
    g.close_loot()
    return box


def total_xp(g):
    ls = g.player.level_sys
    return sum(ls.xp_to_level_fn(l) for l in range(1, ls.level)) + ls.xp


def into_school(g):
    """Из Пятнадцатой — через двор в здание школы (по порталам, как игрок)."""
    goto(g, sorted(portal(g, "fifteen_school")["tiles"])[0])
    for e in g.enemies:
        e.hostile = False
    goto(g, sorted(portal(g, "fifteen_school_in")["tiles"])[0])
    for e in g.enemies:          # радтаканы в библиотеке живы, но в тесте не мешают
        e.hostile = False
        e.aggro = 0
        e.wander_wait = 10 ** 9
    fr(g, 2)


def epilogue_text(g):
    g.show_slides("epilogue")
    pages = [p for sl in g.slides["list"] for p in sl["parts"]]
    g.slides = None
    return " ".join(p["text"] for p in pages)


# ============================================================ путь А: отдать учебник
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
ok(g.quest_mark("miss_lane") == "new", "мисс Лейн — «есть дело» ещё до разговора")

into_school(g)
ok(g.loc.id == "fifteen_school_in", "дверь школы ведёт в «Солнечную долину»")
lane = talk(g, "miss_lane")
say(g, "Автобус не придёт")
say(g, "Чем помочь?")
say(g, "Попробую")
ok(g.flags.get("lane_task"), "разговор: Лейн попросила учебник (lane_task)")
ok(g.stage("sq_lane") == 10, "журнал: «Последний урок» взят (стадия 10)")
ok(g.quest_mark("miss_lane") is None, "пока учебника нет — отметки «сдать» у Лейн нет")
g.dialogue.close()

box = loot(g, "библиотечный шкаф")
ok(not box["loot"].get(BOOK), "учебник вынут из шкафа (шкаф обыскан)")
ok(g.inventory.has(BOOK), "учебник «Наша Америка, 5 класс» — в рюкзаке")
ok(g.stage("sq_lane") == 30, "журнал: учебник у меня (стадия 30)")
ok(g.quest_mark("miss_lane") == "turn_in", "Лейн ждёт ответа (отметка «сдать»)")
ok(sum(1 for e in g.enemies if e.alive and e.type_id == "radroach") >= 2,
   "рядом с библиотекой — радтаканы")

# мясо детям: ключ-карта -> ящик завхоза
loot(g, "картотека директора")
ok(g.inventory.has("ключ-карта школы"), "в картотеке директора — ключ-карта школы")
loot(g, "ящик завхоза")
ok(g.inventory.count("вяленое мясо") >= 2, "в ящике завхоза — вяленое мясо для детей")

xp0, caps0, sci0 = total_xp(g), g.inventory.count("крышки"), g.player.skill("science")
talk(g, "miss_lane")
say(g, "Вот учебник")
ok(g.dialogue.active_node == "lesson", "сцена последнего урока открылась")
ok("Джо. Меня зовут Джо" in g.dialogue.current_node()["text"], "Джо вспоминает своё имя у доски")
ok(not g.inventory.has(BOOK), "учебник отдан")
ok(g.stage("sq_lane") == 100, "журнал: квест закрыт (стадия 100)")
ok(g.flags.get("lane_lesson"), "флаг исхода: урок состоялся (lane_lesson)")
ok(total_xp(g) - xp0 == 150, f"опыт за урок: +{total_xp(g) - xp0} (ждали 150)")
ok(g.inventory.count("крышки") - caps0 == 45, f"классная касса: +{g.inventory.count('крышки') - caps0} крышек")
ok(g.player.skill("science") == min(150, sci0 + 10), f"урок: «Наука» +10: {sci0} → {g.player.skill('science')}")
ok(g.flags.get("karma_done_lane_lesson") and g.karma >= 15, f"карма за урок: {g.karma}")
ok(g.rep("fifteen") >= 25, f"Пятнадцатая: репутация {g.rep('fifteen')}")
ok(any(t[0] == "teacher" for t in g.titles()), "звание «Учитель «Солнечной долины»» выдано")
say(g, "Урок окончен")
ok("Над «Солнечной долиной» стоит звонок" in g.dialogue.current_node()["text"], "звонок прозвенел")
say(g, "Идти")
ok(not g.dialogue.is_active(), "сцена закрывается")

# мясо после урока
xp1 = total_xp(g)
talk(g, "miss_lane")
ok(g.dialogue.active_node == "after_lesson", "после урока Лейн говорит иначе (after_lesson)")
ok(say(g, "вяленое мясо", required=False), "у Лейн можно оставить мясо")
ok(g.flags.get("lane_meat"), "флаг: дети сыты (lane_meat)")
ok(total_xp(g) - xp1 == 30, f"опыт за мясо: +{total_xp(g) - xp1}")
g.dialogue.close()

# отголоски пути А
lane = next(n for n in g.npcs if n.npc_id == "miss_lane")
kid = next(n for n in g.npcs if n.npc_id == "ghoul_kid_c")
lane_barks = " ".join(g.bark_lines(lane))
ok("Звонок был" in lane_barks, "барк Лейн после урока: «Звонок был»")
ok("все сыты разом" in lane_barks, "барк Лейн про мясо")
ok("Маленький Джо" in " ".join(g.bark_lines(kid)), "барк Маленького Джо: имя вспомнено")
goto(g, sorted(portal(g, "fifteen_school")["tiles"])[0])
walt = next(n for n in g.npcs if n.npc_id == "walt")
ok("Это я звонил" in " ".join(g.bark_lines(walt)), "барк сторожа Уолта во дворе")
ok("звонок прозвенел" in " ".join(g.bark_lines(walt)), "слух Пятнадцатой о звонке")
ep = epilogue_text(g)
ok("прозвенел звонок" in ep and "Мисс Лейн провела последний урок" in ep, "эпилог: звонок и последний урок")
ok("пахнет вяленым мясом" in ep, "эпилог: дети сыты")

# ============================================================ путь Б: прочитать самому
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
into_school(g)
talk(g, "miss_lane")
say(g, "Автобус не придёт")
say(g, "Чем помочь?")
say(g, "Попробую")
g.dialogue.close()
loot(g, "библиотечный шкаф")
ok(g.inventory.has(BOOK) and g.stage("sq_lane") == 30, "путь Б: учебник в руках, стадия 30")
sci0, karma0 = g.player.skill("science"), g.karma
g.use_item(BOOK)
ok(g.player.skill("science") == sci0 + 6, f"чтение: Наука {sci0} → {g.player.skill('science')}")
ok(not g.inventory.has(BOOK), "прочитанная книга исчезает")
ok(g.flags.get("lane_book_read"), "флаг исхода: прочитал сам (lane_book_read)")
ok(g.stage("sq_lane") == 100, "журнал: квест закрыт иначе (стадия 100)")
ok(g.karma == karma0 - 15, f"карма за прочитанный учебник: {karma0} → {g.karma}")
ok(not g.flags.get("lane_lesson"), "урока не было: lane_lesson не поставлен")

talk(g, "miss_lane")
ok(g.dialogue.active_node == "read_react", "Лейн начинает с разочарования (read_react)")
ok("Учителя не сердятся" in g.dialogue.current_node()["text"], "её реплика: «учителя не сердятся — они запоминают»")
say(g, "Простите")
ok(g.flags.get("lane_read_reacted"), "сцена разочарования отыграна")
g.dialogue.close()
talk(g, "miss_lane")
ok(g.dialogue.active_node == "cold", "при следующем разговоре — холодная Лейн (cold)")
g.dialogue.close()
lane = next(n for n in g.npcs if n.npc_id == "miss_lane")
ok("Учителя всегда знают" in " ".join(g.bark_lines(lane)), "барк Лейн: «Учителя всегда знают»")
ep = epilogue_text(g)
ok("прочёл и не вернул" in ep, "эпилог: учебник прочли и не вернули")
ok("прозвенел звонок" not in ep, "эпилог: звонка в этом исходе нет")

# ============================================================ путь В: прочитать до знакомства
g = Game(intro=False)
g.player.max_hp = g.player.hp = 10 ** 6
into_school(g)
loot(g, "библиотечный шкаф")
ok(g.inventory.has(BOOK), "путь В: учебник взят до знакомства с Лейн")
g.use_item(BOOK)
ok(not g.flags.get("lane_book_read"), "до просьбы Лейн чтение — без последствий")
talk(g, "miss_lane")
say(g, "Автобус не придёт")
say(g, "Чем помочь?")
say(g, "Попробую")
ok(say(g, "Учебника у меня больше нет", required=False), "у доски можно признаться: учебника нет")
ok(g.dialogue.active_node == "lost", "Лейн просит сказать прямо (lost)")
say(g, "Прочитал")
ok(g.flags.get("lane_book_read"), "признание ставит lane_book_read")
ok(g.stage("sq_lane") == 100, "путь В тоже закрывает квест — тупика нет")
ok(g.dialogue.active_node == "read_react", "и сразу её разочарование")
g.dialogue.close()

print()
print("ИТОГ:", "всё прошло" if not failed else f"провалов: {len(failed)}")
sys.exit(1 if failed else 0)
