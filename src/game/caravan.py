"""
Охранник Красного каравана (docs/city_plan.md, этап 2): Маргарет Крэйн в Хабе нанимает на рейс до Джанктауна,
Нидлса или Вегаса. Дорога — три события (data/caravan_events.json): засада, поломка, путник, контрабанда, буря…
У каждого — выбор и проверки навыков; исход меняет груз (из трёх вьюков), здоровье, карму. Плата — за довезённый
груз; рейс заодно доставляет героя в город назначения. Пять удачных рейсов — партнёр Красного каравана.

Рейс собирается в диалог «caravan_run» (тот же движок, что и разговоры): узел события — варианты, узел исхода — текст.
"""
import json
import random

with open("data/caravan_events.json", encoding="utf-8") as _f:
    EVENTS = {k: v for k, v in json.load(_f).items() if not k.startswith("_")}
ROUTES = {"junktown": ("Джанктаун", 90), "needles": ("Нидлс", 140), "vegas_strip": ("Вегас", 220)}
CARGO = 3
PARTNER_RUNS = 5


class CaravanMixin:
    def caravan_start(self, dest, events=None):
        """events — три события подряд (для тестов); иначе случайные, засада — в 70% рейсов."""
        rnd = random.Random(self.play_ms + 7919 * self.flags.get("caravan_runs", 0))
        evs = list(events) if events else rnd.sample([e for e in EVENTS if e != "ambush"], 2)
        if not events:
            evs.insert(rnd.randint(0, 2), "ambush" if rnd.random() < 0.7 else
                       rnd.choice([e for e in EVENTS if e not in evs and e != "ambush"]))
        self.caravan = {"dest": dest, "cargo": CARGO, "bonus": 0, "safe": False}
        nodes = {}
        for i, eid in enumerate(evs):
            ev = EVENTS[eid]
            opts = []
            for k, o in enumerate(ev["options"]):
                opts.append({"label": o["label"], "next": f"r{i}_{k}", "if": o.get("if", {}),
                             "effects": [{"type": "caravan_out", "ev": eid, "opt": k}]})
                nodes[f"r{i}_{k}"] = {"text": o["text"], "options": [{"label": "Дальше.", "next": f"e{i + 1}" if i < 2 else "end"}]}
            nodes[f"e{i}"] = {"text": f"Рейс в {ROUTES[dest][0]} — {['первый', 'второй', 'третий'][i]} день.\n\n" + ev["text"],
                              "options": opts, "event": eid}
        nodes["end"] = {"text": f"{ROUTES[dest][0]} на горизонте. Возница снимает шляпу и вытирает лоб.",
                        "options": [{"label": "Сдать груз.", "next": None, "effects": [{"type": "caravan_end"}]}]}
        self.dialogue.trees["caravan_run"] = {"start": "e0", "nodes": nodes}
        self.dialogue.start("caravan_run")
        from types import SimpleNamespace
        self.dialogue_speaker = SimpleNamespace(name="Красный караван", anim=None)
        self.log(f"Красный караван уходит из Хаба в {ROUTES[dest][0]}. Вы — охрана.")

    def caravan_skip_safe(self):
        """Путник предупредил о засаде — её не будет: узел засады подменяется спокойной дорогой."""
        tree = self.dialogue.trees["caravan_run"]["nodes"]
        for nid, n in tree.items():
            if n.get("event") == "ambush":
                i = int(nid[1:])
                n["text"] = n["text"].split("\n\n")[0] + ("\n\nПеревал. Путник был прав: на тропе — свежие следы "
                                                          "засады, но караван уже идёт руслом. Тихо.")
                n["options"] = [{"label": "Дальше.", "next": f"e{i + 1}" if i < 2 else "end"}]
                n["event"] = "ambush_avoided"

    def caravan_out(self, eid, k):
        c = self.caravan
        o = EVENTS[eid]["options"][k]
        if o.get("cost"):
            self.inventory.remove("крышки", o["cost"])
        for it in o.get("cost_items", []):
            self.inventory.remove(it, 1)
        out = o.get("out", {})
        c["cargo"] = max(0, c["cargo"] + out.get("cargo", 0))
        c["bonus"] += out.get("bonus", 0)
        if out.get("hp"):
            self.player.hp = max(1, self.player.hp + out["hp"])
        if out.get("caps"):
            self.inventory.add("крышки", out["caps"])
        if out.get("karma"):
            self.add_karma(out["karma"])
        if out.get("xp"):
            self.apply_effect({"type": "xp", "amount": out["xp"]})
        if out.get("flag"):
            self.flags[out["flag"]] = True
        if out.get("safe"):
            self.caravan_skip_safe()

    def caravan_end(self):
        c, self.caravan = self.caravan, None
        name, base = ROUTES[c["dest"]]
        pay = base * c["cargo"] // CARGO + c["bonus"]
        self.inventory.add("крышки", pay)
        if c["cargo"] == CARGO:
            self.flags["caravan_runs"] = self.flags.get("caravan_runs", 0) + 1
        self.flags["caravan_any_run"] = True
        self.log(f"Груз сдан: {c['cargo']} из {CARGO} вьюков. Плата — {pay} крышек."
                 + (" Крэйн отметит чистый рейс." if c["cargo"] == CARGO else ""))
        if self.flags.get("caravan_runs", 0) >= PARTNER_RUNS and not self.flags.get("caravan_partner"):
            self.flags["caravan_partner"] = True
            self.inventory.add("крышки", 500)
            self.log("Пять чистых рейсов! Маргарет Крэйн делает вас партнёром Красного каравана: доля — 500 крышек.")
        if c["dest"] not in self.worldmap.known:
            self.reveal_location(c["dest"])
        self.dialogue.close()
        self.enter_location(c["dest"])
