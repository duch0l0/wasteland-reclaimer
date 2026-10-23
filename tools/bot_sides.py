"""
Побочные квесты городов для бота (tools/playthrough.py): те же цепочки реплик, что в тестах квестов
(tests/test_*quests.py), только бот ходит сам, платит своими крышками и берёт ветку по своим навыкам —
[Красноречие], [Наука] — только если навык есть. Не вышло — бот записывает и идёт дальше.
"""


def skill(b, sid):
    return b.g.player.skill(sid)


def has(b, item, n=1):
    return b.g.inventory.has(item, n)


def caps(b):
    return b.g.inventory.count("крышки")


def buy_in_city(b, city, trader, item, n=1):
    """Купить у торговца в другом городе: по карте мира, как бот ходит между городами.
    Между городами нет порталов, поэтому walk_to_map здесь не работает — только go_world_map + go."""
    g = b.g
    if has(b, item, n):
        return True
    g.go_world_map()
    b.go(city)
    b.buy_from(trader, item, n)
    return has(b, item, n)


def wait_night(g, tries=30):
    """Дождаться ночи (20:00–5:00): герой стоит у колокольни и ждёт, пока сменятся часы.
    Ждать «отдыхом» движок не умеет — время двигает только advance_time (так же, как неделя в «Улыбке папы»)."""
    for _ in range(tries):
        if g.is_night():
            return True
        g.advance_time(60)
    return g.is_night()


# ================================================================ Хаб (акт II)
def hub_start(b):
    g = b.g

    def falcon():
        """Взяться за птицу и узнать, кто её вынес. Денег на ключ здесь ещё нет — сделку с Декером
        делает falcon_deal() позже, в обходе (hub_finish), когда крышки есть или нашлась отмычка."""
        b.visit("hub_falcon", clear=False)
        if not g.flags.get("falcon_job"):
            b.chat("falcon_barkeep", "серый", "Кто знал", "Поспрашиваю")
        if not g.flags.get("know_falcon_decker"):
            b.chat("falcon_singer", "Кто был в баре", "Спасибо")
            b.chat("falcon_gambler", "Лулу видела", "Посмотрим")
        if not g.flags.get("know_falcon_decker"):
            raise b.Stuck("никто в баре не сказал, у кого птица")
    b.side("Мальтийский сокол", falcon)

    def fever():
        b.chat("slum_mother", "весь красный", "найду", "Пока нечего")
        if skill(b, "science") >= 60 and has(b, "пружина"):
            b.chat("slum_old", "колодцем", "Наука", "...")
    b.side("Лихорадка: начало", fever)

    def blue():
        b.chat("junkie", "синий", "Найду")
        b.chat("arms_seller", "голубыми", "Спасибо")
        b.chat("spice_seller", "голубых", "купить")
    b.side("Голубые ментаты: начало", blue)


def falcon_deal(b):
    """Птица у Декера — три пути по цене, в порядке бота: слова, отмычка, крышки.

    Слова — тот же порог, что в диалоге (Красноречие 60): Декер сам отдаёт ключ и злится, что его
    переспорили. Отмычка — второй путь и единственный, который не зависит ни от навыка, ни от денег:
    отмычка стоит 8–20 крышек у Гены и Розы и валяется в каждом втором ящике. Цена вскрытия — карма −5
    и репутация Хаба −15 (Декер видит, кто копается в его сейфе), зато в сейфе, кроме свинцовой птицы,
    лежит его гроссбух — тот самый «выкуп», о котором он молчит."""
    g = b.g
    if g.stage("sq_falcon") >= 100 or not g.flags.get("falcon_job"):
        return
    b.visit("hub_falcon", clear=False)
    if not has(b, "статуэтка сокола") and not g.flags.get("falcon_dk_done"):
        if skill(b, "speech") >= 60 or caps(b) >= 100:
            b.chat("decker", "Птица Винни", ("[Красноречие]", "Сто крышек"), "...")
    if not has(b, "статуэтка сокола"):
        if has(b, "ключ от сейфа Декера"):
            b.walk_to_map("hub_old")
        elif has(b, "отмычка"):
            b.steal("hub_old", "сейф Декера")          # встать с той стороны, где Декер не смотрит
        if has(b, "ключ от сейфа Декера") or has(b, "отмычка"):
            b.take_from("сейф Декера")
    if not has(b, "статуэтка сокола"):
        raise b.Stuck(f"птицы нет: ключ не за сто крышек (в кармане {caps(b)}), отмычки нет")
    b.visit("hub_falcon", clear=False)
    b.chat("falcon_barkeep", "Твоя птица", ("Свинец", "Скол"), "...")
    if g.stage("sq_falcon") < 100:
        raise b.Stuck("Винни птицу не взял")


def hub_finish(b):
    """После Джанктауна: лекарство доктора Шоу — ребёнку, антидот — Вилли, торговца — страже."""
    g = b.g

    def falcon():
        falcon_deal(b)
    b.side("Мальтийский сокол", falcon)

    def fever():
        if g.stage("sq_fever") >= 100:
            return
        b.visit("hub_old", clear=False)
        b.chat("slum_mother", "лекарство", "Жаропонижающее", "колодцем")
        b.chat("slum_old", "колодцем", "Вегой")
        if g.flags.get("dolores_trust"):
            b.chat("dolores", "кран", "Спасибо")
    b.side("Лихорадка в Старом городе", fever)

    def blue():
        if g.stage("sq_blue") >= 100:
            return
        b.visit("hub_old", clear=False)
        b.chat("junkie", "Антидот", "...")
        b.chat("spice_seller", "Тощий Сэм", "к страже", "...")
    b.side("Голубые ментаты", blue)
    b.side("Хаб: лавки и уроки", lambda: (b.visit("hub", clear=False), b.shop_here()))


