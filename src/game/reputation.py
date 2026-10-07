"""
Карма и репутация — как в Fallout 2: мир помнит, что сделал герой.

  карма          одна на всю пустошь: добрые и подлые поступки (флаги из KARMA_FLAGS, убийства жителей, кражи).
                 От неё — звание («Хранитель пустоши», «Бич трассы»…) и то, как встречают незнакомцы.
  репутация      у каждого города своя: выполненные задания города (+25), поступки (REP_FLAGS), кражи и
                 убийства жителей. От неё — цены у торговцев (до ±15%), реплики жителей, звания города.
  титулы         за особые дела (TITLES): «Гробокопатель», «Детектив Гудспрингса», «Паромщик»…

Всё хранится во флагах (karma, rep_<город>, karma_done_<флаг>) — сохранения не меняются.
Условия для реплик и барков (quests.check_condition):
  {"karma_ge": 100} {"karma_lt": -50} {"rep_ge": ["hub", 30]} {"rep_lt": ["hub", -20]} {"title": "gravedigger"}
Эффекты в диалогах: {"type": "karma", "amount": 20}, {"type": "rep", "town": "hub", "amount": 15}.
"""

# город по id локации (префикс)
TOWNS = {
    "fifteen": ("Пятнадцатая", ("ruins", "town", "fifteen", "drain", "vault57", "cellar", "school", "station")),
    "baker": ("Бейкер", ("baker",)),
    "barstow": ("Барстоу", ("barstow",)),
    "zzyzx": ("Зайзикс", ("zzyzx",)),
    "needles": ("Нидлс", ("needles",)),
    "hub": ("Хаб", ("hub",)),
    "junktown": ("Джанктаун", ("junktown",)),
    "necropolis": ("Некрополь", ("necropolis", "vault12")),
    "aradesh": ("Лагерь Арадеша", ("aradesh",)),
    "boneyard": ("Боунъярд", ("boneyard",)),
    "vault15": ("Убежище 15", ("vault15",)),
    "vault4": ("Убежище 4", ("vault4",)),
    "primm": ("Примм", ("primm",)),
    "goodsprings": ("Гудспрингс", ("goodsprings",)),
    "vault22": ("Убежище 22", ("vault22",)),
    "nipton": ("Ниптон", ("nipton",)),
    "searchlight": ("Сёрчлайт", ("searchlight", "fort")),
    "vegas": ("Вегас", ("vegas",)),
    "catalina": ("Каталина", ("catalina",)),
    "nova": ("«Нова»", ("nova",)),
}

# задание → город, которому оно помогло (выполнено — +25 репутации там)
QUEST_TOWN = {
    "sq_scrap": "fifteen", "sq_gang": "fifteen", "sq_turtle": "fifteen", "sq_den": "fifteen", "sq_water": "fifteen",
    "sq_dog": "fifteen", "sq_rats": "fifteen", "sq_vault": "fifteen", "sq_holywater": "fifteen", "sq_kolbasa": "fifteen",
    "sq_debt": "baker", "sq_roy": "baker", "sq_iskra": "baker", "sq_barstow": "barstow", "sq_merc": "barstow",
    "sq_zzyzx": "zzyzx", "sq_needles": "needles", "sq_ferry": "needles", "sq_hub": "hub", "sq_runaway": "hub",
    "sq_junktown": "junktown", "sq_truck": "junktown", "sq_necropolis": "necropolis", "sq_tag": "necropolis",
    "sq_valves": "necropolis", "sq_aradesh": "aradesh", "sq_boneyard": "boneyard", "sq_sphinx": "boneyard",
    "sq_vault15": "vault15", "sq_vault4": "vault4", "sq_primm": "primm", "sq_treasure": "primm",
    "sq_goodsprings": "goodsprings", "sq_murder": "goodsprings", "sq_vault22": "vault22", "sq_nipton": "nipton",
    "sq_searchlight": "searchlight", "sq_vegas": "vegas", "sq_bike": "vegas", "sq_catalina": "catalina",
    "sq_nova": "nova",
}

