"""
Карманы, как в Fallout 2: K рядом с жителем — окно обыска его карманов (то же, что у ящика).
Взять — кража, положить — подбросить. Каждая вещь — свой бросок навыка «Ловкость рук».

Кража — не замена квестам: дело для того, кто вложился в навык, и всегда риск.

  шанс = Ловкость рук − 25 (сложно само по себе)
         ± 15 (за спиной жителя / лицом к лицу)
         − цена вещи / 6 (до 45; крышки — горсть/3, до 30)
         − 35, если вещь сюжетная (ключ, код, бумага — её стерегут: data/pockets.json, "_guarded")
         − 25 за каждого свидетеля рядом (до 50)
         − 20 за каждую уже стащенную у него вещь (карман «полегчал» — он насторожился)
         − 25, если в этом городе героя уже ловили за руку;
         подбросить на 10% легче; 3…85% (сюжетное — не выше 60%).
  Новичок (20) почти всегда попадается; мастер (90) тащит сюжетный ключ со спины примерно через раз.
  поймали — «Эй! Руки! Вор!»: окно закрывается, карма и репутация города вниз, торговец больше не торгует,
         к жертве больше не подобраться, весь город настороже; поймал стражник или боец, или он был рядом —
         город берётся за оружие (src/game/crime.py).
  динамит (или граната) в чужом кармане — взрыв через несколько секунд: житель погибает, свидетели не нужны.
  улика в чужом кармане — PLANT_HOOKS: подставить человека (квест это заметит).

Содержимое карманов — data/pockets.json (сюжетные: ключи, коды, бумаги); у остальных — горсть крышек и мелочь,
одна и та же при каждом запуске (зерно — id жителя). Что осталось в карманах — во флагах pocket_<id>.
"""
import json
import random

import pygame

from .. import items
from ..combat import tile_of, chebyshev
from .reputation import town_of

with open("data/pockets.json", encoding="utf-8") as _f:
    _P = json.load(_f)
POCKETS = {k: v for k, v in _P.items() if not k.startswith("_")}
GUARDED = set(_P.get("_guarded", []))      # сюжетные вещи: их держат при себе и проверяют

# подбросил (житель, предмет) → эффекты
PLANT_HOOKS = {
    ("luis_cards", "фартук в крови"): [{"type": "set_flag", "flag": "murder_framed_luis"}],
    ("decker", "листовка Единства"): [{"type": "set_flag", "flag": "decker_framed_cult"}],
    # заказ Гизмо: фляга с ядом вместо мэрской — мэр пьёт свой мятный чай
    ("mayor_darkwater", "фляга с ядом"): [
        {"type": "log", "text": "Мэр машинально хлопает по карману, достаёт флягу, делает глоток мятного чая... "
                                "и садится. Медленно. Как будто очень устал. Больше он не встаёт."},
        {"type": "set_flag", "flag": "mayor_poisoned"}, {"type": "set_flag", "flag": "killed_mayor_darkwater"},
        {"type": "npc_leave", "npc": "mayor_darkwater"}, {"type": "karma", "amount": -60},
        {"type": "quest", "id": "sq_gizmo", "stage": 50}],
}
BOMB_MS = 3500
SMALL = ["сигареты", "спички", "бинт", "консервы", "энергетический батончик", "изолента", "пружина", "батарейки"]


