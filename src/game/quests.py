"""Условия и эффекты из диалогов и терминалов, стадии квестов (data/quests.json), фракции."""
import json

with open("data/quests.json", "r", encoding="utf-8") as f:
    QUESTS = {k: v for k, v in json.load(f).items() if not k.startswith("_")}


class QuestMixin:
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
        else:
            self.log(f"{'Новое задание' if first else 'Журнал обновлён'}: «{q['title']}» (J — журнал).")
        self.journal_sel = quest_id

    def check_condition(self, cond):
        """Условие реплики/стартового узла: flag, not_flag, flags_any, item+count, no_item, perk,
        min_level, stage [квест, не меньше], stage_lt [квест, меньше]."""
        if "stage" in cond and self.stage(cond["stage"][0]) < cond["stage"][1]:
            return False
        if "stage_lt" in cond and self.stage(cond["stage_lt"][0]) >= cond["stage_lt"][1]:
            return False
        if "flags_any" in cond and not any(self.flags.get(f) for f in cond["flags_any"]):
            return False
        if "no_item" in cond and self.inventory.has(cond["no_item"]):
            return False
        if "flag" in cond and not self.flags.get(cond["flag"]):
            return False
        if "not_flag" in cond and self.flags.get(cond["not_flag"]):
            return False
        if "item" in cond and not self.inventory.has(cond["item"], cond.get("count", 1)):
            return False
        if "perk" in cond and not self.player.perk_rank(cond["perk"]):
            return False
        if "min_level" in cond and self.player.level_sys.level < cond["min_level"]:
            return False
        return True

    def apply_effect(self, eff):
        if not self.check_condition(eff.get("if", {})):  # у эффекта может быть своё условие
            return
        self._apply_effect(eff)
        self.sync_story()

    def sync_story(self):
        """Одни и те же факты можно узнать разными путями — здесь они сводятся в стадии квестов."""
        f, st = self.flags, self.stage
        if self.inventory.has("чей-то глаз") and 0 < st("mq_grandpa") < 20:
            self.set_stage("mq_grandpa", 20)
        if f.get("know_baker") and 40 <= st("mq_grandpa") < 50:
            self.set_stage("mq_grandpa", 50)
        if st("mq_grandpa") >= 50 and "baker" not in self.worldmap.known:
            self.reveal_location("baker")
        if any(f.get(k) for k in ("route_caravan", "route_lira", "route_loner")):
            f["route_any"] = True
            self.set_stage("mq_grandpa", 60)
        if any(f.get(k) for k in ("gang_dead", "gang_left", "gang_paid")) and 0 < st("sq_gang") < 50:
            self.set_stage("sq_gang", 50)
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
            self.log(f"+{eff['amount']} опыта.")
            self.gain_xp(eff["amount"])
        elif t == "trade":
            self.open_trade("gena")
        elif t == "reveal":
            self.reveal_location(eff["location"])
        elif t == "fight":
            speaker = self.dialogue_speaker
            if speaker is not None and getattr(speaker, "faction", None):
                self.make_hostile(speaker.faction)
            self.combat.start(player_first=False)
        elif t == "quest":
            self.set_stage(eff["id"], eff["stage"])
        elif t == "read":
            self.open_document(eff["doc"])
        elif t == "slides":
            self.show_slides(eff["id"])
        elif t == "npc_leave":
            self.loc.npcs[:] = [n for n in self.npcs if n.npc_id != eff["npc"]]
            self.flags[f"{eff['npc']}_left"] = True
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