# ================================================================ Джанктаун
def junktown(b):
    g = b.g

    def anna():
        b.visit("junktown_clinic", clear=False)
        if 0 < g.stage("sq_fever") < 50:
            b.chat("anna_shaw", "ребёнок с лихорадкой", "Бегу")
        if 0 < g.stage("sq_blue") < 100 and has(b, "голубые ментаты"):
            b.chat("anna_shaw", "таблетки", "Спасибо")
    b.side("Доктор Шоу: лекарства для Хаба", anna)

    def fred():                       # раньше «Гизмо и стены»: купчую возвращает сам Гизмо
        b.visit("junktown_casino", clear=False)
        b.chat("gambler_jt_b", "Сколько ты должен", "разберусь")
        if not g.flags.get("fred_vera"):
            # порог тот же, что в диалоге Веры: 60 — тогда «Отдай», иначе «Понял» (кости у Изо)
            b.chat("croupier", "Кости", ("Отдай", "Понял"), ("Спасибо", "Понял"))
        if not has(b, "кости Гизмо"):                 # второй путь: Изо за три бутыли Грека
            if g.inventory.count("самогон") < 3:
                b.visit("junktown_skum", clear=False)
                while g.inventory.count("самогон") < 3 and caps(b) >= 8:
                    b.chat("neal", "Самогон")
                b.visit("junktown_casino", clear=False)
            if g.inventory.count("самогон") >= 3:
                b.chat("gizmo_thug", "Изо", "Держи бутыли")
        if not has(b, "кости Гизмо") and caps(b) >= 150:      # третье: просто выкупить долг Фреда
            b.chat("gambler_jt_b", "Держи сто пятьдесят", "...")
        if not g.flags.get("fred_done"):
            if not has(b, "кости Гизмо"):
                raise b.Stuck("костей ни у Веры, ни у Изо, и ста пятидесяти на долг нет")
            b.chat("gizmo", "Твои кости", "Купчая", "...")
            b.chat("gambler_jt_b", "Купчая", "Удачи")
    b.side("Последняя стена", fred)

    def robes():
        b.walk_to_map("junktown")
        b.chat("jt_woman", "бледная", "Дай сюда")
        b.chat("mayor_darkwater", "детей Джанктауна", "...")
    b.side("Кровь на балахонах", robes)

    def gizmo():
        b.visit("junktown_casino", clear=False)
        if skill(b, "speech") >= 80:
            b.chat("gizmo", "Красноречие", "Передам")
            b.chat("mayor_darkwater", "мир", "...")
            return
        b.chat("gizmo", "работа", "Давай флягу")
        b.chat("mayor_darkwater", "Гизмо заказал", "Пойду")
        b.chat("marsha", "диктофон", "ничего не случится")
        b.chat("gizmo", "Повтори", "Всё")
        b.chat("mayor_darkwater", "голос Гизмо", "...")
    b.side("Гизмо и стена", gizmo)

    if b.build_name == "melee":
        ring(b)


def ring(b):
    """Ринг «Скам-Питта»: лестница из пяти бойцов, Гизмо просит лечь — честный боец не ложится."""
    g = b.g

    def fights():
        b.visit("junktown_casino", clear=False)
        for _ in range(5):
            if g.flags.get("ring_champion") or g.player.hp < g.player.hp_cap * 0.8:
                break
            b.talk("neal")
            for part in ("ринге", "следующий"):
                b.say(part)
            if b.say("готов", required=False):
                b.say("ложусь только спать")
            b.say("Ставлю на себя 50", required=False) or b.say("Без ставки")
            b.fight()
            b.fr(3)
            b.rest()
        if not g.flags.get("ring_wins"):
            raise b.Stuck("ни одной победы на ринге")
    b.side("Ринг «Скам-Питта»", fights)


# ================================================================ Некрополь
def necropolis(b):
    g = b.g

    def fox():
        b.walk_to_map("necropolis")
        b.chat("nc_old", "Какой был кинотеатр", "последнюю часть", "Посмотрю")
        if not has(b, "кинолента «Атомный рейнджер»"):
            raise b.Stuck("плёнки нет")
        b.chat("harry_mech", "Проектор", ("Наука", "Сорок"), "...")
        b.chat("nc_old", "плёнка у меня", "покажем", "...")
    b.side("Чем кончился «Атомный рейнджер»", fox)

    def beach():
        b.walk_to_map("necropolis")
        b.chat("water_queue_b", "чего не было", "с пляжа", "Найду")
        b.chat("lorraine", "реестр", "Спасибо")
        b.chat("water_queue_b", "чьё это детство", "Сета", "...")
        b.chat("water_queue_b", "Дочери Сета", "должен знать", "...")
    b.side("Пляж в Санта-Монике", beach)

    def ferals():
        b.visit("necropolis_under", clear=False)
        b.chat("under_ghoul_b", "Кто перестал", "злее", "Узнаю")
        b.chat("under_barkeep", "шлюзу", "Спасибо")
    b.side("Еда у шлюза: начало", ferals)


def ferals_finish(b):
    g = b.g

    def go():
        if not (0 < g.stage("sq_ferals") < 100):
            return
        b.visit("junktown_clinic", clear=False)
        b.chat("anna_shaw", "Железы", "Передам")
        b.shop_here()
        b.visit("necropolis_under", clear=False)
        b.chat("ghoul_healer", "Шлюз", "наркоз", "...")
        b.shop_here()
    b.side("Еда у шлюза", go)


