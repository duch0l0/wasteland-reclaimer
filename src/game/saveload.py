"""
Сохранение и загрузка (saves/<слот>.json + миниатюра <слот>.png).

Сохраняется всё, что меняется по ходу игры: герой (здоровье, опыт, перки,
снаряжение), рюкзак, флаги сюжета и стадии квестов, запасы торговцев,
карта мира. По каждой посещённой локации — живые и убитые враги, тела с
добычей, содержимое ящиков, подобранные предметы, открытые двери, кто из
NPC ушёл, разведанное на миникарте и пятна крови.

Локации при загрузке строятся заново из данных, и поверх накладывается
сохранённое — так сохранения не ломаются при правке карт, пока не меняется
порядок врагов и контейнеров. Случайные встречи не сохраняются: загрузка
из встречи вернёт на карту мира в то же место.
"""
import json
import os
import time

import pygame

from .. import settings as S
from ..location import LOCATION_DEFS

SAVE_DIR = "saves"
SLOTS = ["1", "2", "3", "4", "5", "6"]
QUICK = "quick"
VERSION = 1


def _path(slot, ext="json"):
    import sys
    return os.path.join(sys.modules[__name__].SAVE_DIR, f"{slot}.{ext}")


def slot_info(slot):
    """Краткое описание слота для меню или None, если пусто/битый."""
    try:
        with open(_path(slot), "r", encoding="utf-8") as f:
            d = json.load(f)
        return d["meta"]
    except (OSError, ValueError, KeyError):
        return None


