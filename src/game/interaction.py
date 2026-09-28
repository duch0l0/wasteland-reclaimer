"""Разговоры, контейнеры, двери, смена оружия, перки и награды за убийства."""
import pygame

from .. import perks
from ..weapons import WEAPONS, available


class InteractionMixin:
    def talk_to(self, speaker, tree_id):
        if self.dialogue.start(tree_id):
            self.dialogue_speaker = speaker
            # собеседник поворачивается к игроку
            speaker.anim.face(self.player.rect.centerx - speaker.rect.centerx,
                              self.player.rect.centery - speaker.rect.centery)
            return True
        return False

    def interact(self):
        """E: поговорить с NPC рядом, иначе терминал, контейнер, дверь, предмет на земле."""
        reach = self.player.rect.inflate(60, 60)  # хитбокс узкий, достаём NPC с соседнего тайла
        for npc in self.npcs:
            if reach.colliderect(npc.rect) and self.talk_to(npc, npc.npc_id):
                return
        term = self.level.terminal_near(self.player.rect)
        if term and term["id"]:
            self.open_terminal(term["id"])
            return
        talker = self._talker_near()
        if talker:
            self.talk_to(talker, talker.talk)
            return
        box = self.level.container_near(self.player.rect)
        if box:
            self.open_container(box)
            return
        door = self.level.adjacent(self.level.doors, self.player.rect)
        if door:
            self.open_door(door)
            return
        item = self.level.pickup_near(self.player.rect)
        if item:
            self.level.take_pickup(item, self.inventory, log_fn=self.log)

    def _talker_near(self):
        """Мирный враг с диалогом (Шрам) рядом — с ним можно заговорить снова."""
        reach = self.player.rect.inflate(60, 60)
        return next((e for e in self.enemies if e.alive and e.talk and not e.hostile
                     and reach.colliderect(e.rect)), None)

    def check_talkers(self):
        """Враги с диалогом (Шрам) сначала заговаривают, а не стреляют."""
        p = self.player
        for e in self.enemies:
            if (e.alive and e.talk and not e.talked and not e.hostile
                    and pygame.Vector2(e.rect.center).distance_to(p.rect.center) <= e.aggro
                    and self.combat.los(e, p)):
                e.talked = True
                self.talk_to(e, e.talk)
                return

    def open_container(self, c):
        req = c.get("requires")
        if req and not self.check_condition(req):
            self.log(req.get("msg", f"{c['name'].capitalize()}: заперто."))
            return
        c["opened"] = True
        loot = c["loot"]
        if loot:
            self.log(f"Вы обыскиваете: {c['name']}. " + ", ".join(f"{k} ×{v}" for k, v in loot.items()))
            for k, v in loot.items():
                self.inventory.add(k, v)
        else:
            self.log(f"{c['name'].capitalize()}: пусто. Кто-то успел раньше.")
        # чужое брать — с последствиями
        owner = c.get("owner")
        if owner == "gena" and any(n.npc_id == "gena" for n in self.npcs):
            self.flags["gena_robbed"] = True
            self.log("Вы чувствуете на спине чей-то взгляд... Гена это так не оставит.")
        elif owner and self.loc.faction_members(owner):
            # как в Fallout: кражу замечают, только если вор на виду
            p = self.player
            seen = [e for e in self.loc.faction_members(owner)
                    if pygame.Vector2(e.rect.center).distance_to(p.rect.center) <= e.aggro and self.combat.los(e, p)]
            if not seen:
                self.log("Кажется, никто не заметил.")
                return
            self.log(f"{seen[0].name.capitalize()}: Эй! Это наше!")
            self.make_hostile(owner)
            self.combat.start(player_first=False)

    def open_door(self, tile):
        if self.inventory.has("отмычка"):
            self.inventory.remove("отмычка")
            self.level.open_door(tile)
            self.log("Отмычка тихо щёлкает. Дверь открыта.")
        elif self.inventory.has("лом"):
            self.inventory.remove("лом")
            self.level.open_door(tile)
            self.log("Вы выламываете дверь ломом. Лом гнётся, дверь сдаётся. Грохот на всю округу.")
            factions = {e.faction for e in self.enemies if e.alive and e.faction}
            if factions:
                self.log("Кажется, вас услышали.")
                for f in factions:
                    self.make_hostile(f)
                self.combat.start(player_first=False)
        else:
            self.log("Заперто. Нужна отмычка (у Гены) или хотя бы лом, чтобы выломать.")

    def switch_weapon(self, to=None):
        """Как «сменить руку» в Fallout: без затрат ОД. Без аргумента — следующее по кругу."""
        guns = available(self.inventory)
        if to is None:
            if len(guns) == 1:
                self.log("Другого оружия нет. Говорят, где-то в развалинах на северо-западе спрятан самопал...")
                return
            to = guns[(guns.index(self.player.weapon) + 1) % len(guns)] if self.player.weapon in guns else "melee"
        if to not in guns:
            return
        self.player.weapon = to
        self.log(f"В руках: {self.weapon_name()}.")

    def weapon_name(self):
        if self.player.weapon == "melee" and self.inventory.has("заточенный лом"):
            return "Заточенный лом"
        return WEAPONS[self.player.weapon]["name"]

    def gain_xp(self, amount):
        for msg in self.player.gain_xp(amount):
            self.log(msg)

    def take_perk(self, perk):
        perks.take(self.player, perk)
        self.player.pending_perks -= 1
        self.perk_choices = None
        self.log(f"Новый перк: {perk['name']}.")

    def on_enemy_killed(self, enemy):
        """Вызывается боевым модулем: добыча, опыт, перки, флаги квестов."""
        self.log(f"{enemy.name[:1].upper() + enemy.name[1:]} повержен.")
        mult = 2 if self.player.perk_rank("looter") else 1
        for item, cnt in (enemy.loot or {}).items():
            self.inventory.add(item, cnt * mult)
            self.log(f"Трофей: {item} ×{cnt * mult}")
        if self.player.perk_rank("scavenger") and self.player.hp < self.player.max_hp:
            self.player.hp = min(self.player.max_hp, self.player.hp + 5)
            self.log("Падальщик: +5 HP.")
        self.gain_xp(enemy.xp_reward)
        if enemy.faction == "gang" and not self.loc.faction_members("gang"):
            self.flags["gang_dead"] = True
            self.log("Бензо-банды больше нет. Гена будет рад. Наверное.")