# ================================================================ Боунъярд
def boneyard_before(b):
    """До кражи со склада Собора: брат Пола пишет «родным» чужим почерком."""
    b.side("Почерк не его: начало",
           lambda: (b.walk_to_map("boneyard"), b.chat("adytum_farmer", "Чем платят", "письма брата", "Узнаю")))


def boneyard(b):
    g = b.g

    def letters():
        if not has(b, "пачка писем «родным»"):
            raise b.Stuck("писем со склада нет")
        b.walk_to_map("boneyard")
        b.chat("adytum_farmer", "нашёл письма", "жив", "...")
        try:                          # мэр читает письма на площади — если сейчас не занят другим разговором
            b.chat("adytum_mayor", "Письма со стройки", "...")
        except b.Stuck:
            pass
    b.side("Почерк не его", letters)

    def karl():
        b.visit("boneyard_adytum", clear=False)
        b.chat("adytum_mom", "Кто ушёл", "Как его зовут", "не буду стрелять")
        b.chat("adytum_kid", "папина гармошка", "Постараюсь")
        b.chat("cult_listener", "сыграть", "Идём", "...")
    b.side("Брат Карл", karl)

    def bell():
        b.walk_to_map("boneyard")
        b.chat("adytum_worker", "Что строит", "медный кабель", "Спасибо")
        if skill(b, "science") >= 60 and (has(b, "изолента")):
            b.chat("adytum_worker", "Наука", "...")
    b.side("Колокольня: начало", bell)

    def cement():                     # мешок цемента для баржи Нидлса — с поддона на стройке
        if not has(b, "мешок цемента"):
            b.walk_to_map("boneyard")
            b.take_from("поддон с мешками")
    b.side("Цемент для баржи", cement)


def bell_finish(b):
    g = b.g

    def go():
        if g.stage("sq_bell") >= 100 or not (0 < g.stage("sq_bell")):
            return
        b.visit("boneyard", clear=False)
        if has(b, "динамит"):                      # динамит: 250 xp, репутация +15
            b.chat("adytum_worker", "динамит", "...")
            return
        # Ночной подъём: ни динамита, ни Науки, ни изоленты — только ночь и руки.
        # Рабочий сам сказал: «ночью там никого». Днём реплики нет — герой ждёт смены часа.
        if not wait_night(g):
            raise b.Stuck("ночь не наступила — на колокольню днём рабочих не пускают")
        b.visit("boneyard", clear=False)
        b.chat("adytum_worker", "ночью наверху никого", "...")
        b.heal_if_needed()
        if g.stage("sq_bell") < 100:
            raise b.Stuck("катушка не снята: маяк всё ещё гудит")
    b.side("Колокольня", go)


# ================================================================ Арадеш (акт II)
def aradesh(b):
    """Вода для Арадеша: пещера (бой, «честный» путь) или насос Вика из каньона (доля Ханов).

    Пещера — единственный путь, который был у бота, и он же самый честный: радскорпионы, флаг
    clear_flag, репутация Арадеша. Если матка выжила и флага нет — второй путь: Ханы пропускают
    механика (первая бочка им), Вик поднимает воду из каньона пружиной от тачки. Оба не вышли —
    честная причина в side_fails, а не тихая потеря (раньше required=False молчал)."""
    g = b.g
    from src.combat import tile_of

    def go():
        b.visit("aradesh", clear=False)
        b.pursue("aradesh", "aradesh_job", required=False)
        cave_left = []
        if not g.flags.get("aradesh_free_water"):
            b.visit("aradesh_cave")
            cave_left = [f"{e.type_id} ({tile_of(e)[0]},{tile_of(e)[1]})"
                         for e in g.enemies if e.alive and e.hostile]
        if g.flags.get("aradesh_spring_cleared") and not g.flags.get("aradesh_free_water"):
            b.visit("aradesh", clear=False)
            b.pursue("aradesh", "aradesh_free_water", required=False)
        if g.flags.get("aradesh_free_water"):
            return
        b.visit("aradesh_canyon", clear=False)
        b.pursue("khan_chief", "khans_pump_ok", required=False)
        if not g.flags.get("khans_pump_ok"):
            raise b.Stuck("пещера не зачищена" + (f" (живы: {', '.join(cave_left)})" if cave_left else "")
                          + "; Ханы не пропустили механика к насосной")
        b.visit("aradesh", clear=False)
        if not has(b, "пружина"):
            b.buy_from("mechanic_vic", "пружина")       # пружина от тачки, 5 крышек — у него в лотке
        b.pursue("mechanic_vic", "pump_fixed", required=False)
        if not g.flags.get("pump_fixed"):
            raise b.Stuck(f"насос не поднят: пружины нет, в кармане {caps(b)} крышек")
        b.pursue("aradesh", "aradesh_free_water", required=False)
        if not g.flags.get("aradesh_free_water"):
            raise b.Stuck("Арадеш не принял воду из насоса")
    b.side("Вода для Арадеша", go)


# ================================================================ Нидлс (акт I½ и обход)
def needles(b):
    g = b.g

    def barge():
        b.walk_to_map("needles")
        b.chat("kate", "рыба светится", "баржа", "цементом", "Нырну")
        b.chat("drunk_vic", "открытая бочка", "Спасибо")
    b.side("Жёлтые треугольники: начало", barge)

    def noa():
        b.walk_to_map("needles")
        b.chat("preacher_eli", "особенно", "Поговорю")
        b.chat("noa_runaway", "Что ты видела", "в безопасности")
        if g.flags.get("ferry_done"):
            b.chat("noa_runaway", "Кейт", "...")
        elif skill(b, "speech") >= 60:
            b.chat("noa_runaway", "вытащу", "Останься", "...")
    b.side("Беглянка в церкви", noa)


