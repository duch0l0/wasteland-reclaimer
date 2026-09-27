"""Условия и эффекты из диалогов (data/dialogues.json), флаги квестов, фракции."""


class QuestMixin:
    def check_condition(self, cond):
        """Условие реплики/стартового узла: flag, not_flag, item+count, perk, min_level."""
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