class PickpocketMixin:
    # ------------------------------------------------------------ карманы
    def pocket(self, npc_id):
        key = f"pocket_{npc_id}"
        if key not in self.flags:
            if npc_id in POCKETS:
                self.flags[key] = dict(POCKETS[npc_id])
            else:
                rnd = random.Random(sum(ord(c) * (i + 3) for i, c in enumerate(npc_id)))
                p = {"крышки": rnd.randint(2, 18)}
                if rnd.random() < 0.6:
                    p[rnd.choice(SMALL)] = 1
                self.flags[key] = p
        return self.flags[key]

    def steal_chance(self, npc, name, plant=False):
        p = self.player
        skill = p.skill("steal")
        behind = 15 if npc.rect.centery > p.rect.centery else -15   # житель смотрит «вниз» — подкрасться сверху
        pile = self.loot["box"]["loot"].get(name, 1) if self.loot else 1
        price = min(30, pile // 3) if name == "крышки" else min(45, items.price(name) // 6)
        guarded = name in GUARDED and not plant
        witnesses = [n for n in self.npcs if n is not npc and chebyshev(tile_of(n), tile_of(npc)) <= 5
                     and self.combat.los(n, p)]
        heat = self.flags.get(f"pocket_heat_{npc.npc_id}", 0)
        town = town_of(self.loc.id)
        wary = 25 if self.flags.get(f"wary_{town or self.loc.id}") else 0
        chance = (skill - 25 + behind - price - (35 if guarded else 0) - min(50, 25 * len(witnesses))
                  - 20 * heat - wary + (10 if plant else 0))
        return max(3, min(60 if guarded else 85, chance))

    def pickpocket(self, target=None):
        """K: карманы жителя рядом (или того, кого выбрали в меню ПКМ)."""
        if self.combat.active:
            self.log("Обчищать карманы посреди боя? Смело. Но нет.")
            return
        reach = self.player.rect.inflate(60, 60)
        npc = next((n for n in self.npcs if reach.colliderect(n.rect) and (target is None or n is target)), None)
        if npc is None:
            self.log("Рядом нет никого, у кого есть карманы.")
            return
        if self.flags.get(f"{npc.npc_id}_robbed"):
            self.log(f"{npc.name} держит руку на кармане и не сводит с вас глаз.")
            return
        box = {"name": f"карманы: {npc.name}", "loot": self.pocket(npc.npc_id), "opened": True, "pocket": npc,
               "tiles": [tile_of(npc)], "owner": None}
        self.loot = {"box": box, "side": "box", "sel": 0, "stolen_checked": True}
        self.log(f"Вы осторожно запускаете руку в карман: {npc.name}. (Ловкость рук: {self.player.skill('steal')})")

    def pocket_roll(self, npc, name, plant=False):
        """True — не заметили. Иначе — поймали: последствия."""
        chance = self.steal_chance(npc, name, plant)
        if random.randint(1, 100) <= chance:
            if not plant:
                key = f"pocket_heat_{npc.npc_id}"
                self.flags[key] = self.flags.get(key, 0) + 1
            return True
        self.caught_stealing(npc)
        return False

    def caught_stealing(self, npc):
        from .crime import ROLES
        self.loot = None
        self.speech = {"ent": npc, "text": "Эй! Руки! Вор!", "t": 2600}
        self.log(f"{npc.name} хватает вас за руку: «Вор!»")
        self.flags[f"{npc.npc_id}_robbed"] = True
        self.flags["caught_stealing"] = self.flags.get("caught_stealing", 0) + 1
        self.flags[f"wary_{town_of(self.loc.id) or self.loc.id}"] = True
        self.on_theft_seen()
        fighters = ("guard", "elite", "brawler")
        guard_near = any(ROLES.get(n.npc_id) in fighters and chebyshev(tile_of(n), tile_of(npc)) <= 8
                         for n in self.npcs)
        if guard_near:
            self.log("На крик оборачивается охрана. Город берётся за оружие.")
            self.town_turns_hostile(npc)
            self.combat.start(player_first=False)

    # ------------------------------------------------------------ подбросить
    def pocket_planted(self, npc, name):
        if name in ("динамит", "граната"):
            self.bombs.append({"npc": npc, "ms": BOMB_MS, "kind": name})
            self.log(f"Вы аккуратно опускаете в карман: {name}. Фитиль тлеет. Лучше отойти.")
            self.flags["planted_bomb"] = True
            return
        for eff in PLANT_HOOKS.get((npc.npc_id, name), []):
            self.apply_effect(eff)
        self.flags[f"planted_{npc.npc_id}"] = True
        self.log(f"Подброшено: {name} — в карман: {npc.name}.")

    def update_bombs(self, dt_ms):
        if not getattr(self, "bombs", None):
            return
        for b in list(self.bombs):
            b["ms"] -= dt_ms
            if b["ms"] > 0:
                continue
            self.bombs.remove(b)
            npc = b["npc"]
            if npc not in self.npcs:
                continue
            tile = tile_of(npc)
            self.combat.explode(tile, "barrel" if b["kind"] == "динамит" else "grenade")
            self.npcs.remove(npc)
            self.flags[f"killed_{npc.npc_id}"] = True
            self.flags[f"{npc.npc_id}_left"] = True
            self.log(f"{npc.name} больше нет. Свидетелей — тоже.")
            self.on_npc_killed(npc.npc_id)
            if pygame.Vector2(npc.rect.center).distance_to(self.player.rect.center) < 5 * 48:
                self.on_theft_seen()      # взорвал на глазах у всех