def needles_finish(b):
    g = b.g

    def go():
        if not (0 < g.stage("sq_barge") < 100):
            return
        if not has(b, "мешок цемента"):
            raise b.Stuck("нет цемента")
        b.visit("needles", clear=False)
        if not has(b, "противогаз"):
            b.visit("needles_shop", clear=False)
            b.buy_from("shopkeeper_rosa", "противогаз")
            b.walk_to_map("needles")
        if has(b, "противогаз"):
            b.chat("kate", "Цемент у меня", "химзащиты", "...")
            b.cure_rads()
        elif not g.flags.get("barge_done"):
            # без маски нырять нечем — работает Речная стража. Дороже славой (+10 вместо +30/+35),
            # дешевле здоровьем: ни рад, ни ожогов. Морроу берёт цемент и отдаёт результат за славу.
            try:
                b.chat("captain_morrow", "Баржа ниже моста",
                       ("[Красноречие]", "знаю про белые фургоны", "Цемент мой"), "...")
            except b.Stuck as ex:
                raise b.Stuck(f"противогаза нет, и Морроу не уговорить: {ex}")
        if not g.flags.get("barge_done"):
            raise b.Stuck("баржа не залита: в трюм так никто и не нырнул")
        if 0 < g.stage("sq_noa") < 100 and g.flags.get("ferry_done"):
            b.chat("noa_runaway", "Кейт", "...")
    b.side("Жёлтые треугольники", go)


# ================================================================ Бейкер (акт I)
def baker(b):
    g = b.g

    def moonshine(n):              # самогон у Ника — по 8 крышек, прямо в разговоре
        while g.inventory.count("самогон") < n and caps(b) >= 8:
            b.chat("nick", "Самогон")
        return g.inventory.count("самогон") >= n

    def thermo():
        b.visit("baker", clear=False)
        b.chat("nick", "Термометр", "Посмотрю")
        if skill(b, "science") >= 45:                  # порог тот же, что в диалоге мальчишки
            b.chat("baker_kid", "на самом деле", "Наука", "жара")
        else:                                          # без Науки — изолента и батарейки из хлама на окраине
            for lid in ("baker_outskirts", "baker_motel_2f"):
                if has(b, "изолента") and has(b, "батарейки"):
                    break
                b.visit(lid)
                b.loot_area()
            b.visit("baker", clear=False)
            if not (has(b, "изолента") and has(b, "батарейки")):
                raise b.Stuck("изоленты и батареек на колонну не нашлось")
            b.chat("baker_kid", "на самом деле", "Изолента", "жара")
        b.chat("nick", "работает", "...")
    b.side("Термометр", thermo)

    def smile():
        DAY = 24 * 60
        b.visit("baker_motel_2f", clear=False)
        b.chat("motel_mom", "муж", "Узнаю")
        if not has(b, "ключ от крипты"):          # ключ — в сундуке Ансельма, взять тихо
            b.steal("baker_mission", "сундук Ансельма")
        if not has(b, "ключ от крипты"):          # второй путь: пьяный ключник Тобиас за две бутыли
            b.visit("baker", clear=False)        # Ник и Тобиас — в «Безумном греке»
            if not moonshine(2):
                raise b.Stuck("на две бутыли самогона Грека не хватает крышек")
            b.talk("tobias")                     # Тобиас сидит в «Безумном греке», не в миссии
            b.say("Ты ключник?", required=False)      # ключ от келий уже отдан — сразу к делу
            if b.say("Две бутыли", required=False):
                b.say("Понял", required=False)
            b.end_talk()
            b.fr(2)
        if not has(b, "ключ от крипты"):
            raise b.Stuck("ключа от крипты нет")
        b.visit("baker_mission", clear=False)
        b.walk_to_map("baker_crypt")
        b.chat("oskar", "вернулся", "Спасибо")
        if not has(b, "чистая вода", 3):          # вода в двух шагах: колонка на площади и ящик в миссии
            b.visit("baker", clear=False)
            b.loot_area()
            b.visit("baker_mission", clear=False)
            b.loot_area()
        if not has(b, "чистая вода", 3):
            raise b.Stuck("нет трёх фляг чистой воды на три дня")
        b.visit("baker_motel_2f", clear=False)
        b.chat("motel_mom", "Три дня", "Вернусь")
        g.advance_time(DAY + 60)              # герой ждёт рядом (отдых), как сделал бы игрок
        b.chat("motel_mom", "Держитесь", "Не открывайте")
        g.advance_time(2 * DAY + 60)
        b.fr(3)
        if not g.flags.get("smile_back"):
            raise b.Stuck("улыбка не прошла")
    b.side("Улыбка папы", smile)


