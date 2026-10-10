"""
Голос спутника: человек в отряде замечает места и поступки — сам, облачком над головой
(data/ally_lines.json). Место — один раз за игру (ключ: id локации, город, префикс локации);
поступок (@deeds) — тоже один раз, как только условие стало верным. Если герой опустился ниже
того, что спутник готов терпеть (quit), — тот говорит, что думает, и уходит домой.
"""
import json

from .reputation import town_of

with open("data/ally_lines.json", encoding="utf-8") as _f:
    LINES = {k: v for k, v in json.load(_f).items() if not k.startswith("_")}
DELAY_MS = 1400          # заговорить не сразу у входа, а когда огляделись
GAP_MS = 12000           # между репликами спутника


class AllyVoiceMixin:
    def ally_on_enter(self):
        self.ally_voice_ms = DELAY_MS

    def _ally_line(self):
        """Что спутник скажет сейчас: (флаг «сказано», текст, уходит ли) или None."""
        a = self.ally
        lines = LINES.get(a.type_id, {})
        quit_ = lines.get("quit")
        if quit_ and self.check_condition(quit_["if"]):
            return (f"{a.type_id}_quit", quit_["text"], True)
        for i, d in enumerate(lines.get("@deeds", [])):
            key = f"ally_said_{a.type_id}_deed{i}"
            if not self.flags.get(key) and self.check_condition(d.get("if", {})):
                return (key, d["text"], False)
        lid = self.loc.id
        for k in (lid, town_of(lid)) + tuple(p for p in lines if not p.startswith("@") and lid.startswith(p)):
            if k and k in lines and isinstance(lines[k], str):
                key = f"ally_said_{a.type_id}_{k}"
                return None if self.flags.get(key) else (key, lines[k], False)
        return None

    def update_ally_voice(self, dt_ms):
        a = getattr(self, "ally", None)
        if a is None or self.mode != "local" or not self.player.alive:
            return
        self.ally_voice_ms = getattr(self, "ally_voice_ms", DELAY_MS) - dt_ms
        if self.ally_voice_ms > 0 or self.speech or self.combat.active or self.modal_open():
            return
        line = self._ally_line()
        self.ally_voice_ms = GAP_MS
        if not line:
            return
        key, text, leaving = line
        self.flags[key] = True
        self.speech = None if leaving else {"ent": a, "text": text, "t": 4200}
        self.log(f"{a.name}: {text}")
        if leaving:
            name = a.name
            self.dismiss_ally()
            self.log(f"{name} уходит. Больше не позовёшь.")
