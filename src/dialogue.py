"""
Диалоговые деревья NPC (data/dialogues.json).

Формат:
  "start": [{"if": {...}, "node": "id"}, ..., {"node": "id"}]  — первый подходящий
  "nodes": {"id": {"text": "...", "options": [
      {"label": "...", "next": "id" | null, "if": {...}, "effects": [{...}, ...]}
  ]}}

Условия ("if") проверяет игра (Game.check_condition): flag, not_flag,
item + count, caps, perk, min_level. Эффекты ("effects") исполняет игра
(Game.apply_effect). Варианты с невыполненным условием не показываются —
как в Fallout: реплику [Красноречие] видно, только если навык есть.
"""
import json

# условия, которые помечаются тегом перед репликой
CHECK_TAGS = {"silver_tongue": "[Красноречие]"}


class DialogueRunner:
    def __init__(self, dialogues_path, check_fn):
        with open(dialogues_path, "r", encoding="utf-8") as f:
            self.trees = json.load(f)
        self.check = check_fn
        self.active_id = None
        self.active_node = None

    def is_active(self):
        return self.active_node is not None

    def start(self, tree_id):
        tree = self.trees.get(tree_id)
        if not tree:
            return None
        start = tree["start"]
        if isinstance(start, str):
            start = [{"node": start}]
        for entry in start:
            if self.check(entry.get("if", {})):
                self.active_id = tree_id
                self.active_node = entry["node"]
                return self.current_node()
        return None

    def current_node(self):
        if not self.is_active():
            return None
        return self.trees[self.active_id]["nodes"][self.active_node]

    def visible_options(self):
        node = self.current_node()
        if not node:
            return []
        return [o for o in node.get("options", []) if self.check(o.get("if", {}))]

    @staticmethod
    def option_label(opt):
        cond = opt.get("if", {})
        tag = CHECK_TAGS.get(cond.get("perk"), "")
        if not tag and "skill" in cond:
            from .skills import SKILL_BY_ID
            tag = f"[{SKILL_BY_ID[cond['skill'][0]]['name']} {cond['skill'][1]}]"
        if not tag and "min_level" in cond:
            tag = f"[Уровень {cond['min_level']}+]"
        return f"{tag} {opt['label']}" if tag else opt["label"]

    def choose(self, option_index):
        """Возвращает список эффектов выбранной реплики (их применяет игра)."""
        options = self.visible_options()
        if not (0 <= option_index < len(options)):
            return []
        opt = options[option_index]
        nxt = opt.get("next")
        if nxt:
            self.active_node = nxt
        else:
            self.close()
        return opt.get("effects", [])

    def close(self):
        self.active_id = None
        self.active_node = None