# ================================================================ Акт III
def primm(b):
    g = b.g

    def bonnie():
        b.visit("primm_vikki", clear=False)
        b.chat("barkeep_slim", "Багажник", "23 мая 1934", "...")
        b.take_from("машина Бонни и Клайда")
    b.side("Машина смерти", bonnie)

    def coaster():
        b.walk_to_map("primm")
        b.chat("pr_mechanic", "горки", "Найду ток")
        if not g.flags.get("coaster_power"):
            if has(b, "ядерный элемент"):
                b.chat("pr_mechanic", "Ток для горок", "Ядерный элемент", "...")
            elif skill(b, "science") >= 55:              # порог диалога: ветряк у колонок
                b.chat("pr_mechanic", "Ток для горок", "Наука", "...")
            else:
                if not has(b, "топливо", 5):              # канистра — 5 крышек, продают в трёх городах
                    for city, trader in (("aradesh", "mechanic_vic"), ("junktown", "jt_tinker"),
                                         ("needles", "shopkeeper_rosa")):
                        try:
                            if buy_in_city(b, city, trader, "топливо", 5):
                                break
                        except b.Stuck:
                            continue
                g.go_world_map()
                b.go("primm")
                if has(b, "топливо", 5):
                    b.chat("pr_mechanic", "Ток для горок", "Пять канистр", "...")
        if not g.flags.get("coaster_power"):
            raise b.Stuck(f"ток не найден: топлива {g.inventory.count('топливо')}/5, элемента нет, Науки < 55")
        # Рельсы: пороги диалога — Наука 60 или Выживание 50, не больше. Нет ни того, ни другого —
        # смотрит Абнер: он их строил в семьдесят седьмом и знает, где стучать.
        if skill(b, "science") >= 60 or skill(b, "survival") >= 50:
            b.chat("pr_mechanic", "Запускай", ("проверю рельсы", "обойду опоры"), "...")
        else:
            b.chat("pr_old", "Абнер, ты же их строил", "...")
        if not g.flags.get("coaster_done"):
            raise b.Stuck("горки не запущены: рельсы никто не проверил")
    b.side("Отчаянный", coaster)


def goodsprings(b):
    g = b.g

    def ringo():
        b.visit("goodsprings_saloon", clear=False)
        b.chat("gs_drunk", "прячешься", "разберусь")
        b.chat("trudy", "Кобб пришёл", "Спасибо")
        b.walk_to_map("goodsprings")
        b.chat("chet", "патроны для Ринго", "Пятьдесят")
        b.chat("joe_cobb", "под защитой", "выйти на улицу)", "...")
    b.side("Перестрелка в городе-призраке", ringo)

    def spring_start():
        b.walk_to_map("goodsprings")
        b.chat("sunny", "у родника", "с тобой")
        b.chat("gs_kid", "ночью к роднику", "можно")
    b.side("Двор Санни: начало", spring_start)


def goodsprings_after_cave(b):
    g = b.g

    def go():
        if not (0 < g.stage("sq_spring") < 100):
            return
        if not g.flags.get("gs_cave_cleared"):
            from src.combat import tile_of
            left = [f"{e.type_id} ({tile_of(e)[0]},{tile_of(e)[1]})" for e in g.enemies if e.alive and e.hostile]
            raise b.Stuck("пещера не зачищена: " + (", ".join(left) if left else "флаг gs_cave_cleared не выставлен"))
        b.walk_to_map("goodsprings")
        b.chat("sunny", "Пещера чиста", "Чет", "...")
    b.side("Двор Санни", go)


def nipton(b):
    g = b.g

    def luis():
        b.visit("nipton_mine", clear=False)
        b.chat("np_captive", "вытащу", "вернусь")
        if has(b, "отмычка"):
            b.chat("np_captive", "вытащу", "вскрыть", "Беги")
        elif caps(b) >= 400:
            b.chat("brother_t", "Продай", "...")
        else:
            raise b.Stuck("нечем открыть клетку")
    b.side("Луис из Примма: клетка", luis)

    def irma():
        b.visit("nipton_camp", clear=False)
        b.chat("groom_c", "осталась", "Как тебя звали", "Понимаю")
        b.visit("nipton", clear=False)
        b.chat("grace_widow", "Ирма", "Отнесу")
        b.visit("nipton_camp", clear=False)
        b.talk("groom_c")
        b.say("платок")
        if b.say("Жребия больше нет", required=False):
            b.say("...")
            b.end_talk()
            return
        b.say("строчку")
        b.say("Передам")
        b.end_talk()
        b.visit("nipton", clear=False)
        b.chat("grace_widow", "Письмо", "...")
    b.side("Честная клетка", irma)

    def fair():
        if not g.flags.get("nipton_mayor_exposed"):
            raise b.Stuck("пока жребий жив — ярмарки нет")
        b.visit("nipton", clear=False)
        b.chat("np_crier", "вместо жребия", "Конкурс пирогов", "бабка Мэй", "...", "...")
        b.visit("nipton_camp", clear=False)
        b.chat("groom_cal", "Бусы", "...")
    b.side("Ярмарка без жребия", fair)


def luis_home(b):
    g = b.g

    def go():
        if not g.flags.get("luis_free") or g.stage("sq_luis") >= 100:
            return
        b.visit("primm_bison", clear=False)
        b.chat("pr_manager", "Луис свободен", "...")
    b.side("Луис из Примма", go)


# ================================================================ Письма почтальона (sq_letters)
# Конверты из мешка Почтальона-3000: адресат — тот, кто живёт в том же городе, что и адрес.
MAIL = (("mae_reeves", "письмо: Ривзам, Примм", "mail_done_reeves", "Ривзам, Примм"),
        ("mayor_darkwater", "письмо: Дарквотеру, Джанктаун", "mail_done_darkwater", "Дарквотеру, Джанктаун"),
        ("anna_shaw", "письмо: доктору Шоу, Бейкерсфилд", "mail_done_shaw", "доктору Шоу, Бейкерсфилд"),
        ("beatrice", "письмо: смотрителю Убежища 15", "mail_done_vault15", "смотрителю Убежища 15"),
        ("springer", "письмо: Спрингеру, Зайзикс", "mail_done_springer", "Спрингеру, Зайзикс"),
        ("harold", "письмо: Р. Грею, Хаб", "mail_done_grey", "Р. Грею, Хаб"))


