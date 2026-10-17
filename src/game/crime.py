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
    # бойцы города — не мишени: в Fallout напасть на город означало смерть. У каждого броня, настоящее оружие
    # и своя роль в бою (src/ai_roles.py): страж стреляет из-за укрытия, громила заходит с флангов с обрезом,
    # старший командует и бьёт очередями. Броня гасит слабые стволы, уязвимы глаза; на шум сбегается стража
    "guard": {"hp": 70, "damage": 11, "ac": 14, "ap": 9, "skill": 75, "sequence": 7, "ai": "ranged", "range": 8,
              "hit_verb": "стреляет в вас", "armor": 4, "weak_parts": ["eyes", "groin"], "role": "cover",
              "stims": 1, "level": 5, "xp": 40,
              "loot": {"патроны": 8, "10-мм пистолет": 0.5, "металлическая броня": 0.25}},
    "brawler": {"hp": 65, "damage": 15, "ac": 12, "ap": 8, "skill": 70, "sequence": 6, "ai": "ranged", "range": 5,
                "hit_verb": "палит в вас из обреза", "armor": 3, "weak_parts": ["eyes", "head"], "role": "flanker",
                "level": 5, "xp": 40, "loot": {"патроны": 6, "обрез": 0.6, "кожаная броня": 0.4}},
    "elite": {"hp": 120, "damage": 9, "ac": 18, "ap": 10, "skill": 85, "sequence": 9, "ai": "ranged", "range": 9,
              "hit_verb": "бьёт очередью", "burst": 3, "armor": 7, "weak_parts": ["eyes"], "role": "commander",
              "grenades": 2, "stims": 2, "level": 8, "xp": 120,
              "loot": {"патроны": 12, "граната": 1, "стимулятор": 1, "пистолет-пулемёт": 0.5, "боевая броня": 0.3}},
    "cultist": {"hp": 32, "damage": 6, "ac": 10, "ap": 8, "skill": 55, "sequence": 6, "ai": "melee",
                "hit_verb": "бьёт вас посохом", "armor": 1, "level": 3, "xp": 15},
}
POSSE_EVERY = 3        # раундов боя между волнами подкрепления
POSSE_SIZE = 2


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
    # Примм
    "deputy_baxter": "guard", "pr_deputy": "guard", "pr_caravan_guard": "guard", "brother_job": "cultist",
    "cult_guard_pr": "cultist", "cult_guard_pr_b": "cultist", "cult_sister_pr": "cultist",
    # Гудспрингс
    "sunny": "elite", "mayor_pettit": "guard", "cult_hunter": "cultist", "ezekiel": "brawler",
    # Убежище 22
    "hugo_lee": "elite",
    # Ниптон
    "groom_cal": "elite", "groom_a": "brawler", "groom_b": "brawler", "groom_c": "brawler", "brother_t": "cultist",
    "cult_guard_np": "cultist", "cult_guard_np_b": "cultist",
    # Сёрчлайт и Форт
    "robo_sgt": "elite", "robo_sentry": "elite", "paladin_ross": "elite", "bos_knight": "guard", "fire_chief_hope": "guard",
    # руины Вегаса
    "hank_spur": "elite", "boots_rider": "brawler", "boots_rider_b": "brawler", "boots_rider_c": "brawler",
    "snake_guard": "guard", "mother_snake": "guard", "palms_doorman": "guard", "palms_cook": "brawler", "cooper_zero": "elite",
    # «Посейдон-7»
    "enclave_gate": "elite", "enclave_officer": "elite", "hollis_p7": "elite", "enclave_tech": "guard",
    "enclave_trooper": "elite", "enclave_scientist": "civilian",
    # Марипоза
    "brother_t_mp": "elite", "cult_herald": "cultist", "mp_acolyte": "cultist", "mp_acolyte_b": "cultist",
    # остров Санта-Каталина
    "harbor_master": "guard", "sailor_finn": "brawler",
    # «Нова»
    "sphinx": "elite", "radio_bot": "elite", "harold": "civilian", "marta_subject": "civilian", "marta_home": "civilian", "billy": "guard", "caravan_lars": "civilian", "deputy_abby": "guard", "luis_cards": "civilian",
    "beth_waitress": "civilian", "hank_miner": "civilian",
    "purity_officer": "guard", "purity_bot": "elite", "raven_hacker": "elite", "nv_dealer": "brawler", "councillor_vale": "civilian",
}
CULT_ZONES = {"baker_mission", "primm_camp", "nipton_mine", "mariposa", "mariposa_lab", "mariposa_vats"}
SPARE = {"dog", "robot", "amos", "amos_b7", "tobi", "np_captive", "darnell", "tobi_mp", "ezekiel_mp", "nipton_bride_mp", "rover_bot"}     # их не трогает и не превращает: пёс, робот, дед в келье


ENCLAVE_ZONES = {"poseidon7", "poseidon7_base", "poseidon7_hangar"}   # одна тревога на всю станцию


def faction_of(loc_id):
    if loc_id in ENCLAVE_ZONES:
        return "enclave"
    return "cult" if loc_id in CULT_ZONES else f"town_{loc_id}"


