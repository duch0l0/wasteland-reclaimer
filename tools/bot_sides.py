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


# ================================================================ Хаб (акт II)
def hub_start(b):
    g = b.g

    def falcon():
        b.visit("hub_falcon", clear=False)
        b.chat("falcon_barkeep", "серый", "Кто знал", "Поспрашиваю")
        b.chat("falcon_singer", "Кто был в баре", "Спасибо")
        b.chat("falcon_gambler", "Лулу видела", "Посмотрим")
        if caps(b) < 100:
            raise b.Stuck("не хватает сотни на ключ Декера")
        b.chat("decker", "Птица Винни", ("Красноречие", "Сто крышек"), ("...", "Спасибо"))
        b.walk_to_map("hub_old")
        b.take_from("сейф Декера")
        b.chat("falcon_barkeep", "Твоя птица", "Свинец", "...")
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


def hub_finish(b):
    """После Джанктауна: лекарство доктора Шоу — ребёнку, антидот — Вилли, торговца — страже."""
    g = b.g

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
        if skill(b, "speech") < 70:
            raise b.Stuck("кости у Веры — без Красноречия не отдаст")
        b.chat("croupier", "Кости", "Отдай", "Спасибо")
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
        if g.flags.get("bell_jammed") and has(b, "дубликат передатчика"):
            b.visit("hub", clear=False)
            b.chat("bos_scout", "маяк 3", "...")
        elif has(b, "динамит"):
            b.visit("boneyard", clear=False)
            b.chat("adytum_worker", "динамит", "...")
        else:
            raise b.Stuck("нечем взорвать колокольню")
    b.side("Колокольня", go)


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
        if not has(b, "противогаз"):
            raise b.Stuck("без противогаза — 350 рад, игрок бы не нырнул")
        b.chat("kate", "Цемент у меня", "химзащиты", "...")
        b.cure_rads()
        if 0 < g.stage("sq_noa") < 100 and g.flags.get("ferry_done"):
            b.chat("noa_runaway", "Кейт", "...")
    b.side("Жёлтые треугольники", go)


# ================================================================ Бейкер (акт I)
def baker(b):
    g = b.g

    def thermo():
        b.visit("baker", clear=False)
        b.chat("nick", "Термометр", "Посмотрю")
        if skill(b, "science") < 50:
            raise b.Stuck("без Науки градусник не прочесть")
        b.chat("baker_kid", "на самом деле", "Наука", "жара")
        b.chat("nick", "работает", "...")
    b.side("Термометр", thermo)

    def smile():
        DAY = 24 * 60
        b.visit("baker_motel_2f", clear=False)
        b.chat("motel_mom", "муж", "Узнаю")
        if not has(b, "ключ от крипты"):          # ключ — в сундуке Ансельма, взять тихо
            b.steal("baker_mission", "сундук Ансельма")
        if not has(b, "ключ от крипты"):
            raise b.Stuck("ключа от крипты нет")
        b.visit("baker_mission", clear=False)
        b.walk_to_map("baker_crypt")
        b.chat("oskar", "вернулся", "Спасибо")
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
        if skill(b, "science") < 70:
            raise b.Stuck("рельсы без Науки не проверить — запускать вслепую игрок не станет")
        if not has(b, "топливо", 5):
            raise b.Stuck("нет пяти канистр топлива")
        b.chat("pr_mechanic", "Ток для горок", "Пять канистр", "...")
        b.chat("pr_mechanic", "Запускай", "проверю рельсы", "...")
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
        if skill(b, "speech") < 70:
            raise b.Stuck("крупье без Красноречия монету не отдаст")
        b.visit("vegas_den", clear=False)
        b.chat("den_dealer", "Монета судьи", "Красноречие", "...")
        b.visit("vegas_strip", clear=False)
        b.chat("judge_sol", "Настоящая", "...")
    b.side("Монета судьи", coin)

    def hank():
        b.visit("vegas_boots", clear=False)
        b.chat("boots_rider_c", "Что с Хэнком", "вылечить", "Схожу")
        if g.flags.get("boots_member"):
            b.chat("hank_spur", "Кто поведёт", "Бетт", "...")
            return
        b.visit("vegas_palms", clear=False)
        b.chat("palms_doctor", "лёгкими", "Спасибо")
        raise b.Stuck("вода Зайзикса и правда о ней — далеко, Хэнк ждёт")
    b.side("Лёгкие Шпоры", hank)

    def shops():                      # у Змей — силовой кулак и кувалда, у дилера Стрипа — плазма и шлем
        for m in ("vegas_snakes", "vegas_strip"):
            b.visit(m, clear=False)
            b.shop_here()
    b.side("Вегас: лавки", shops)