def mail_sack(b):
    """Почтальон-3000 в пустоши: мешок писем 2077 года. Восьмое — жителям Убежища 13 — доставить
    некуда: дверь откроется не скоро, оно так и останется в рюкзаке (как и задумано квестом)."""
    g = b.g
    if g.flags.get("mail_sack"):
        return
    b.encounter("robot")
    b.chat("robot", "недоставленное", "Доставлю")
    letters = [k for k in g.inventory.nonzero() if k.startswith("письмо: ")]
    if not g.flags.get("mail_sack") or len(letters) != 8:
        raise b.Stuck(f"мешок не отдали: писем {len(letters)}, стадия {g.stage('sq_letters')}")
    g.go_world_map()


def mail_to(b, npc, item, flag):
    """Отнести конверт адресату. Чужие письма бот не вскрывает — отдаёт в руки (вскрытие — карма −2).
    Если герой в другом городе (или на карте пустоши) — бот идёт по карте мира к адресату."""
    g = b.g
    if g.flags.get(flag) or not g.flags.get("mail_sack"):
        return bool(g.flags.get(flag))
    if not has(b, item):
        raise b.Stuck(f"конверта «{item}» в рюкзаке нет")
    b.portal_graph()
    home = b._npc_home.get(npc)
    if home:
        try:
            city = b.city_of(home)
        except b.Stuck:
            raise b.Stuck(f"город адресата ({home}) ещё не открыт на карте мира")
        try:
            here = b.city_of(g.loc.id)
        except b.Stuck:
            here = None                       # стоим на карте пустоши или во встрече — дверей нет
        if here != city:
            g.go_world_map()
            b.go(city)
    b.chat(npc, "У меня для вас письмо", "...")
    if not g.flags.get(flag):
        raise b.Stuck(f"{npc} письмо не взял")
    return True


def mail(b, npc, item, flag, where=""):
    """Доставка письма как побочка: не вышло — причина в side_fails, маршрут идёт дальше."""
    b.side(f"Письма: {where or npc}", lambda: mail_to(b, npc, item, flag))


def mail_house(b):
    """Хаусу письмо не отдать в руки: в Стрипе только терминал «Лаки 38» и щель для почты."""
    g = b.g
    if g.flags.get("mail_done_house") or not g.flags.get("mail_sack"):
        return
    if not has(b, "письмо: мистеру Р. Хаусу, Лаки 38"):
        raise b.Stuck("письма Хаусу в рюкзаке нет")
    b.visit("vegas_strip", clear=False)
    b.terminal("lucky38_door", "Опустить письмо")
    if not g.flags.get("mail_done_house"):
        raise b.Stuck("терминал «Лаки 38» письмо не принял")


def mail_sisters(b):
    """Эхо письма Убежища 15: Беатрис знает про раскол — Лейла идёт мириться. Это уже после
    Убежища 15, поэтому визит в Арадеш идёт обходом, а не по прямой дороге акта."""
    g = b.g
    if g.flags.get("sisters_reconciled") or not g.flags.get("beatrice_knows"):
        return
    g.go_world_map()
    b.go("aradesh")
    b.visit("aradesh_hall", clear=False)
    b.chat("aradesh_wife", "Беатрис знает", "Передам")


# ================================================================ Контракт на Барстоу (sq_merc)
def merc_bail(g):
    """Контракт не вышел — вернуть управление герою там, где он ждал, без выдуманных флагов:
    караван остался в Барстоу, квест так и не закрыт (и это видно в отчёте).
    Если Дэкс погиб — это смерть наёмника, а не героя: экран смерти снимаем, причина провала
    уже записана в отчёт."""
    if not g.merc_mode:
        return
    hero, g.other_profile = g.other_profile, None
    g.dex_profile = g.capture_profile()
    g.merc_mode = False
    g.game_over = False
    g.restore_profile(hero)
    g.log("Дэкс вернулся в Пятнадцатую ни с чем: контракт не закрыт.")


