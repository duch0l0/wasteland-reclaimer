"""Условия и эффекты из диалогов и терминалов, стадии квестов (data/quests.json), фракции."""
import json
from ..balance import roll_loot

with open("data/quests.json", "r", encoding="utf-8") as f:
    QUESTS = {k: v for k, v in json.load(f).items() if not k.startswith("_")}


# квест -> [(стадия, условие)]: условие — флаг, список флагов «любой» или «loc:<id>» (герой там бывал)
STORY_STEPS = [
    ("mq_list", [(10, "baker_done"), (20, ["dolores_trust", "know_vega_mariposa"]), (30, ["anna_trust", "know_cobbs_necropolis"]),
                 (40, ["cobbs_clear", "know_set_deal"]), (50, ["know_vt_vre", "cooper_card"]),
                 (60, ["know_enclave_hint", "know_convoy_cargo"]), (100, "loc:primm")]),
    ("mq_zero", [(10, ["know_zero", "know_amos_manifest"]), (20, ["know_cult_race", "brother_t_flees"]),
                 (30, ["know_poseidon", "know_general_puppet"]), (40, "loc:vegas_strip"), (50, "zero_open"),
                 (60, "zero_fate"), (100, "game_ending")]),
    ("sq_order", [(10, "order_found"), (100, "order_member")]),
    ("sq_zzyzx", [(10, "loc:zzyzx"), (50, ["know_clean_slate", "springer_confessed"]), (100, ["clean_slate_off", "springer_safe", "springer_spared"])]),
    ("sq_needles", [(10, "loc:needles"), (50, ["know_barge", "morrow_suspicious"]), (100, "know_cult_convoys")]),
    ("sq_hub", [(10, ["dolores_tunnels", "know_cult_water"]), (50, "know_sluice"), (100, "sluice_restored")]),
    ("sq_junktown", [(10, "know_rourke"), (50, ["know_rourke_cult", "know_gizmo_cult"]), (100, ["rourke_paid", "anna_debt_cleared"])]),
    ("sq_necropolis", [(10, "know_set_deal"), (50, ["v12_way", "harry_job"]), (100, "set_refuses")]),
    ("sq_aradesh", [(10, ["aradesh_job", "know_spring_cave"]), (100, "aradesh_free_water")]),
    ("sq_boneyard", [(10, ["adytum_job", "blades_job"]), (50, ["nika_knows", "know_morpheus_deal"]), (100, "adytum_truce")]),
    ("sq_vault15", [(10, ["know_mira", "loc:vault15"]), (50, ["v15_lower_ok", "beatrice_trust"]), (100, "v15_power")]),
    ("sq_vault4", [(10, ["v4_open", "know_v4_science"]), (100, "v4_deal_off")]),
    ("sq_primm", [(10, ["primm_job", "know_tobi_missing"]), (50, "mae_suspect"), (100, "tobi_home")]),
    ("sq_goodsprings", [(10, ["know_ezekiel", "ezekiel_listened"]), (100, "gs_decided")]),
    ("sq_vault22", [(10, ["hugo_known", "know_v22_smell"]), (50, "know_v22_spores"), (100, ["v22_decided", "hugo_joins"])]),
    ("sq_nipton", [(10, ["know_grace", "know_lottery_past", "loc:nipton"]), (50, ["know_lottery_rigged", "nipton_mayor_caught"]),
                   (100, "nipton_decided")]),
    ("sq_searchlight", [(10, "fort_job"), (50, ["know_general_puppet", "know_general_orders"]), (100, "recruits_free")]),
    ("sq_vegas", [(10, ["know_crowns", "loc:vegas_strip"]), (50, ["boots_secret", "snakes_secret", "palms_secret"]),
                  (100, ["crowns_united", "boots_member", "snakes_member", "palms_member"])]),
    ("sq_poseidon", [(10, "loc:poseidon7"), (50, "know_enclave_purge"),
                     (100, ["p7_deal_done", "p7_vertibird_stolen", "p7_sabotage", "darnell_home"])]),
    ("sq_truck", [(10, "truck_job"), (100, "truck_done")]),
    ("sq_runaway", [(10, "runaway_job"), (100, "runaway_done")]),
    ("sq_falcon", [(10, "falcon_job"), (50, "know_falcon_decker"), (100, "falcon_done")]),
    ("sq_fever", [(10, "fever_job"), (50, "fever_cured"), (100, "fever_done")]),
    ("sq_blue", [(10, "blue_job"), (50, "know_blue_seller"), (100, "blue_done")]),
    ("sq_gizmo", [(10, "gizmo_offer"), (50, ["mayor_knows", "gizmo_peace", "mayor_poisoned"]), (100, "gizmo_done")]),
    ("sq_robes", [(10, "robes_job"), (100, "robes_done")]),
    ("sq_fox", [(10, "fox_job"), (50, ["fox_reel", "fox_projector"]), (100, "fox_done")]),
    ("sq_ferals", [(10, "ferals_job"), (50, ["ferals_clue", "ferals_journal"]), (100, "ferals_done")]),
    ("sq_beach", [(10, "beach_job"), (50, "beach_known"), (100, "beach_done")]),
    ("sq_karl", [(10, "karl_job"), (50, "karl_harmonica"), (100, "karl_done")]),
    ("sq_letters_by", [(10, "lt_job"), (50, "lt_letters"), (100, "lt_done")]),
    ("sq_bell", [(10, "bell_job"), (50, "know_cult_beacon"), (100, "bell_done")]),
    ("sq_luis", [(10, ["luis_job", "luis_rita"]), (50, "luis_free"), (100, "luis_home")]),
    ("sq_irma", [(10, "irma_name"), (50, "irma_job"), (100, "irma_done")]),
    ("sq_fair", [(10, "fair_job"), (100, "fair_done")]),
    ("sq_hank", [(10, "hank_job"), (50, ["know_hank_zz", "know_zz_truth"]), (100, "hank_done")]),
    ("sq_coin", [(10, "coin_job"), (50, "coin_fake"), (100, "coin_done")]),
    ("sq_milo", [(10, "milo_job"), (100, ["milo_done", "gambler_eaten"])]),
    ("sq_barge", [(10, "barge_job"), (50, "barge_vic"), (100, "barge_done")]),
    ("sq_noa", [(10, "noa_job"), (50, "noa_talked"), (100, "noa_done")]),
    ("sq_ringo", [(10, "ringo_job"), (100, "ringo_done")]),
    ("sq_spring", [(10, "spring_job"), (50, "gs_cave_cleared"), (100, "spring_done")]),
    ("sq_coaster", [(10, "coaster_job"), (50, "coaster_power"), (100, "coaster_done")]),
    ("sq_bonnie", [(10, "bonnie_job"), (100, "bc_code")]),
    ("sq_smile", [(10, "smile_job"), (50, "smile_started"), (100, ["smile_back", "smile_lost"])]),
    ("sq_thermo", [(10, "thermo_job"), (100, "thermo_done")]),
    ("sq_fred", [(10, "fred_job"), (50, ["fred_vera", "know_dice"]), (100, "fred_done")]),
    ("sq_tag", [(10, "tag_job"), (100, "tag_done")]),
    ("sq_bike", [(10, "bike_job"), (100, "bike_done")]),
    ("sq_treasure", [(10, "treasure_piece"), (50, "treasure_map"), (100, "treasure_dug")]),
    ("sq_murder", [(50, "murder_ready")]),
    ("sq_letters", [(50, "mail_half"), (100, "mail_all")]),
    ("sq_caravans", [(30, "caravans_lead"), (60, "caravans_picture")]),
    ("sq_harold", [(10, "harold_story"), (50, "know_cargo_bay"), (100, "know_master_vat")]),
    ("sq_water_war", [(50, "clue_middleman")]),
    ("sq_vault11", [(10, "know_vault11"), (50, "know_v11_truth")]),
    ("sq_heist", [(50, "bank_vault_open")]),
    ("sq_catalina", [(10, "loc:catalina"), (50, ["know_ct_tribute", "know_ct_lie"]), (100, "ct_tribute_stopped")]),
    ("sq_nova", [(10, "loc:nova"), (50, ["know_nova_vre", "nova_rebels_ally"]), (100, "nova_decided")]),
    ("sq_ares", [(10, "loc:repconn"), (50, "loc:ares"), (100, "ares_decided")]),
]


