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
    ("sq_tag", [(10, "tag_job"), (100, "tag_done")]),
    ("sq_bike", [(10, "bike_job"), (100, "bike_done")]),
    ("sq_catalina", [(10, "loc:catalina"), (50, ["know_ct_tribute", "know_ct_lie"]), (100, "ct_tribute_stopped")]),
    ("sq_nova", [(10, "loc:nova"), (50, ["know_nova_vre", "nova_rebels_ally"]), (100, "nova_decided")]),
    ("sq_ares", [(10, "loc:repconn"), (50, "loc:ares"), (100, "ares_decided")]),
]


class QuestMixin:
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
        if "stage_lt" in cond and self.stage(cond["stage_lt"][0]) >= cond["stage_lt"][1]:
            return False
        if "flags_any" in cond and not any(self.flags.get(f) for f in cond["flags_any"]):
            return False
        if "flags_all" in cond and not all(self.flags.get(f) for f in cond["flags_all"]):
            return False
        if "no_item" in cond and self.inventory.has(cond["no_item"]):
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
            self.flags[eff["flag"]] = True
        elif t == "clear_flag":
            self.flags.pop(eff["flag"], None)
        elif t == "give":
            self.inventory.add(eff["item"], eff["count"])
            self.log(f"Получено: {eff['item']} ×{eff['count']}")
        elif t == "take":
            self.inventory.remove(eff["item"], eff["count"])
            self.log(f"Отдано: {eff['item']} ×{eff['count']}")
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