# поступки: флаг → карма (срабатывает один раз, когда флаг появился)
KARMA_FLAGS = {
    # акт I
    "clean_slate_off": 60, "springer_confessed": 20, "water_fixed": 20, "marla_home": 25, "loner_share": 15,
    "gang_paid": -10, "gena_robbed": -20, "ferry_done": 10,
    # акт II
    "sluice_restored": 40, "anna_debt_cleared": 25, "set_refuses": 30, "watershed_fixed": 30, "aradesh_free_water": 40,
    "adytum_truce": 40, "mira_free": 40, "v4_deal_off": 30, "runaway_done": 15, "tag_done": 10,
    # акт III
    "tobi_home": 50, "gs_take_boy": 30, "ezekiel_to_cult": -60, "v22_vre_given": -50, "v22_burn_ok": 30,
    "nipton_mayor_exposed": 50, "nipton_bribed": -50, "nipton_mayor_drawn": 20, "recruits_free": 50,
    "gambler_eaten": -70, "snakes_member": -20, "darnell_home": 40, "p7_deal_done": -40, "p7_sabotage": 20,
    "ct_tribute_stopped": 50, "murder_justice": 30, "murder_mercy": 25, "murder_wrong": -50,
    "sphinx_done": 5, "radio_done": 5, "mail_done_reeves": 3, "mail_done_darkwater": 3, "mail_done_shaw": 5, "mail_done_vault15": 3,
    "mail_done_springer": 3, "mail_done_grey": 3, "mail_done_house": 3, "sisters_reconciled": 25, "told_widow": 5, "told_pilgrim": 3, "danny_told": 15, "doris_delivered": 10,
    "beggar_sent_anna": 5, "ending_ash": 50, "ending_steel": 30, "ending_hands": -60,
}

# поступки: флаг → (город, репутация)
REP_FLAGS = {
    "clean_slate_off": ("zzyzx", 20), "springer_safe": ("zzyzx", -30), "gena_robbed": ("fifteen", -30),
    "know_cult_convoys": ("needles", 10), "ferry_done": ("needles", 15),
    "sluice_restored": ("hub", 30), "rourke_paid": ("junktown", 20), "gizmo_exposed": ("junktown", 30),
    "set_refuses": ("necropolis", 30), "aradesh_free_water": ("aradesh", 30), "adytum_truce": ("boneyard", 40),
    "mira_free": ("vault15", 40), "v4_deal_off": ("vault4", 30), "tobi_home": ("primm", 40),
    "gs_take_boy": ("goodsprings", -20), "ezekiel_to_cult": ("goodsprings", -40), "murder_justice": ("goodsprings", 30),
    "murder_wrong": ("goodsprings", -40), "v22_burn_ok": ("vault22", 20), "v22_vre_given": ("vault22", 20),
    "nipton_mayor_exposed": ("nipton", 50), "nipton_bribed": ("nipton", -30), "recruits_free": ("searchlight", 50),
    "crowns_united": ("vegas", 40), "gambler_eaten": ("vegas", -20), "ct_tribute_stopped": ("catalina", 50),
    "nova_rebels_ally": ("nova", 30),
}

# звание по карме
KARMA_TITLES = [(500, "Святой пустоши"), (250, "Хранитель пустоши"), (100, "Добрый странник"), (-99, "Бродяга"),
                (-249, "Сомнительный тип"), (-499, "Бич трассы"), (-10 ** 9, "Чума пустоши")]
# отношение города
REP_RANKS = [(100, "Идол"), (50, "Друг"), (15, "Свой"), (-14, "Чужак"), (-49, "Не любят"), (-10 ** 9, "Враг")]

# особые звания за дела — (id, название, описание, условие)
TITLES = [
    ("gravedigger", "Гробокопатель", "Раскопал могилу Колбасы, пустую могилу Некрополя и клад у Примма.",
     {"flags_all": ["tag_done", "treasure_dug"], "stage": ["sq_kolbasa", 100]}),
    ("detective", "Детектив Гудспрингса", "Нашёл убийцу Гаррисона.", {"flags_any": ["murder_justice", "murder_mercy"]}),
    ("ferryman", "Паромщик", "Переправил Бакса, Генриетту и кукурузу через Колорадо.", {"flag": "ferry_done"}),
    ("voice", "Оператор «Маяк»", "Принят «Голосом пустоши» по позывному.", {"flag": "radio_done"}),
    ("visitor", "Посетитель года", "Ответил на загадки Сфинкса.", {"flag": "sphinx_done"}),
    ("plumber", "Сантехник пустоши", "Перекрыл контур в Пятнадцатой, открыл шлюз Хаба, починил Водораздел и вентили "
     "Убежища 12.", {"flags_all": ["water_fixed", "sluice_restored", "watershed_fixed", "valves_done"]}),
    ("legend_hunter", "Охотник за легендами", "Добыл три легендарных ствола.", {"legends": 3}),
    ("liberator", "Освободитель", "Вернул домой Миру, Тоби и Дарнелла.", {"flags_all": ["mira_free", "tobi_home", "darnell_home"]}),
    ("butcher", "Мясник", "Убил больше десятка мирных жителей.", {"killed_civ": 10}),
    ("orderly", "Брат ложи", "Принят в Орден Тайн.", {"flag": "order_member"}),
    ("grail", "Рыцарь Моста", "Знал, что спросить у Хранителя моста.", {"flag": "bridge_won"}),
    ("postman", "Почтальон пустоши", "Доставил все письма 2077 года, которые ещё можно было доставить.", {"flag": "mail_all"}),
    ("courier", "Курьер поневоле", "Нашёл чип, который так и не доехал до Убежища 13.", {"flag": "know_vault13_chip"}),
    ("whale", "Свидетель кита", "Видел кита, упавшего с неба. И петунию.", {"flag": "enc_whale"}),
    ("tourist", "Пассажир синей будки", "Нашёл в пустыне синюю будку. Она нашла тебя.", {"flag": "enc_police_box"}),
    ("abductee", "Контактёр", "Обыскал летающую тарелку.", {"flag": "enc_saucer"}),
]