class SaveMixin:
    # ------------------------------------------------------------ можно ли
    def can_save(self):
        if self.combat.active:
            return "Нельзя сохраняться в бою."
        if self.game_over:
            return "Мёртвые не сохраняются."
        if self.slides:
            return "Сначала досмотрите."
        if self.action.active and self.action.chasing():
            return "За вами гонятся — не до сохранений."
        return None

    # ------------------------------------------------------------ сохранить
    def save_game(self, slot):
        why = self.can_save()
        if why:
            self.log(why)
            return False
        os.makedirs(SAVE_DIR, exist_ok=True)
        data = {"version": VERSION, "meta": self._meta(), "state": self._state()}
        tmp = _path(slot) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, _path(slot))  # запись целиком или никак — сохранение не побьётся
        if self.last_frame is not None:
            thumb = pygame.transform.smoothscale(self.last_frame, (192, 108))
            pygame.image.save(thumb, _path(slot, "png"))
        self.log(f"Игра сохранена ({'быстрое сохранение' if slot == QUICK else 'слот ' + slot}).")
        return True

    def _meta(self):
        where = "Карта пустоши" if self.mode == "world" else self.loc.name
        return {"where": where, "level": self.player.level_sys.level, "time": time.strftime("%d.%m.%Y %H:%M"),
                "played": int(self.play_ms // 1000), "hp": f"{self.player.hp}/{self.player.max_hp}"}

    def _state(self):
        p = self.player
        encounter = self.loc.is_encounter
        return {
            "player": {"pos": list(p.rect.topleft), "hp": p.hp, "max_hp": p.max_hp, "base_ap": p.base_ap,
                       "ac": p.ac, "base_damage": p.base_damage, "level": p.level_sys.level,
                       "xp": p.level_sys.xp, "perks": p.perks, "pending_perks": p.pending_perks,
                       "weapon": p.weapon, "equipment": p.equipment, "dir": p.anim.direction,
                       "rads": p.rads, "skills": p.skills, "pending_skills": p.pending_skills},
            "inventory": dict(self.inventory.items),
            "flags": self.flags, "quests": self.quests, "traders": self.traders,
            "world": {"pos": list(self.worldmap.pos), "known": sorted(self.worldmap.known), "v": 2,
                      "fog": __import__("base64").b64encode(__import__("zlib").compress(self.worldmap.fog_bytes())).decode()},
            "mode": "world" if (self.mode == "world" or encounter) else "local",
            "loc": None if encounter else self.loc.id,
            "locations": {lid: self._loc_state(loc) for lid, loc in self.locations.items()},
            "log": self.log_lines[-6:], "played_ms": self.play_ms,
            "merc_mode": self.merc_mode,
            "other_profile": self._profile_to_json(self.other_profile),
            "dex_profile": self._profile_to_json(getattr(self, "dex_profile", None)),
            "companion": None if self.companion is None else {
                "hp": self.companion.hp, "max_hp": self.companion.max_hp, "down": self.companion.down},
        }

    @staticmethod
    def _profile_to_json(prof):
        if not prof:
            return None
        c = prof.get("companion")
        return {**prof, "companion": None if c is None else {"hp": c.hp, "max_hp": c.max_hp}}

    def _profile_from_json(self, prof):
        if not prof:
            return None
        c = prof.get("companion")
        if c:
            from ..entities import Companion
            from ..location import npc_animations
            dog = Companion((0, 0), npc_animations("dog"))
            dog.hp, dog.max_hp = max(1, c["hp"]), c["max_hp"]
            c = dog
        return {**prof, "companion": c}

    @staticmethod
    def _loc_state(loc):
        lv = loc.level
        base = [c for c in lv.containers if not c.get("corpse")]
        return {
            "enemies": [{"alive": e.alive, "hp": e.hp, "pos": list(e.rect.topleft), "hostile": e.hostile,
                         "talked": e.talked, "present": e in loc.enemies} for e in loc.enemies_all],
            "npcs": [{"id": n.npc_id, "pos": list(n.rect.topleft)} for n in loc.npcs],
            "containers": [{"loot": c["loot"], "opened": c["opened"], "hook_used": c.get("on_put") is None}
                           for c in base],
            "removed": [i for i, o in enumerate(getattr(lv, "objects", [])) if o.get("hidden") and not o.get("gate")],
            "corpses": [{"enemy": loc.enemies_all.index(c["enemy"]), "loot": c["loot"], "opened": c["opened"]}
                        for c in lv.corpses if c.get("enemy") in loc.enemies_all],
            "pickups": [[p["kind"], p["count"], p["rect"].x, p["rect"].y] for p in lv.pickups],
            "doors": [list(d) for d in lv.doors],
            "explored": [list(t) for t in getattr(lv, "explored", ())],
            "met": sorted(getattr(lv, "met", ())),
            "stains": [list(s) for s in getattr(lv, "stains", [])[-200:]],
            "hordes_done": [i for i, h in enumerate(getattr(lv, "hordes", [])) if h["done"]],
        }

    # ------------------------------------------------------------ загрузить
    def load_game(self, slot):
        try:
            with open(_path(slot), "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            self.log("Не удалось прочитать сохранение.")
            return False
        self._apply_state(data["state"])
        self.log(f"Загружено: {data['meta']['where']}, {data['meta']['time']}.")
        return True

    def _apply_state(self, st):
        from ..inventory import Inventory
        # чистый лист: всё открытое закрыть, бой и эффекты сбросить
        self.menu = None
        self.slides = self.term = self.loot = self.trade = self.perk_choices = None
        self.inv_open = self.craft_open = self.journal_open = False
        self.dialogue.close()
        self.combat.active = False
        self.combat.order = []
        self.game_over = False
        self.autowalk = self.combat_queue = None
        self.gore.parts = []

        self.flags = st["flags"]
        self.quests = st["quests"]
        self.traders = st["traders"]
        self.inventory = Inventory("data/recipes.json")
        self.inventory.items = dict(st["inventory"])
        self.inventory.on_add = self.on_item_added

        p = self.player
        ps = st["player"]
        p.inventory = self.inventory
        p.hp, p.max_hp, p.base_ap, p.ac = ps["hp"], ps["max_hp"], ps["base_ap"], ps["ac"]
        p.base_damage = ps["base_damage"]
        p.level_sys.level, p.level_sys.xp = ps["level"], ps["xp"]
        p.perks, p.pending_perks = ps["perks"], ps["pending_perks"]
        from .. import skills
        p.skills = dict(ps.get("skills") or skills.defaults(ps["level"]))   # старые сохранения — без навыков
        p.pending_skills = ps.get("pending_skills", 0)
        p.weapon, p.equipment = ps["weapon"], ps["equipment"]
        p.alive = True
        p.ap = p.max_ap
        p.blinded = p.crippled_arms = p.crippled_legs = False
        p.skip_turns = 0
        p.rads = ps.get("rads", 0)
        p.dots = []
        p.anim.direction = ps.get("dir", "down")
        p.anim.set_action("idle")

        self.worldmap.known = set(st["world"]["known"])
        if st["world"].get("v") == 2:
            import base64
            import zlib
            self.worldmap.pos = pygame.Vector2(st["world"]["pos"])
            self.worldmap.set_fog(zlib.decompress(base64.b64decode(st["world"]["fog"])) if st["world"].get("fog") else None)
        else:   # сохранение со старой маленькой карты — встаём у локации, где был герой
            lid = st.get("loc") or "ruins"
            self.worldmap.pos = pygame.Vector2(LOCATION_DEFS.get(lid, LOCATION_DEFS["ruins"]).get(
                "world_pos", LOCATION_DEFS["ruins"]["world_pos"]))
            self.worldmap.set_fog(None)
        self.worldmap.target = None

        self.locations = {}
        for lid, ls in st["locations"].items():
            if lid in LOCATION_DEFS:
                self._restore_loc(self.get_location(lid), ls)
        self.play_ms = st.get("played_ms", 0)
        self.companion = None
        cs = st.get("companion")
        if cs:
            from ..entities import Companion
            from ..location import npc_animations
            self.companion = Companion((0, 0), npc_animations("dog"))
            self.companion.hp, self.companion.max_hp = max(1, cs["hp"]), cs["max_hp"]
        self.log_lines = list(st.get("log", []))
        self.merc_mode = st.get("merc_mode", False)
        self.other_profile = self._profile_from_json(st.get("other_profile"))
        self.dex_profile = self._profile_from_json(st.get("dex_profile"))

        if st["mode"] == "world" or not st["loc"]:
            self.loc = self.get_location(st["loc"] or "ruins")
            self.mode = "world"
        else:
            self.loc = self.get_location(st["loc"])
            self.mode = "local"
            self.apply_view()
            p.rect.topleft = tuple(ps["pos"])
            self.snap_camera()
        from .. import companion
        companion.place_near_player(self)
        if self.mode == "local":
            self.restore_town_hostility()
        self.sync_gates()

    @staticmethod
    def _restore_loc(loc, ls):
        lv = loc.level
        for e, es in zip(loc.enemies_all, ls["enemies"]):
            e.alive, e.hp, e.hostile, e.talked = es["alive"], es["hp"], es["hostile"], es["talked"]
            e.rect.topleft = tuple(es["pos"])
            e.anim.set_action("idle")
        loc.enemies[:] = [e for e, es in zip(loc.enemies_all, ls["enemies"]) if es.get("present", True)]
        keep = {n["id"]: n["pos"] for n in ls["npcs"]}
        loc.npcs[:] = [n for n in loc.npcs if n.npc_id in keep]
        from ..entities import NPC
        from ..location import npc_animations, NPC_NAMES
        have = {n.npc_id for n in loc.npcs}
        for nid in keep:   # пришедшие по ходу сюжета (караван Розы, спутники в Бейкере) — вернуть
            if nid not in have:
                loc.npcs.append(NPC((0, 0), npc_animations(nid), npc_id=nid, name=NPC_NAMES.get(nid, nid)))
        for n in loc.npcs:
            n.rect.topleft = tuple(keep[n.npc_id])
        base = [c for c in lv.containers if not c.get("corpse")]
        for c, cs in zip(base, ls["containers"]):
            c["loot"], c["opened"] = dict(cs["loot"]), cs["opened"]
            if cs.get("hook_used"):
                c["on_put"] = None
        for i in ls.get("removed", []):
            lv.remove_object(lv.objects[i])
        for cs in ls["corpses"]:
            enemy = loc.enemies_all[cs["enemy"]]
            box = lv.add_corpse(enemy, cs["loot"])
            box["opened"] = cs["opened"]
        lv.pickups = []
        for kind, count, x, y in ls["pickups"]:
            lv.add_pickup((x, y), kind, count)
        for d in [d for d in lv.doors if list(d) not in ls["doors"]]:
            lv.open_door(d)
        lv.explored = {tuple(t) for t in ls["explored"]}
        lv.met = set(ls["met"])
        lv._mm_fog = None
        lv._last_reveal = None
        lv.stains = [tuple(s) for s in ls["stains"]]
        for i in ls.get("hordes_done", []):
            if i < len(getattr(lv, "hordes", [])):
                lv.hordes[i]["done"] = True