def merc_contract(b):
    """«Контракт на Барстоу»: нанять Дэкса в Пятнадцатой и отработать контракт за него.

    Дэкс — не герой: в Барстоу игра идёт в экшене (src/action.py, «action» у локации), поэтому
    бот целится мышью, держит гашетку, перезаряжает и отходит, когда гуль подошёл вплотную
    (b.action_clear). Платит бот своими крышками, ветку берёт по своим козырям: перк «серебряный
    язык» — даром, слово шерифа (крысолюды в ливнёвке пройдены) — пятьдесят, иначе сотня.
    Нет ни денег, ни козырей — честная причина, а не тихая потеря. Заодно город чистится
    от гулей (депо и центр), и Роза платит уже Дэксу, а герою — доля.
    """
    g = b.g
    from src.combat import rect_pos_for_tile
    if g.stage("sq_merc") >= 100:
        return
    if g.merc_mode:
        raise b.Stuck("уже играем за Дэкса — контракт начат не с начала")
    if g.loc.id != "ruins":
        g.go_world_map()
        b.go("ruins")
    if g.stage("sq_merc") < 10:
        b.chat("dex", "Кто ты?", "Караван нужен")
    caps = g.inventory.count("крышки")
    tongue = g.check_condition({"perk": "silver_tongue"})
    if not tongue and caps < 100 and (not g.flags.get("rats_reward_done") or caps < 50):
        for t in ("gena", "doc", "mo"):               # нечем платить — сдать хлам в Пятнадцатой
            if any(n.npc_id == t for n in g.npcs) and t in g.traders:
                try:
                    b.shop(t)
                except b.Stuck:
                    pass
            caps = g.inventory.count("крышки")
            if caps >= 100 or (g.flags.get("rats_reward_done") and caps >= 50):
                break
    if tongue:
        pay = "Караван — это и твои деньги"
    elif g.flags.get("rats_reward_done") and caps >= 50:
        pay = "Шериф за меня поручится"
    elif caps >= 100:
        pay = "Держи сотню"
    else:
        raise b.Stuck(f"наёмник просит сотню крышек, а их {caps} (слово шерифа: "
                      f"{bool(g.flags.get('rats_reward_done'))}, серебряный язык: {tongue})")
    b.chat("dex", "Нанимаю", pay, "Удачи, Дэкс")
    if not g.merc_mode:
        raise b.Stuck("слайды «Тем временем» не перевели управление на Дэкса")
    try:
        b.action_clear("двор Барстоу")                    # 8 гулей и толпа из развалин
        b.chat("rose", "Могу помочь с гулями", "Договорились")
        for area in ("barstow_depot", "barstow_center"):
            if g.flags.get(area + "_cleared"):
                continue
            b.goto_portal(area)
            b.action_clear(area)
            b.goto_portal("barstow")
        if g.stage("sq_barstow") < 100:
            b.chat("rose", "Депо и центр чисты")
        if g.stage("sq_barstow") < 100:
            raise b.Stuck(f"Роза не расплатилась: депо {bool(g.flags.get('barstow_depot_cleared'))}, "
                          f"центр {bool(g.flags.get('barstow_center_cleared'))}, стадия {g.stage('sq_barstow')}")
        exit_tile = sorted(g.level.exits)[0]              # Дэкс уходит с трассы только с закрытым контрактом
        g.player.rect.topleft = rect_pos_for_tile(g.player, exit_tile)
        g.snap_camera()
        b.fr(6)                                           # слайды «Дорога домой» → merc_finish
    except b.Stuck:
        merc_bail(g)
        raise
    if g.merc_mode:
        raise b.Stuck("Дэкс не ушёл из Барстоу — контракт не закрыт")
    b.chat("dex", "Спасибо, Дэкс")
    if g.stage("sq_merc") < 100:
        raise b.Stuck(f"долю не отдал (стадия {g.stage('sq_merc')})")


# ================================================================ Пропавшие караваны (sq_caravans)
def caravans_take(b):
    """Взять заказ у Маргарет Крэйн и не называть Ханов, пока нет улик: неделя на правду."""
    g = b.g
    if g.flags.get("caravans_job") or g.stage("sq_caravans") >= 100:
        return
    b.visit("hub", clear=False)
    b.chat("crimson_boss", "пропадают караваны", "Дай мне время", "Договорились")
    if not g.flags.get("caravans_job"):
        raise b.Stuck("Маргарет не дала времени искать правду")
    b.chat("caravan_lars", "Кто напал", "Спасибо")        # «брод держи» — так говорят речники


def caravans_wreck(b):
    """Сгоревший фургон у заставы на I-15: стрела с заводским клеймом и обрывок накладной."""
    g = b.g
    if g.stage("sq_caravans") >= 100 or not g.flags.get("caravans_job"):
        return
    if g.flags.get("clue_arrow") and g.flags.get("clue_route"):
        return
    g.reveal_location("spot_toll")                        # заставу видно с трассы, квест её и называет
    g.go_world_map()
    b.go("spot_toll")
    b.clear(max_rounds=15)
    b.take_from("сожжённый фургон каравана")
    b.read_books()                                        # стрела и накладная читаются из рюкзака
    missing = [n for f, n in (("clue_arrow", "стрела"), ("clue_route", "накладная")) if not g.flags.get(f)]
    if missing:
        raise b.Stuck(f"фургон обыскан, но улик нет: {', '.join(missing)}")


def caravans_toll(b):
    """Журнал пошлин моста: маршруты Красного каравана проданы «белым», подпись Б."""
    g = b.g
    if g.stage("sq_caravans") >= 100 or not g.flags.get("caravans_job") or g.flags.get("clue_toll"):
        return
    g.go_world_map()
    b.go("needles")
    b.goto_portal("needles_bridge")
    b.terminal("needles_toll", "Платные проводки")
    if not g.flags.get("clue_toll"):
        raise b.Stuck("журнал «Платные проводки» не открылся: пароля нет, взлом не удался")


def caravans_billy(b):
    """Билли с моста: ветку бот берёт по навыку — Красноречие 60 (двойная игра) или паром Кейт."""
    g = b.g
    if g.flags.get("billy_turned") or g.stage("sq_caravans") >= 100:
        return
    if not (g.flags.get("clue_toll") or g.flags.get("clue_survivor")):
        raise b.Stuck("Билли не с чем прижать: нет ни журнала пошлин, ни слов Ларса")
    g.go_world_map()
    b.go("needles")
    b.goto_portal("needles_bridge")
    if b.g.player.skill("speech") >= 60:
        b.chat("billy", "платные проводки", "Есть способ искупить", "Договорились")
    elif g.flags.get("ferry_done"):
        b.chat("billy", "платные проводки", "Пойдём к матери", "Пойдём")
    else:
        raise b.Stuck(f"Билли не прижать: Красноречие {b.g.player.skill('speech')} < 60, "
                      "а Кейт не доверяет — паром не переправлен")
    if not g.flags.get("billy_turned"):
        b.go("needles")
        b.chat("kate", "Билли должен", "...")             # Кейт сама решает за сына
    if not g.flags.get("billy_turned"):
        raise b.Stuck("Билли не согласился сливать маршруты культа")


