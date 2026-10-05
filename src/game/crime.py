"""
Нападение на мирных и реакция города — как в Fallout: напал на жителя при всех —
и город берётся за оружие.

  - Напасть можно на любого жителя: Shift + клик (или Shift + E рядом).
  - Житель становится врагом. Бойцы города (шериф, помощник, бармен с обрезом,
    агент Анклава…) — тоже: они стреляют, остальные жители разбегаются и с убийцей
    больше не разговаривают.
  - В миссии культа все мирные — свои для культа: нападение на послушника или
    Ансельма поднимает весь культ.
  - Город помнит (флаг town_hostile_<локация>): при следующем приходе и после загрузки
    бойцы снова враждебны. Убитые остаются мёртвыми (флаг killed_<id>).
  - На шум боя сбегаются все враждебные этой фракции в пределах слышимости
    (src/combat.py, HEARING — 20 клеток) — даже из-за угла.
"""
from ..entities import Enemy
from ..location import npc_animations, NPC_NAMES

# кто в каком городе отстреливается (остальные — мирные, разбегаются)
STATS = {
    "civilian": {"hp": 15, "damage": 3, "ac": 6, "ap": 7, "skill": 40, "sequence": 4, "ai": "melee",
                 "hit_verb": "бьёт вас", "coward": True, "level": 1, "xp": 5},
    "guard": {"hp": 32, "damage": 7, "ac": 12, "ap": 8, "skill": 60, "sequence": 6, "ai": "ranged", "range": 7,
              "hit_verb": "стреляет в вас", "level": 4, "xp": 40},
    "brawler": {"hp": 30, "damage": 10, "ac": 10, "ap": 7, "skill": 60, "sequence": 5, "ai": "ranged", "range": 4,
                "hit_verb": "палит в вас из обреза", "level": 4, "xp": 40},
    "elite": {"hp": 55, "damage": 11, "ac": 16, "ap": 9, "skill": 75, "sequence": 8, "ai": "ranged", "range": 9,
              "hit_verb": "стреляет в вас", "armor": 3, "level": 7, "xp": 120},
    "cultist": {"hp": 18, "damage": 4, "ac": 8, "ap": 8, "skill": 45, "sequence": 6, "ai": "melee",
                "hit_verb": "бьёт вас посохом", "level": 2, "xp": 15},
}
ROLES = {
    # Пятнадцатая
    "sheriff": "guard", "dale": "guard", "dex": "elite", "blondie": "elite", "mo": "brawler", "rose": "guard",
    # Бейкер
    "nick": "brawler", "hollis": "elite", "lira_baker": "elite", "scar_baker": "guard", "loner_baker": "guard",
    "anselm": "cultist", "acolyte_a": "cultist", "acolyte_b": "cultist", "silas_baker": "cultist",
    "tobias": "cultist", "iskra": "cultist", "marla": "cultist",
    # Джанктаун
    "gate_guard": "guard", "jt_guard": "guard", "hall_guard": "guard", "gizmo_thug": "brawler",
    "hunter_rourke": "elite", "cult_recruiter": "cultist",
    # Некрополь
    "nc_guard": "guard", "nc_guard_b": "guard", "nc_hall_guard": "guard", "nc_hall_guard_b": "guard",
    "set": "elite", "cobbs": "elite", "cult_envoy": "cultist", "zeke": "brawler",
    # лагерь Арадеша и Ханы
    "aradesh": "guard", "khan_chief": "elite", "khan_a": "brawler", "khan_b": "brawler", "unity_sister": "cultist",
    # Боунъярд
    "adytum_guard": "guard", "adytum_guard_b": "guard", "blade_nika": "elite", "blade_a": "brawler", "blade_b": "brawler",
    "morpheus": "cultist", "cult_foreman": "cultist", "cooper": "elite",
    # Убежище 15
    "jackal_boss": "elite", "jackal_a": "brawler", "jackal_b": "brawler", "jackal_c": "brawler", "v15_sentry": "guard",
}
CULT_ZONES = {"baker_mission"}
SPARE = {"dog", "robot", "amos", "amos_b7"}     # их не трогает и не превращает: пёс, робот, дед в келье


def faction_of(loc_id):
    return "cult" if loc_id in CULT_ZONES else f"town_{loc_id}"


class CrimeMixin:
    def _npc_to_enemy(self, npc, faction):
        role = ROLES.get(npc.npc_id, "civilian")
        d = {"name": NPC_NAMES.get(npc.npc_id, npc.name), "faction": faction, "hitbox": [28, 32], **STATS[role]}
        e = Enemy(npc.rect.topleft, npc_animations(npc.npc_id), "npc:" + npc.npc_id, d)
        e.rect = npc.rect.copy()
        e.npc_id = npc.npc_id
        e.hostile = True
        e.wander_wait = 10 ** 9
        self.loc.npcs[:] = [n for n in self.npcs if n is not npc]
        self.loc.enemies.append(e)
        return e

    def town_turns_hostile(self, victim=None):
        """Весь город (или культ в миссии) — против героя. victim — на кого напали."""
        loc_id = self.loc.id
        fac = faction_of(loc_id)
        self.flags[f"town_hostile_{loc_id}"] = True
        target = None
        if victim is not None:
            target = self._npc_to_enemy(victim, fac)
        for n in list(self.npcs):
            if n.npc_id in SPARE:
                continue
            if fac == "cult" or ROLES.get(n.npc_id, "civilian") != "civilian":
                self._npc_to_enemy(n, fac)
        if fac == "cult":
            self.make_hostile("cult")
        else:
            self.make_hostile(fac)
        return target

    def attack_npc(self, npc):
        """Shift + клик по жителю: напасть. Город это видит."""
        if npc.npc_id in SPARE or self.merc_mode:
            self.log("Рука не поднимается.")
            return
        name = NPC_NAMES.get(npc.npc_id, npc.name)
        target = self.town_turns_hostile(npc)
        self.log(f"Вы нападаете на: {name}. Крики: «Убивают!» — город берётся за оружие.")
        self.combat.start(player_first=True)
        if self.combat.active and target in self.combat.order:
            self.combat.target = target

    def restore_town_hostility(self):
        """Вход в локацию / загрузка: город помнит нападение — бойцы враждебны, убитые мертвы."""
        self.loc.npcs[:] = [n for n in self.npcs if not self.flags.get(f"killed_{n.npc_id}")]
        if self.flags.get(f"town_hostile_{self.loc.id}"):
            self.town_turns_hostile()

    def scared_line(self, npc):
        """Мирный житель после нападения на город — не разговаривает."""
        if self.flags.get(f"town_hostile_{self.loc.id}") and npc.npc_id not in SPARE:
            self.speech = {"ent": npc, "text": "Не подходи! Убийца!", "t": 2200}
            return True
        return False
