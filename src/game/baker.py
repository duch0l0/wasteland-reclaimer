"""
Бейкер: три пути спасения деда (docs/story.md, раздел 7).

  Тень   — пробраться в миссию (калитка в дюнах, балахон послушника), добыть ключ от келий
           и увести деда без шума. Двор охраняют: чужака без пропуска и балахона
           послушник, оказавшийся рядом, замечает — и тогда это уже не Тень.
  Сделка — войти по пропуску (поручитель, пожертвование, слово Хэтти) и договориться
           с братом Ансельмом: убедить, выменять на код склада или заплатить деньгами Холлиса.
  Сталь  — штурм: с союзниками (Лира и паладины, Панк) или в одиночку.

Каким путём дед вышел из кельи, решается в момент освобождения (baker_free_amos):
культ враждебен — Сталь; была сделка — Сделка; иначе — Тень. Флаг baker_path_<путь>
дальше читают финал главы и следующий акт.

Кто ещё стоит в городе, зависит от того, с кем герой пришёл (флаги route_*) —
их ставит baker_arrive при каждом входе (повторно не дублируются).
"""
from ..combat import tile_of, chebyshev

MISSION = (27, 8, 56, 23)          # двор и постройки миссии (клетки, включительно)
BUNKER_SPOT = (73, 17)             # где дед ждёт у склада «Бейкер-7»
DEALS = ("deal_anselm", "deal_code", "deal_hollis_paid")

# кто приходит в Бейкер вместе с героем: флаг -> (id NPC, клетка)
COMPANIONS = [
    ("route_lira", "lira_baker", (28, 34)),     # Лира — с отрядом Братства в дюнах к югу
    ("route_loner", "loner_baker", (48, 3)),    # Панк — у задней калитки миссии
    ("route_silas", "silas_baker", (34, 21)),   # брат Сайлас — во дворе миссии
    ("gang_paid", "scar_baker", (44, 27)),      # Шрам — нанялся к культу сторожем
]


class BakerMixin:
    def baker_arrive(self):
        """Вход в Бейкер: спутники по маршруту, дед у склада, стадия квеста."""
        f = self.flags
        for flag, nid, tile in COMPANIONS:
            if f.get(flag) and not f.get(f"{nid}_left"):
                self._spawn_npc("baker", nid, tile)
        if f.get("amos_free") and not f.get("baker_done"):
            self._spawn_npc("baker", "amos_b7", BUNKER_SPOT)
        if f.get("iskra_free") and not f.get("iskra_out_left"):
            self._spawn_npc("baker", "iskra_out", (49, 3) if f.get("route_loner") else (36, 33))
        if self.stage("mq_grandpa") < 70:
            self.set_stage("mq_grandpa", 70)

    def baker_watch(self):
        """Чужак во дворе миссии без пропуска и балахона: ближний послушник поднимает тревогу."""
        if self.loc.id != "baker" or self.combat.active:
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
        """Штурм миссии. Союзники снимают часть охраны до того, как герой входит в ворота."""
        f = self.flags
        def in_mission(e):
            x, y = tile_of(e)
            return MISSION[0] <= x <= MISSION[2] and MISSION[1] <= y <= MISSION[3]
        # союзники бьют по самой миссии — блокпост на трассе остаётся герою
        cult = sorted((e for e in self.enemies if e.alive and e.faction == "cult"), key=lambda e: not in_mission(e))
        allies = [name for flag, name in (("route_lira", "паладины Братства"), ("route_loner", "Панк"))
                  if f.get(flag)]
        down = cult[:len(cult) // 2 + len(allies) - 1] if allies else []
        for e in down:
            e.hp, e.alive = 0, False
            self.level.add_corpse(e, dict(e.loot or {}))
        f["baker_assault"] = True
        f["mission_gate_open"] = True
        if allies:
            self.log(f"Штурм! {' и '.join(allies).capitalize()} бьют по миссии с флангов — "
                     f"охрана редеет на глазах ({len(down)} балахонов уже не встанут).")
        else:
            self.log("Вы идёте на миссию в одиночку. Ворота трещат, послушники хватаются за оружие.")
        self.make_hostile("cult")
        if any(e.alive and e.faction == "cult" for e in self.enemies):
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
        self._spawn_npc("baker", "amos_b7", BUNKER_SPOT)
        self.set_stage("mq_grandpa", 80)
        self.gain_xp(150)
        self.log({"shadow": "Дед выскальзывает из кельи. Никто ничего не видел — пока.",
                  "deal": "Дед выходит из кельи под взглядами послушников. Сделка есть сделка.",
                  "steel": "Дед выходит из кельи, переступая через гильзы."}[path]
                 + " Он идёт к складу «Бейкер-7», в дюны на северо-востоке.")
