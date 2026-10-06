"""
Наёмник Дэкс: в Барстоу играешь за него.

Герой нанимает Дэкса в Пятнадцатой (квест «Контракт на Барстоу», data/dialogues.json → dex)
и отправляет вызволять застрявший караван Розы. Дальше управление переходит к Дэксу:
у него своё здоровье, уровень, перки и рюкзак (винтовка, патроны, стимуляторы),
в изометрическом Барстоу он — выживший с винтовкой из набора Zombie City. Герой
тем временем ждёт там, где стоял. Уйти из Барстоу Дэкс соглашается, только когда
город зачищен и Роза расплатилась; тогда караван приходит в Пятнадцатую, герою —
доля, управление возвращается к нему.

Профиль персонажа — те же поля, что в сохранении: состояние героя, рюкзак, где стоит.
"""
from ..inventory import Inventory

# с чем Дэкс уходит в первый раз
DEX_START = {
    "player": {"hp": 120, "max_hp": 120, "base_ap": 9, "ac": 12, "base_damage": 6, "level": 4, "xp": 0,
               "perks": {"steady_hand": 1}, "pending_perks": 0, "weapon": "rifle",
               "equipment": {"head": None, "body": None, "weapon": None}, "rads": 0,
               "skills": {"guns": 85, "melee": 70, "medicine": 40, "science": 20, "speech": 30, "survival": 60}},
    "inventory": {"охотничья винтовка": 1, "патроны": 40, "стимулятор": 2, "бинт": 3, "крышки": 15},
    "loc": "barstow", "pos": None,
}


class MercMixin:
    merc_mode = False
    other_profile = None     # профиль того, кем сейчас НЕ играешь (герой, пока играешь за Дэкса)

    # ------------------------------------------------------------ профиль
    def capture_profile(self):
        p = self.player
        return {"player": {"hp": p.hp, "max_hp": p.max_hp, "base_ap": p.base_ap, "ac": p.ac,
                           "base_damage": p.base_damage, "level": p.level_sys.level, "xp": p.level_sys.xp,
                           "perks": dict(p.perks), "pending_perks": p.pending_perks, "weapon": p.weapon,
                           "equipment": dict(p.equipment), "rads": p.rads, "skills": dict(p.skills),
                           "pending_skills": p.pending_skills},
                "inventory": dict(self.inventory.items),
                "loc": self.loc.id, "pos": list(p.rect.topleft),
                "companion": self.companion, "ally": getattr(self, "ally", None)}

    def restore_profile(self, prof):
        p = self.player
        ps = prof["player"]
        p.hp, p.max_hp, p.base_ap, p.ac = ps["hp"], ps["max_hp"], ps["base_ap"], ps["ac"]
        p.base_damage = ps["base_damage"]
        p.level_sys.level, p.level_sys.xp = ps["level"], ps["xp"]
        p.perks, p.pending_perks = dict(ps["perks"]), ps["pending_perks"]
        p.weapon, p.equipment = ps["weapon"], dict(ps["equipment"])
        p.rads = ps.get("rads", 0)
        from ..skills import defaults
        p.skills = dict(ps.get("skills") or defaults(ps["level"]))
        p.pending_skills = ps.get("pending_skills", 0)
        p.dots = []
        p.alive = True
        p.blinded = p.crippled_arms = p.crippled_legs = False
        self.inventory = Inventory("data/recipes.json")
        self.inventory.items = dict(prof["inventory"])
        self.inventory.on_add = self.on_item_added
        p.inventory = self.inventory
        self.companion = prof.get("companion")
        self.ally = prof.get("ally")
        self.enter_location(prof["loc"], at=None if prof.get("pos") is None else
                            (prof["pos"][0] // 48, prof["pos"][1] // 48))
        if prof.get("pos") is not None:
            p.rect.topleft = tuple(prof["pos"])
            self.snap_camera()
        p.ap = p.max_ap

    # ------------------------------------------------------------ туда и обратно
    def merc_start(self):
        """Слайды «Тем временем…» кончились — играем за Дэкса в Барстоу."""
        if self.merc_mode:
            return
        hero = self.capture_profile()
        dex = getattr(self, "dex_profile", None) or DEX_START
        self.other_profile = hero
        self.merc_mode = True
        self.companion = None
        self.ally = None
        self.restore_profile(dex)
        self.log("Вы играете за наёмника Дэкса. Барстоу, трасса I-15. Где-то здесь караван Розы.")

    def merc_finish(self):
        """Караван вызволен — Дэкс уходит в Пятнадцатую, управление — снова герою."""
        if not self.merc_mode:
            return
        self.dex_profile = self.capture_profile()
        self.dex_profile["companion"] = None
        self.dex_profile["ally"] = None
        self.merc_mode = False
        hero, self.other_profile = self.other_profile, None
        self.restore_profile(hero)
        self.flags["dex_back"] = True
        self.flags["caravan_arrived"] = True
        self._spawn_npc("ruins", "dex", (12, 25))
        self._spawn_npc("ruins", "rose", (48, 24))
        self.set_stage("sq_merc", 90)
        if self.flags.get("barstow_base_cleared"):   # Дэкс зачистил и базу морпехов — склад гарнизона в караван
            self.inventory.add("крышки", 150)
            self.inventory.add("аптечка армейская", 1)
            self.log("Дэкс привёз и со склада морпехов: 150 крышек и армейскую аптечку — твоя доля.")
        self.log("Караван Розы въезжает в Пятнадцатую. Впереди — Дэкс, пыльный и довольный.")

    def _spawn_npc(self, loc_id, npc_id, tile):
        from ..entities import NPC
        from ..location import npc_animations, NPC_NAMES
        loc = self.get_location(loc_id)
        if any(n.npc_id == npc_id for n in loc.npcs):
            return
        loc.npcs.append(NPC((tile[0] * 48, tile[1] * 48), npc_animations(npc_id), npc_id=npc_id,
                            name=NPC_NAMES.get(npc_id, npc_id)))

    def merc_leave_attempt(self):
        """Дэкс на выходе из Барстоу: уходит, только выполнив контракт."""
        if self.stage("sq_barstow") >= 100:
            self.show_slides("merc_back")
            return True
        self.log("Дэкс: «Контракт не закрыт. Роза ждёт, гули жрут. Никуда я не пойду».")
        return False