class CrimeMixin:
    def _hardened(self, d, role):
        """Город не слабеет с ростом героя: бойцы крепчают вместе с ним (мирных это не касается)."""
        if role == "civilian":
            return d
        k = max(0, self.player.level_sys.level - 1)
        d["hp"] = round(d["hp"] * (1 + 0.08 * k))
        d["damage"] += k // 2
        d["skill"] = min(95, d["skill"] + 2 * k)
        d["level"] += k
        return d

    def _npc_to_enemy(self, npc, faction):
        role = ROLES.get(npc.npc_id, "civilian")
        d = self._hardened({"name": NPC_NAMES.get(npc.npc_id, npc.name), "faction": faction, "hitbox": [28, 32],
                            **STATS[role]}, role)
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
            if n.npc_id in SPARE or n.npc_id.startswith("amb_critter_"):
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
        if npc.npc_id in SPARE or npc.npc_id.startswith("amb_critter_") or self.merc_mode:
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
        from ..location import NPC_IF
        self.loc.npcs[:] = [n for n in self.npcs if not self.flags.get(f"killed_{n.npc_id}")
                            and not self.flags.get(f"{n.npc_id}_left")      # ушёл (с героем или навсегда)
                            and self.check_condition(NPC_IF.get(n.npc_id, {}))]
        # кто по условию появляется позже (охотник приехал за должником) — возвращается из полного списка карты
        here = {n.npc_id for n in self.npcs} | {getattr(e, "npc_id", None) for e in self.enemies}
        ally = getattr(getattr(self, "ally", None), "type_id", None)
        for n in getattr(self.loc, "npcs_all", []):
            if (n.npc_id in NPC_IF and n.npc_id not in here and n.npc_id != ally
                    and not self.flags.get(f"killed_{n.npc_id}") and not self.flags.get(f"{n.npc_id}_left")
                    and self.check_condition(NPC_IF[n.npc_id])):
                self.loc.npcs.append(n)
        if self.flags.get(f"town_hostile_{self.loc.id}") or \
                (self.loc.id in ENCLAVE_ZONES and self.flags.get("enclave_hostile")):
            self.town_turns_hostile()
            self.crime_sentries()

    def scared_line(self, npc):
        """Мирный житель после нападения на город — не разговаривает."""
        if self.flags.get(f"town_hostile_{self.loc.id}") and npc.npc_id not in SPARE:
            self.speech = {"ent": npc, "text": "Не подходи! Убийца!", "t": 2200}
            return True
        return False

    # ------------------------------------------------------------------ подкрепление
    def _posse_sprite(self):
        """Чей облик у подкрепления: у кого-то из бойцов этого города (остальные берутся из набора врагов)."""
        for n in list(getattr(self.loc, "npcs_all", [])) + list(self.npcs):
            if ROLES.get(n.npc_id, "civilian") in ("guard", "brawler"):
                return npc_animations(n.npc_id), n.npc_id
        return None, None

    def _spawn_posse(self, n, near, lo, hi, elite=False):
        """n бойцов города встают на свободных клетках в lo..hi клетках от near и сразу вступают в бой."""
        import random
        from ..combat import tile_of, rect_pos_for_tile, chebyshev
        fac = faction_of(self.loc.id)
        anims, sprite = self._posse_sprite()
        c = self.combat
        px, py = tile_of(self.player)
        spots = [(x, y) for x in range(px - hi, px + hi + 1) for y in range(py - hi, py + hi + 1)
                 if lo <= chebyshev((x, y), near) <= hi and c._walkable((x, y))]
        random.shuffle(spots)
        made = 0
        for t in spots:
            if made >= n:
                break
            if t in c._occupied():
                continue
            role = "cultist" if fac == "cult" else "elite" if elite else ("guard" if made % 2 == 0 else "brawler")
            name = {"cult": "фанатик Единства", "enclave": "солдат Анклава"}.get(fac, "боец городской стражи")
            d = self._hardened({"name": name, "faction": fac, "hitbox": [28, 32], **STATS[role]}, role)
            e = Enemy(rect_pos_for_tile(self.player, t), anims or _enemy_anims("raider_elite"),
                      "npc:" + sprite if sprite else "raider_elite", d)
            e.hostile = True
            e.wander_wait = 10 ** 9
            self.loc.enemies.append(e)
            made += 1
        return made

    def crime_reinforce(self, round_no):
        """Вызывается боем в начале каждого раунда: в городе, где напали, к бойцам стягивается стража.
        Чем дольше бой, тем больше врагов, а на третьей волне приходят лучшие бойцы — расправа или бегство."""
        loc = self.loc.id
        if not self.flags.get(f"town_hostile_{loc}") or round_no < POSSE_EVERY or round_no % POSSE_EVERY:
            return
        from ..combat import tile_of
        wave = round_no // POSSE_EVERY
        made = self._spawn_posse(POSSE_SIZE, tile_of(self.player), 9, 14, elite=wave >= 3 and wave % 2 == 1)
        if made:
            self.log("С улиц сбегается городская стража!")

    def crime_sentries(self):
        """Вход в город, где вас помнят: у ворот уже ждут (не больше трёх бойцов на карте)."""
        from ..combat import tile_of
        fac = faction_of(self.loc.id)
        alive = [e for e in self.enemies if e.alive and e.faction == fac]
        if len(alive) < 3:
            self._spawn_posse(3 - len(alive), tile_of(self.player), 5, 9)


def _enemy_anims(type_id):
    from ..location import enemy_animations
    return enemy_animations(type_id)