def rank(value, table):
    return next(name for limit, name in table if value >= limit)


def town_of(loc_id):
    for tid, (_, prefixes) in TOWNS.items():
        if loc_id and loc_id.startswith(prefixes):
            return tid
    return None


class ReputationMixin:
    # ------------------------------------------------------------ значения
    @property
    def karma(self):
        return self.flags.get("karma", 0)

    def rep(self, town):
        return self.flags.get(f"rep_{town}", 0)

    def add_karma(self, n, why=None):
        if not n:
            return
        self.flags["karma"] = self.karma + n
        if why:
            self.log(f"Карма {'+' if n > 0 else ''}{n}: {why}.")

    def add_rep(self, town, n):
        if not n or town not in TOWNS:
            return
        was = rank(self.rep(town), REP_RANKS)
        self.flags[f"rep_{town}"] = self.rep(town) + n
        now = rank(self.rep(town), REP_RANKS)
        if now != was:
            self.log(f"{TOWNS[town][0]}: вас теперь считают — «{now}».")

    def karma_title(self):
        return rank(self.karma, KARMA_TITLES)

    def titles(self):
        return [(tid, name, desc) for tid, name, desc, cond in TITLES if self.title_cond(cond)]

    def title_cond(self, cond):
        from ..weapons import WEAPONS
        cond = dict(cond)
        need = cond.pop("legends", 0)
        if need and sum(1 for w in WEAPONS.values() if w.get("unique") and self.inventory.has(w.get("item", "?"))) < need:
            return False
        civ = cond.pop("killed_civ", 0)
        if civ and self.flags.get("killed_civ", 0) < civ:
            return False
        return self.check_condition(cond) if cond else True

    # ------------------------------------------------------------ поступки
    def sync_reputation(self):
        """Вызывается из sync_story: новые флаги-поступки → карма и репутация (по одному разу)."""
        f = self.flags
        for flag, n in KARMA_FLAGS.items():
            if f.get(flag) and not f.get(f"karma_done_{flag}"):
                f[f"karma_done_{flag}"] = True
                self.add_karma(n)
        for flag, (town, n) in REP_FLAGS.items():
            if f.get(flag) and not f.get(f"rep_done_{flag}"):
                f[f"rep_done_{flag}"] = True
                self.add_rep(town, n)

    def on_quest_done(self, quest_id):
        town = QUEST_TOWN.get(quest_id)
        if town:
            self.add_rep(town, 25)

    def on_npc_killed(self, npc_id):
        """Убит житель (не враг): карма и репутация города падают."""
        town = town_of(self.loc.id) if getattr(self, "loc", None) else None
        self.flags["killed_civ"] = self.flags.get("killed_civ", 0) + 1
        self.add_karma(-25)
        if town:
            self.add_rep(town, -30)

    def on_theft_seen(self):
        town = town_of(self.loc.id) if getattr(self, "loc", None) else None
        self.add_karma(-5)
        if town:
            self.add_rep(town, -15)

    # ------------------------------------------------------------ торговля
    def rep_price_mult(self):
        """Свой — скидка, чужак — наценка: −15%…+15% к цене покупки."""
        town = town_of(self.loc.id) if getattr(self, "loc", None) else None
        r = self.rep(town) if town else 0
        return 1 - max(-0.15, min(0.15, r / 400))
