"""
Бейкер: три района и три пути спасения деда (docs/story.md, раздел 7).

Районы — отдельные локации (tools/build_baker.py): baker (трасса, сюда приходят с карты
мира), baker_mission (миссия «Детей Единства»), baker_outskirts (окраина и склад).

  Тень   — пробраться в миссию (калитка в дюнах, балахон послушника), добыть ключ от келий
           и увести деда без шума. Двор охраняют: чужака без пропуска и балахона
           послушник, оказавшийся рядом, замечает — и тогда это уже не Тень.
  Сделка — войти по пропуску (поручитель, пожертвование, слово Хэтти) и договориться
           с братом Ансельмом: убедить, выменять на код склада или заплатить деньгами Холлиса.
  Сталь  — штурм: с союзниками (Лира и паладины, Панк) или в одиночку.

Каким путём дед вышел из кельи, решается в момент освобождения (baker_free_amos):
культ враждебен — Сталь; была сделка — Сделка; иначе — Тень. Флаг baker_path_<путь>
дальше читают финал главы и следующий акт.

Кто ещё стоит в городе, зависит от того, с кем герой пришёл (флаги route_*) и что уже
случилось, — это расставляет baker_arrive при каждом входе в район (повторно не дублируются).
"""
from ..combat import tile_of, chebyshev
from ..balance import roll_loot

ZONES = ("baker", "baker_mission", "baker_outskirts")
MISSION = (13, 11, 58, 38)          # двор и постройки миссии (клетки, включительно)
BUNKER_SPOT = ("baker_outskirts", (67, 14))   # где дед ждёт у склада «Бейкер-7»
DEALS = ("deal_anselm", "deal_code", "deal_hollis_paid")

# кто стоит в районе: (условие-флаг, флаг «ушёл», район, id NPC, клетка)
SPAWNS = [
    ("route_lira", "lira_baker_left", "baker", "lira_baker", (22, 35)),      # Лира — у бочки за трассой
    ("route_loner", "loner_baker_left", "baker_mission", "loner_baker", (55, 4)),  # Панк — в дюнах у калитки
    ("route_silas", "silas_baker_left", "baker_mission", "silas_baker", (30, 34)),  # Сайлас — во дворе миссии
    ("gang_paid", "scar_baker_left", "baker_mission", "scar_baker", (40, 43)),  # Шрам — сторожит снаружи ворот
    ("marla_home", "marla_home_left", "baker", "marla_home", (10, 39)),     # Марла вернулась к Рою
]


class BakerMixin:
    def baker_arrive(self, loc_id):
        """Вход в район Бейкера: спутники по маршруту, дед у склада, Искра, враждебность культа."""
        f = self.flags
        for flag, gone, zone, nid, tile in SPAWNS:
            if zone == loc_id and f.get(flag) and not f.get(gone):
                self._spawn_npc(zone, nid, tile)
        zone, tile = BUNKER_SPOT
        if loc_id == zone and f.get("amos_free") and not f.get("baker_done"):
            self._spawn_npc(zone, "amos_b7", tile)
        if f.get("iskra_free") and not f.get("iskra_out_left"):
            where = ("baker_mission", (56, 5)) if f.get("route_loner") else ("baker", (36, 21))
            if where[0] == loc_id:
                self._spawn_npc(where[0], "iskra_out", where[1])
        if f.get("cult_hostile"):    # культ помнит: в любом районе балахоны нападают
            for e in self.enemies:
                if e.faction == "cult":
                    e.hostile = True
        if self.stage("mq_grandpa") < 70:
            self.set_stage("mq_grandpa", 70)

    def baker_watch(self):
        """Чужак во дворе миссии без пропуска и балахона: ближний послушник поднимает тревогу."""
        if self.loc.id != "baker_mission" or self.combat.active:
            return
        f = self.flags
        if f.get("mission_pass") or f.get("cult_hostile") or self.inventory.has("балахон послушника"):
            return
        x, y = tile_of(self.player)
        if not (MISSION[0] <= x <= MISSION[2] and MISSION[1] <= y <= MISSION[3]):
            return
        for e in self.enemies:
            if e.alive and e.faction == "cult" and chebyshev(tile_of(e), (x, y)) <= 3:
                self.speech = {"ent": e, "text": "Чужой во дворе! Братья, сюда!", "t": 2600}
                self.log("Послушник заметил вас: «Чужой во дворе!» Тихо уже не выйдет.")
                f["baker_alarm"] = True
                self.make_hostile("cult")
                self.combat.start(player_first=False)
                return

    def baker_assault(self):
        """Штурм миссии. Союзники снимают часть охраны во дворе до того, как герой входит в ворота."""
        f = self.flags
        mission = self.get_location("baker_mission")

        def in_mission(e):
            x, y = tile_of(e)
            return MISSION[0] <= x <= MISSION[2] and MISSION[1] <= y <= MISSION[3]
        cult = [e for e in mission.enemies if e.alive and e.faction == "cult" and in_mission(e)]
        allies = [name for flag, name in (("route_lira", "паладины Братства"), ("route_loner", "Панк"))
                  if f.get(flag)]
        down = cult[:len(cult) // 2 + len(allies) - 1] if allies else []
        for e in down:
            e.hp, e.alive = 0, False
            mission.level.add_corpse(e, roll_loot(e.loot))
        f["baker_assault"] = True
        f["mission_gate_open"] = True
        for e in self.enemies:     # и здесь, и в миссии культ теперь враг
            if e.faction == "cult":
                e.hostile = True
        for e in mission.enemies:
            if e.faction == "cult":
                e.hostile = True
        f["cult_hostile"] = True
        if allies:
            self.log(f"Штурм! {' и '.join(allies).capitalize()} бьют по миссии с флангов — "
                     f"охрана редеет на глазах ({len(down)} балахонов уже не встанут). Ворота открыты.")
        else:
            self.log("Вы идёте на миссию в одиночку. Ворота трещат, послушники хватаются за оружие.")
        if self.loc is mission and any(e.alive and e.faction == "cult" for e in self.enemies):
            self.combat.start(player_first=True)

    def baker_free_amos(self):
        """Дед выходит из кельи и уходит к складу. Здесь решается, каким путём он спасён."""
        f = self.flags
        f["amos_free"] = True
        if f.get("cult_hostile"):
            path = "steel"
        elif any(f.get(k) for k in DEALS):
            path = "deal"
        else:
            path = "shadow"
        f[f"baker_path_{path}"] = True
        self.loc.npcs[:] = [n for n in self.npcs if n.npc_id != "amos"]
        self.set_stage("mq_grandpa", 80)
        self.gain_xp(150)
        self.log({"shadow": "Дед выскальзывает из кельи. Никто ничего не видел — пока.",
                  "deal": "Дед выходит из кельи под взглядами послушников. Сделка есть сделка.",
                  "steel": "Дед выходит из кельи, переступая через гильзы."}[path]
                 + " Он идёт к складу «Бейкер-7» — на окраине, в дюнах на северо-востоке.")

    def marla_return(self):
        """Марла уходит из миссии к Рою."""
        self.flags["marla_home"] = True
        self.loc.npcs[:] = [n for n in self.npcs if n.npc_id != "marla"]
        self.set_stage("sq_roy", 50)
