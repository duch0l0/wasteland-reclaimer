"""
Ринг «Скам-Питта» в Джанктауне (docs/city_plan.md, этап 2) — как бокс в Нью-Рино.

Бармен Нил ведёт лестницу из пяти бойцов. Бой — настоящий, на движке боя, но по правилам ринга:
только кулаки (оружие и спутники — в сторону), до нокаута: упавший не умирает, а остаётся с 1 HP.
Перед боем — ставка на себя (0 / 50 / 100 крышек, выигрыш вдвое). Перед третьим боем Гизмо просит
лечь: согласиться — и упасть в третьем раунде (300 крышек от Гизмо), или согласиться и победить раньше —
Гизмо этого не забудет. Чемпион — пояс, +10 к Рукопашной и слава по всей пустоше.
"""
from ..entities import Enemy
from ..location import npc_animations
from ..combat import tile_of, rect_pos_for_tile

FIGHTERS = [
    {"name": "Мясник Бо", "sprite": "folk_e", "hp": 26, "damage": 4, "skill": 50, "ac": 6, "ap": 7, "prize": 40,
     "hit_verb": "лупит вас кулаком, как тушу на крюке"},
    {"name": "Сестрёнка Тэсс", "sprite": "girl_hood", "hp": 32, "damage": 5, "skill": 64, "ac": 12, "ap": 9, "prize": 70,
     "hit_verb": "бьёт вас быстрой двойкой"},
    {"name": "Громила Изо", "sprite": "gang", "hp": 46, "damage": 7, "skill": 64, "ac": 10, "ap": 7, "prize": 110,
     "hit_verb": "бьёт вас кулаком размером с окорок"},
    {"name": "Лу «Гаечный ключ»", "sprite": "folk_i", "hp": 52, "damage": 8, "skill": 72, "ac": 13, "ap": 9, "prize": 160,
     "hit_verb": "бьёт вас, будто закручивает гайку"},
    {"name": "Бык Маккой, чемпион", "sprite": "boss", "hp": 70, "damage": 10, "skill": 80, "ac": 14, "ap": 9, "prize": 300,
     "hit_verb": "бьёт вас так, что в ушах звенит колокол"},
]
DIVE_FIGHT = 2          # третий бой — Гизмо просит лечь
DIVE_ROUND = 3


class RingMixin:
    def ring_next(self):
        return self.flags.get("ring_wins", 0)

    def ring_fight(self, bet=0, dive=False):
        """Выйти на ринг против следующего бойца лестницы."""
        n = self.ring_next()
        if n >= len(FIGHTERS):
            self.log("Бить больше некого: чемпион — вы.")
            return
        f = FIGHTERS[n]
        if bet:
            self.inventory.remove("крышки", bet)
        p = self.player
        d = {"name": f["name"], "hp": f["hp"], "damage": f["damage"], "skill": f["skill"], "ac": f["ac"], "ap": f["ap"],
             "sequence": 6, "ai": "melee", "range": 1, "hit_verb": f["hit_verb"], "level": 2 + n, "xp": 0, "hitbox": [28, 32]}
        t = tile_of(p)
        opp = Enemy(rect_pos_for_tile(p, (t[0] + 2, t[1])), npc_animations(f["sprite"]), "ring_fighter", d)
        opp.hostile, opp.faction, opp.ring = True, "ring", True
        self.loc.enemies.append(opp)
        self.ring = {"opp": opp, "n": n, "bet": bet, "dive": dive, "weapon": p.weapon, "result": None}
        p.weapon = "melee"
        self.log(f"Нил бьёт в гонг: «{f['name']} против чужака! Только кулаки!»")
        if not self.combat.start(player_first=True):
            self._ring_finish(None)

    def ring_ko(self, ent):
        """Удар, который убил бы, — на ринге нокаут: боец лежит с 1 HP, бой окончен."""
        r = self.ring
        if r is None or ent not in (self.player, r["opp"]):
            return False
        ent.hp, ent.alive = 1, True
        self._ring_finish(ent is not self.player)
        return True

    def ring_turn(self):
        """Начало хода героя: договорился лечь — в третьем раунде картинно падает."""
        r = self.ring
        if r and r["dive"] and self.combat.round >= DIVE_ROUND:
            self.log("Третий раунд. Вы пропускаете удар, которого не было, и красиво падаете на доски.")
            self.player.hp = max(1, self.player.hp)
            self._ring_finish(False)
            return True
        return False

    def _ring_finish(self, won):
        r, self.ring = self.ring, None
        if r is None:
            return
        opp = r["opp"]
        if opp in self.loc.enemies:
            self.loc.enemies.remove(opp)
        if self.combat.active:
            self.combat.end("Гонг! Бой окончен.")
        self.player.weapon = r["weapon"]
        if won is None:
            return
        f = FIGHTERS[r["n"]]
        if won:
            self.flags["ring_wins"] = r["n"] + 1
            self.inventory.add("крышки", f["prize"] + 2 * r["bet"])
            self.apply_effect({"type": "xp", "amount": 40 + 30 * r["n"]})
            self.log(f"НОКАУТ! {f['name']} лежит. Нил: «Победитель!» Приз — {f['prize']} крышек"
                     + (f", ставка — +{2 * r['bet']}" if r["bet"] else "") + ".")
            if r["dive"]:
                self.flags["ring_crossed_gizmo"] = True
                self.log("Из ложи Гизмо доносится звон разбитого бокала. Договор был — лечь. Вы не легли.")
            if r["n"] + 1 == len(FIGHTERS):
                self.flags["ring_champion"] = True
                self.inventory.add("пояс чемпиона Джанктауна", 1)
                self.player.skills["melee"] = self.player.skill("melee") + 10
                self.log("Вы — чемпион Джанктауна! Пояс ваш, а кулаки помнят каждый бой: +10 к Рукопашной.")
        else:
            self.flags["ring_losses"] = self.flags.get("ring_losses", 0) + 1
            if r["dive"]:
                self.flags["ring_dived"] = True
                self.inventory.add("крышки", 300)
                self.log("Изо помогает вам встать и незаметно суёт в карман триста крышек. «Босс доволен».")
            else:
                self.log(f"Вы лежите на досках. Над вами качается лампа. {f['name']} поднимает руки. Нил: «Приходи, когда отлежишься».")