# флаг -> [(квест, стадия)]: какие стадии двигает этот флаг (для отметки квестодателя)
FLAG_STAGES = {}
for _qid, _steps in STORY_STEPS:
    for _stage, _cond in _steps:
        for _fl in (_cond if isinstance(_cond, list) else [_cond]):
            if not _fl.startswith("loc:"):
                FLAG_STAGES.setdefault(_fl, []).append((_qid, _stage))


class QuestMixin:
    def quest_mark(self, npc_id):
        """Отметка у курсора над NPC: "new" — у него есть дело (квест ещё не начат), "turn_in" — ждёт
        ответа (реплика двинет начатый квест), None — просто поговорить. Смотрит реплики, доступные
        сейчас, на несколько узлов вглубь."""
        tree = self.dialogue.trees.get(npc_id)
        if not tree:
            return None
        start = tree["start"] if isinstance(tree["start"], list) else [{"node": tree["start"]}]
        first = next((e["node"] for e in start if self.check_condition(e.get("if", {}))), None)
        nodes, seen, queue, mark = tree["nodes"], set(), [first], None
        while queue and len(seen) < 24:
            nid = queue.pop(0)
            if nid is None or nid in seen or nid not in nodes:
                continue
            seen.add(nid)
            node = nodes[nid]
            opts = [o for o in node.get("options", []) if self.check_condition(o.get("if", {}))]
            for eff in [e for o in opts for e in o.get("effects", [])] + node.get("effects", []):
                if eff.get("type") == "quest":
                    moves = [(eff["id"], eff["stage"])]
                elif eff.get("type") == "set_flag" and not self.flags.get(eff["flag"]):
                    moves = FLAG_STAGES.get(eff["flag"], [])
                else:
                    continue
                for qid, stage in moves:
                    now = self.stage(qid)
                    if qid in QUESTS and stage > now:
                        if now > 0:
                            return "turn_in"
                        mark = "new"
            queue += [o.get("next") for o in opts]
        return mark

    def _story_cond(self, cond):
        if isinstance(cond, list):
            return any(self.flags.get(c) for c in cond)
        if cond.startswith("loc:"):
            return cond[4:] in self.locations
        return bool(self.flags.get(cond))

    # ------------------------------------------------------------ квесты
    def stage(self, quest_id):
        return self.quests.get(quest_id, 0)

    def set_stage(self, quest_id, stage):
        """Стадия только растёт: вернуться назад по сюжету нельзя."""
        if stage <= self.stage(quest_id):
            return
        q = QUESTS[quest_id]
        first = quest_id not in self.quests
        self.quests[quest_id] = stage
        if stage >= q.get("done", 10 ** 9):
            self.log(f"Задание выполнено: «{q['title']}».")
            self.on_quest_done(quest_id)
            from ..balance import quest_caps
            caps = quest_caps(quest_id, q.get("main"))
            if caps:
                self.inventory.add("крышки", caps)
                self.log(f"Слух о сделанном расходится — благодарные люди скидываются: +{caps} крышек.")
        else:
            self.log(f"{'Новое задание' if first else 'Журнал обновлён'}: «{q['title']}» (J — журнал).")
        self.journal_sel = quest_id

    def check_condition(self, cond):
        """Условие реплики/стартового узла: flag, not_flag, not_flags (ни одного), flags_any, item+count, no_item, perk,
        skill [навык, не меньше], min_level, stage [квест, не меньше], stage_lt [квест, меньше]."""
        if "stage" in cond and self.stage(cond["stage"][0]) < cond["stage"][1]:
            return False
        # карма и репутация (src/game/reputation.py)
        if "karma_ge" in cond and self.karma < cond["karma_ge"]:
            return False
        if "karma_lt" in cond and self.karma >= cond["karma_lt"]:
            return False
        if "rep_ge" in cond and self.rep(cond["rep_ge"][0]) < cond["rep_ge"][1]:
            return False
        if "rep_lt" in cond and self.rep(cond["rep_lt"][0]) >= cond["rep_lt"][1]:
            return False
        if "title" in cond and cond["title"] not in {t[0] for t in self.titles()}:
            return False
        if "stage_lt" in cond and self.stage(cond["stage_lt"][0]) >= cond["stage_lt"][1]:
            return False
        if "flags_any" in cond and not any(self.flags.get(f) for f in cond["flags_any"]):
            return False
        if "flag_eq" in cond and self.flags.get(cond["flag_eq"][0], 0) != cond["flag_eq"][1]:   # счётчик ровно N
            return False
        if "items_all" in cond and not all(self.inventory.has(i) for i in cond["items_all"]):
            return False
        if "flag_ge" in cond and self.flags.get(cond["flag_ge"][0], 0) < cond["flag_ge"][1]:   # счётчик не меньше N
            return False
        if "night" in cond and self.is_night() != cond["night"]:          # ночь: 20:00–5:00
            return False
        if "weekday" in cond and (self.game_day() - 1) % 7 != cond["weekday"]:   # 0 — пн … 6 — вс
            return False
        if "weekly_free" in cond and self.flags.get(f"{cond['weekly_free']}_w{(self.game_day() - 1) // 7}"):
            return False
        if "at" in cond and not (getattr(self, "loc", None) and self.loc.id.startswith(cond["at"])):   # герой здесь
            return False
        if "count_flags" in cond:      # хотя бы N из списка: [[флаги], N]
            names, need = cond["count_flags"]
            if sum(1 for n in names if self.flags.get(n)) < need:
                return False
        if "flags_all" in cond and not all(self.flags.get(f) for f in cond["flags_all"]):
            return False
        if "no_item" in cond and self.inventory.has(cond["no_item"]):
            return False
        if "items_any" in cond and not any(self.inventory.has(i) for i in cond["items_any"]):   # отмычка или ключ
            return False
        if "flag" in cond and not self.flags.get(cond["flag"]):
            return False
        if "not_flag" in cond and self.flags.get(cond["not_flag"]):
            return False
        if "not_flags" in cond and any(self.flags.get(f) for f in cond["not_flags"]):
            return False
        if "item" in cond and not self.inventory.has(cond["item"], cond.get("count", 1)):
            return False
        if "perk" in cond and not self.player.perk_rank(cond["perk"]):
            # «Подвешенный язык» заменяет высокое Красноречие
            from ..skills import SPEECH_FOR_TONGUE
            if not (cond["perk"] == "silver_tongue" and self.player.skill("speech") >= SPEECH_FOR_TONGUE):
                return False
        if "skill" in cond and self.player.skill(cond["skill"][0]) < cond["skill"][1]:
            return False
        if "skill_lt" in cond and self.player.skill(cond["skill_lt"][0]) >= cond["skill_lt"][1]:   # не хватает навыка
            return False
        if "min_level" in cond and self.player.level_sys.level < cond["min_level"]:
            return False
        return True

    def apply_effect(self, eff):
        if not self.check_condition(eff.get("if", {})):  # у эффекта может быть своё условие
            return
        self._apply_effect(eff)
        self.sync_story()
        self.sync_gates()

    def sync_story(self):
        """Одни и те же факты можно узнать разными путями — здесь они сводятся в стадии квестов."""
        f, st = self.flags, self.stage
        if hasattr(self, "sync_reputation"):
            self.sync_reputation()
        if hasattr(self, "check_deadlines"):
            self.check_deadlines()          # квест взят — срок пошёл сразу (src/game/clock.py)
        if getattr(self, "mode", None) == "local" and getattr(self, "loc", None) is not None:
            self.apply_world_changes()      # решение принято здесь же — город меняется сразу
        if self.inventory.has("чей-то глаз") and 0 < st("mq_grandpa") < 20:
            self.set_stage("mq_grandpa", 20)
        if f.get("know_baker") and 40 <= st("mq_grandpa") < 50:
            self.set_stage("mq_grandpa", 50)
        if st("mq_grandpa") >= 50 and "baker" not in self.worldmap.known:
            self.reveal_location("baker")
        if any(f.get(k) for k in ("route_caravan", "route_lira", "route_loner", "route_silas")):
            f["route_any"] = True
            self.set_stage("mq_grandpa", 60)
        if any(f.get(k) for k in ("gang_dead", "gang_left", "gang_paid")) and 0 < st("sq_gang") < 50:
            self.set_stage("sq_gang", 50)
        if f.get("raiders_dead") and 0 < st("sq_dog") < 50:
            self.set_stage("sq_dog", 50)
        # побочные квесты Пятнадцатой
        if f.get("rats_cleared") and 10 <= st("sq_rats") < 50:
            self.set_stage("sq_rats", 50)
        if self.inventory.has("жетон Эймоса") and st("sq_kolbasa") < 100:
            self.set_stage("sq_kolbasa", 100)
        if f.get("vault_b_open") and st("sq_vault") < 30:
            self.set_stage("sq_vault", 30)
        if self.inventory.has("журнал «Проект Панцирь»") and st("sq_vault") < 50:
            self.set_stage("sq_vault", 50)
        if self.inventory.has("святая вода") and 10 <= st("sq_holywater") < 30:
            self.set_stage("sq_holywater", 30)
        # Барстоу: зачистка районов
        cleared = sum(bool(f.get(k)) for k in ("barstow_depot_cleared", "barstow_center_cleared"))
        if cleared and st("sq_barstow") < 10:
            self.set_stage("sq_barstow", 10)
        if cleared == 1 and st("sq_barstow") < 50:
            self.set_stage("sq_barstow", 50)
        if cleared == 2 and st("sq_barstow") < 90:
            self.set_stage("sq_barstow", 90)
        if self.inventory.has("кинолента «Атомный рейнджер»"):
            f["fox_reel"] = True
        if self.inventory.has("журнал Дейва"):
            f["ferals_journal"] = True
        if self.inventory.has("пачка писем «родным»"):
            f["lt_letters"] = True
        for crown in ("boots", "snakes", "palms"):      # вступил в Корону — первая ступень ранга
            if f.get(f"{crown}_member") and not f.get(f"{crown}_rank"):
                f[f"{crown}_rank"] = 1
            if f.get(f"{crown}_rank") == 4:
                f[f"{crown}_hand_t"] = True                 # правая рука — голос на совете Корон
        if f.get("grooms_turned"):                       # «женихи» открыли клетки в шахте — Луис бежит домой сам
            f["luis_free"] = True
        if self.inventory.has("кости Гизмо"):            # «Последняя стена»: улика в руках, как бы ни досталась
            f["know_dice"] = True
        # «Карта клада»: три обрывка склеиваются сами, как только все у героя
        pieces = ("обрывок карты (север)", "обрывок карты (центр)", "обрывок карты (юг)")
        if any(self.inventory.has(p) for p in pieces) or self.inventory.has("карта клада"):
            f["treasure_piece"] = True
        if all(self.inventory.has(p) for p in pieces):
            for p in pieces:
                self.inventory.remove(p)
            self.inventory.add("карта клада", 1)
            self.log("Три обрывка совпали по краям. Изолента — и у вас карта клада (рюкзак → прочитать).")
        if self.inventory.has("карта клада"):
            f["treasure_map"] = True
        if self.inventory.has("броня «Пустынный рейнджер»"):
            f["treasure_dug"] = True
        # «Письма почтальона»: семь доставляемых писем (восьмое — Убежищу 13 — не доставить)
        mail = sum(bool(f.get(f"mail_done_{k}")) for k in ("reeves", "darkwater", "shaw", "vault15", "springer", "grey", "house"))
        if mail >= 4:
            f["mail_half"] = True
        if mail >= 7:
            f["mail_all"] = True
        # «Пропавшие караваны»: улики складываются в картину (три из пяти — и уже видно, кто за этим стоит)
        clues = sum(bool(f.get(k)) for k in ("clue_arrow", "clue_route", "clue_toll", "clue_survivor", "clue_cargo"))
        if f.get("caravans_job") and clues >= 1:
            f["caravans_lead"] = True
        if f.get("caravans_job") and clues >= 3:
            f["caravans_picture"] = True
        # «Кто убил Гаррисона?»: фартук с ножом и показания — пора назвать убийцу
        if f.get("clue_apron") and sum(bool(f.get(k)) for k in ("clue_luis", "clue_beth", "clue_hank", "clue_watch")) >= 2:
            f["murder_ready"] = True
        # главные квесты актов II–III и тайные места — стадии по фактам (одно можно узнать разными путями)
        for qid, steps in STORY_STEPS:
            for stage, cond in steps:
                if st(qid) < stage and self._story_cond(cond):
                    self.set_stage(qid, stage)
        if f.get("baker_done") and "zzyzx" not in self.worldmap.known:   # глава 3: Зайзикс
            self.reveal_location("zzyzx")
        if "zzyzx" in self.locations and "needles" not in self.worldmap.known:   # из Зайзикса — дорога на Нидлс
            self.reveal_location("needles")
        if f.get("know_cult_convoys") and "hub" not in self.worldmap.known:   # фургоны культа идут к Хабу — акт II
            self.reveal_location("hub")
        if "hub" in self.locations and "junktown" not in self.worldmap.known:   # из Хаба — караванная дорога в Джанктаун
            self.reveal_location("junktown")
        if ("junktown" in self.locations or f.get("know_cobbs_necropolis")) and "necropolis" not in self.worldmap.known:
            self.reveal_location("necropolis")   # архив Анны Шоу или караванщики Джанктауна — к гулям Бейкерсфилда
        if "necropolis" in self.locations and "aradesh" not in self.worldmap.known:   # гули видели переселенцев на севере
            self.reveal_location("aradesh")
        if "aradesh" in self.locations and "boneyard" not in self.worldmap.known:   # Ханы и журнал фургона — на юг, к руинам ЛА
            self.reveal_location("boneyard")
        if ("boneyard" in self.locations or f.get("know_vault15")) and "vault15" not in self.worldmap.known:
            self.reveal_location("vault15")   # журнал переселенцев или Иона из лагеря Арадеша: «на север, за холмами»
        if f.get("know_vault4") and "vault4" not in self.worldmap.known:   # Купер или сеть убежищ — побережье южнее ЛА
            self.reveal_location("vault4")
        if "vault4" in self.locations and "primm" not in self.worldmap.known:   # акт III: дорога на Мохаве — через Примм
            self.reveal_location("primm")
        if "primm" in self.locations and "goodsprings" not in self.worldmap.known:   # от Примма — старая дорога на север
            self.reveal_location("goodsprings")
        if "goodsprings" in self.locations and "vault22" not in self.worldmap.known:   # из Гудспрингса — тропа к Убежищу 22
            self.reveal_location("vault22")
        if (f.get("know_nipton_lottery") or f.get("know_brother_t_nipton") or "vault22" in self.locations) \
                and "nipton" not in self.worldmap.known:   # голоса Иезекииля или слухи — Ниптон
            self.reveal_location("nipton")
        if "nipton" in self.locations and "searchlight" not in self.worldmap.known:   # из Ниптона — на восток, к Сёрчлайту
            self.reveal_location("searchlight")
        if f.get("fort_bos_storm") and f.get("fort_cleared") and not f.get("fort_decided"):   # Форт взят с паладинами
            for k in ("fort_bos", "recruits_free", "fort_decided", "fort_access"):
                f[k] = True
        if ("searchlight" in self.locations or f.get("know_zero")) and "vegas_strip" not in self.worldmap.known:
            self.reveal_location("vegas_strip")   # хранилище «Ноль» — под башней Vault-Tec в руинах Вегаса
        if f.get("know_vault11") and "vault11" not in self.worldmap.known:   # устав Ярмарки — «выжившая из Убежища 11»
            self.reveal_location("vault11")
        if (f.get("know_poseidon") or f.get("enclave_contact") or f.get("fort_enclave_deal")) \
                and "poseidon7" not in self.worldmap.known:   # канал «П-7» ведёт к станции Анклава
            self.reveal_location("poseidon7")
        from .crime import ENCLAVE_ZONES
        if f.get("enclave_hostile") and getattr(self, "loc", None) is not None and self.loc.id in ENCLAVE_ZONES and \
                (self.npcs or any(not e.hostile for e in self.enemies if e.alive)):
            self.town_turns_hostile()   # тревога на станции: угон, диверсия — все с оружием в бой
        if (f.get("zero_fate") or f.get("brother_t_flees") or f.get("p7_deal_done") or f.get("p7_vertibird_stolen")) \
                and "mariposa" not in self.worldmap.known:   # финал: туда, где всё началось
            self.reveal_location("mariposa")
        if (f.get("crowns_united") or f.get("zero_fate") or f.get("know_nova")) and "nova" not in self.worldmap.known:
            self.reveal_location("nova")   # купол к северо-востоку от Вегаса — слухи на Стрипе
        if (f.get("know_repconn") or "vegas_strip" in self.locations) and "repconn" not in self.worldmap.known:
            self.reveal_location("repconn")   # полигон с ракетой к югу от Вегаса
        if f.get("know_catalina") and "catalina" not in self.worldmap.known:   # остров, который платит дань «флоту»
            self.reveal_location("catalina")
        # «Ноль»: питание, коды совета и двое из Списка Марипозы (сетчатка, голос, код)
        if f.get("zero_power") and f.get("zero_codes") and \
                sum(bool(f.get(k)) for k in ("zero_retina", "zero_voice", "zero_code")) >= 2:
            f["zero_open"] = True
        if self.inventory.has("жетон жребия") and not f.get("nipton_decided"):   # жетон с зазубриной — у героя, вытянут мэр
            f["nipton_token_swapped"] = True
        # Примм: улики против вдовы — две из четырёх, и она уже не может молчать
        if self.inventory.has("письмо культа"):
            f["clue_letter"] = True
        if sum(bool(f.get(k)) for k in ("clue_gun", "clue_shawl", "clue_letter", "clue_log")) >= 2:
            f["mae_suspect"] = True
        if self.inventory.has("доля Панка") and 0 < st("sq_loner") < 50:
            self.set_stage("sq_loner", 50)

    def _apply_effect(self, eff):
        t = eff.get("type")
        if t == "set_flag":
            self.flags[eff["flag"]] = eff.get("value", True)     # value — счётчик (ранг в Короне и т.п.)
        elif t == "disable_enemies":   # пульт охраны: выключить турели / увести роботов в чужой локации
            loc = self.get_location(eff["loc"])
            n = 0
            for e in loc.enemies:
                if e.alive and e.type_id in eff["types"]:
                    e.alive = False
                    n += 1
            loc.enemies[:] = [e for e in loc.enemies if e.alive]
            if eff.get("flag"):
                self.flags[eff["flag"]] = True
            self.log(eff.get("text", f"Отключено: {n}."))
        elif t == "implant":   # операция у хирурга: навсегда, один раз (флаг implant_<id>)
            p = self.player
            stat, n = eff["stat"], eff["amount"]
            if stat == "hp":
                p.max_hp += n
                p.hp = min(p.hp_cap, p.hp + n)
            elif stat == "ac":
                p.ac += n
            elif stat == "ap":
                p.base_ap += n
            elif stat == "dmg":
                p.base_damage += n
            self.flags[f"implant_{eff['id']}"] = True
            self.log(eff.get("text", "Операция прошла успешно."))
        elif t == "hurt":   # сюжетный урон (сбросили в пропасть, ударило током)
            self.player.hp = max(1, self.player.hp - eff["amount"])
            self.log(eff.get("text", f"Вы теряете {eff['amount']} HP."))
        elif t == "karma":
            self.add_karma(eff["amount"], eff.get("why"))
        elif t == "rep":
            self.add_rep(eff["town"], eff["amount"])
        elif t == "clear_flag":
            self.flags.pop(eff["flag"], None)
        elif t == "give":
            self.inventory.add(eff["item"], eff.get("count", 1))
            self.log(f"Получено: {eff['item']} ×{eff.get('count', 1)}")
        elif t == "take":
            self.inventory.remove(eff["item"], eff.get("count", 1))
            self.log(f"Отдано: {eff['item']} ×{eff.get('count', 1)}")
        elif t == "xp":
            if not self.merc_mode:   # за Дэкса опыта нет
                self.log(f"+{eff['amount']} опыта.")
            self.gain_xp(eff["amount"])
        elif t == "trade":
            self.open_trade(eff.get("id", "gena"))
        elif t == "heal":   # врач лечит (за крышки — отдельным эффектом take)
            p = self.player
            p.hp = p.hp_cap if not eff.get("rads") else p.hp
            if eff.get("rads"):
                p.add_rads(-p.rads)
            p.dots = []
            self.log("Док обрабатывает раны. HP восстановлено." if not eff.get("rads")
                     else "Док ставит капельницу антирадина. Радиация выведена.")
        elif t == "caps":
            self.inventory.add("крышки", eff["count"])
            self.log(f"Получено: {eff['count']} крышек.")
        elif t == "reveal":
            self.reveal_location(eff["location"])
        elif t == "fight":
            speaker = self.dialogue_speaker
            if speaker is not None and getattr(speaker, "faction", None):
                self.make_hostile(speaker.faction)
            self.combat.start(player_first=False)
        elif t == "town_fight":   # собеседник и все бойцы локации — в бой (как нападение на жителя)
            speaker = next((n for n in self.npcs if n.npc_id == eff.get("npc")), None)
            target = self.town_turns_hostile(speaker)
            self.combat.start(player_first=False)
            if self.combat.active and target in self.combat.order:
                self.combat.target = target
        elif t == "quest":
            self.set_stage(eff["id"], eff["stage"])
        elif t == "read":
            self.open_document(eff["doc"])
        elif t == "slides":
            self.show_slides(eff["id"])
        elif t == "join_ally":   # спутник-человек идёт с героем (прежний — домой)
            self.join_ally(eff["id"])
        elif t == "leave_ally":
            self.dismiss_ally()
        elif t == "pocket_drop":   # вещь ушла из кармана жителя (отдал сам)
            self.pocket(eff["npc"]).pop(eff["item"], None)
        elif t == "rads":     # сюжетное облучение (нырнул к бочкам)
            self.player.add_rads(eff["amount"])
            self.log(f"Счётчик Гейгера захлёбывается: +{eff['amount']} рад.")
        elif t == "ring_fight":   # ринг «Скам-Питта» (src/game/ring.py)
            self.dialogue.close()
            self.ring_fight(eff.get("bet", 0), eff.get("dive", False))
        elif t == "take_any_book":   # отдать одну любую книгу (Ладоням в библиотеку)
            book = next((n for n in self.inventory.items if n.startswith(("книга", "журнал «")) and
                         n != "журнал Дейва"), None)
            if book:
                self.inventory.remove(book, 1)
                self.log(f"Отдано: {book}.")
        elif t == "caravan_go":    # Крэйн нанимает охранником (src/game/caravan.py)
            self.dialogue.close()
            self.caravan_start(eff["dest"])
        elif t == "caravan_out":
            self.caravan_out(eff["ev"], eff["opt"])
        elif t == "caravan_end":
            self.caravan_end()
        elif t == "inc":       # счётчик +1 (экспонаты музея и т.п.)
            self.flags[eff["flag"]] = self.flags.get(eff["flag"], 0) + eff.get("by", 1)
        elif t == "train":     # платный урок у мастера: навык +amount, полдня занятий
            from .. import skills
            p, sid = self.player, eff["skill"]
            was = p.skill(sid)
            p.skills[sid] = min(skills.CAP, was + eff.get("amount", 5))
            self.advance_time(eff.get("hours", 6) * 60)
            self.log(f"Урок окончен. {skills.SKILL_BY_ID[sid]['name']}: {was} → {p.skills[sid]}.")
        elif t == "fishing":      # рыбалка у причала Нидлса (src/game/fishing.py)
            self.dialogue.close()
            self.fishing_start()
        elif t == "rest":          # отдых: время идёт, раны затягиваются (кино в «Фоксе», ночлег)
            self.advance_time(eff["hours"] * 60)
            self.player.hp = self.player.hp_cap
            self.log(f"Прошло {eff['hours']} ч. Вы отдохнули.")
        elif t == "weekly":        # раз в игровую неделю (ярмарка по воскресеньям)
            self.flags[f"{eff['name']}_w{(self.game_day() - 1) // 7}"] = True
        elif t == "log":
            self.log(eff["text"])
        elif t == "npc_leave":
            self.loc.npcs[:] = [n for n in self.npcs if n.npc_id != eff["npc"]]
            self.flags[f"{eff['npc']}_left"] = True
        elif t == "say":  # герой говорит вслух — облачко над головой
            self.speech = {"ent": self.player, "text": eff["text"], "t": eff.get("ms", 3500)}
            self.log(f"Вы: «{eff['text']}»")
        elif t == "merc_start":
            self.merc_start()
        elif t == "merc_finish":
            self.merc_finish()
        elif t == "baker_assault":
            self.baker_assault()
        elif t == "baker_free_amos":
            self.baker_free_amos()
        elif t == "marla_return":
            self.marla_return()
        elif t == "join_dog":
            self.join_dog()
        elif t == "kill_pack":   # отравили кормушку — стая гибнет в своих норах
            dead = [e for e in self.enemies if e.alive and e.pack == eff["pack"]]
            for e in dead:
                e.hp, e.alive = 0, False
                self.level.add_corpse(e, roll_loot(e.loot))
            if dead:
                self.log("Из глубины тоннелей доносится визг, возня... потом тишина.")
            self._check_cleared()
        elif t == "gang_leave":
            self.loc.enemies[:] = [e for e in self.enemies if e.faction != "gang"]
            self.log("Бензо-банда собирает пожитки и уходит. Заправка свободна.")

    def make_hostile(self, faction):
        """Вся фракция в текущей локации становится враждебной."""
        if not faction:
            return
        for e in self.enemies:
            if e.faction == faction:
                e.hostile = True
        self.flags[f"{faction}_hostile"] = True