def caravans_finish(b):
    """Назвать виновного: полная правда (Билли) — если есть три улики и он сдался; иначе — культ."""
    g = b.g
    if g.stage("sq_caravans") >= 100 or not g.flags.get("caravans_job"):
        return
    clues = {"clue_arrow": "стрела с клеймом", "clue_cargo": "журнал фургона культа", "clue_toll": "журнал пошлин"}
    missing = [n for f, n in clues.items() if not g.flags.get(f)]
    g.go_world_map()
    b.go("hub")
    if not missing and g.flags.get("billy_turned"):
        b.chat("crimson_boss", "Я знаю, кто виноват", "Стражник Билли", "С ним разобрались", "...")
    elif g.flags.get("clue_cargo"):
        b.chat("crimson_boss", "Я знаю, кто виноват", "забирает культ", "...")
    else:
        raise b.Stuck(f"назвать некого: не хватает улик — {', '.join(missing) or 'журнала фургона'}")
    if g.stage("sq_caravans") < 100:
        raise b.Stuck(f"Красный караван не принял версию (стадия {g.stage('sq_caravans')})")


def caravans_rounds(b):
    """Обход конца акта II: застава, мост, Билли — и правда в Хаб. Каждый шаг — своя причина провала."""
    b.side("Пропавшие караваны: фургон", lambda: caravans_wreck(b))
    b.side("Пропавшие караваны: журнал моста", lambda: caravans_toll(b))
    b.side("Пропавшие караваны: Билли", lambda: caravans_billy(b))
    b.side("Пропавшие караваны: виновный", lambda: caravans_finish(b))


# ================================================================ Экспедиция Гарольда (sq_harold)
def harold_story(b):
    """Гарольд в Старом городе: Грей выжил в купели, а в Марипозу есть грузовой въезд с краном."""
    g = b.g
    if g.flags.get("know_cargo_bay"):
        return
    b.visit("hub_old", clear=False)
    b.chat("harold", "Что с тобой", "А потом", "Ещё вопрос", "Создатель", "Как попасть", "Передам")
    if not g.flags.get("know_cargo_bay"):
        raise b.Stuck(f"Гарольд не рассказал про грузовой въезд (стадия {g.stage('sq_harold')})")


def harold_finish(b):
    """Журнал «Купели» в Марипозе: подпись «Р. Грей. Создатель» — Гарольд был прав."""
    g = b.g
    if g.stage("sq_harold") >= 100:
        return
    if not g.flags.get("know_master_origin"):
        raise b.Stuck("журнал «Купели» закрыт: герой не знает, кого искать — Гарольд не рассказал")
    b.visit("mariposa_vats", clear=False)
    b.terminal("mariposa_1977", "Купели")
    if g.stage("sq_harold") < 100:
        raise b.Stuck("журнал «Купели» не прочитан")


def vegas(b):
    g = b.g

    def milo():
        b.visit("vegas_snakes", clear=False)
        b.chat("snake_gambler", "выиграть", "Сколько", "придумаю")
        b.visit("vegas_den", clear=False)
        b.chat("mother_snake", "Долг Мило", "перстнем", "...")
    b.side("Человек, который сидит и играет", milo)

    def coin():
        b.visit("vegas_strip", clear=False)
        b.chat("strip_kid", "главный", "всегда прав", "Проверю")
        b.chat("judge_sol", "монету", ("десять раз", "кости Гизмо"), ("...", "Верну"), "Верну")
        b.visit("vegas_den", clear=False)
        if not has(b, "монета судьи Сола") and skill(b, "speech") >= 65:   # порог диалога, не 70
            b.chat("den_dealer", "Монета судьи", "Красноречие", "...")
        if not has(b, "монета судьи Сола") and caps(b) >= 200:             # та же ветка за деньги
            b.chat("den_dealer", "Монета судьи", "Двести", "...")
        if not has(b, "монета судьи Сола"):                                # второй путь: услуга Матери-Змее
            if not has(b, "фальшивая монета"):
                raise b.Stuck("фальшивки нет — Матери-Змее нечего предложить")
            b.chat("mother_snake", "Монета у твоего крупье", "Проведу")
        if not has(b, "монета судьи Сола"):
            raise b.Stuck("крупье монету не отдал ни словами, ни деньгами, ни услугой")
        b.visit("vegas_strip", clear=False)
        b.chat("judge_sol", "Настоящая", "...")
    b.side("Монета судьи", coin)

    def hank():
        b.visit("vegas_boots", clear=False)
        b.chat("boots_rider_c", "Что с Хэнком", "вылечить", "Схожу")
        if not g.flags.get("know_hank_zz"):
            b.visit("vegas_palms", clear=False)
            b.chat("palms_doctor", "лёгкими", "Спасибо")
        if not has(b, "вода Зайзикса", 2) and not g.flags.get("hank_done"):
            try:                                  # второй путь: две бутыли у Абдула (60 крышек)
                b.visit("zzyzx", clear=False)
                b.buy_from("merchant_zz", "вода Зайзикса", 2)
            except b.Stuck:
                pass
        b.visit("vegas_boots", clear=False)
        if not g.flags.get("hank_done") and has(b, "вода Зайзикса", 2):
            b.chat("hank_spur", "Выпей", "Бесплодие", "...")
        elif not g.flags.get("hank_done") and (g.flags.get("boots_member") or g.flags.get("boots_job1")):
            b.chat("hank_spur", "Кто поведёт", "Бетт", "...")   # наследника можно назвать и по подкове
        elif not g.flags.get("hank_done"):
            raise b.Stuck("нет воды Зайзикса, а назвать наследника нечем")
    b.side("Лёгкие Шпоры", hank)

    def shops():                      # у Змей — силовой кулак и кувалда, у дилера Стрипа — плазма и шлем
        for m in ("vegas_snakes", "vegas_strip"):
            b.visit(m, clear=False)
            b.shop_here()
    b.side("Вегас: лавки", shops)
