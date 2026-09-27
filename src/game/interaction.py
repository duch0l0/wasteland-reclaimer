"""Разговоры, контейнеры, двери, смена оружия, перки и награды за убийства."""
import pygame

from .. import perks
from ..weapons import WEAPONS


class InteractionMixin:
    def talk_to(self, speaker, tree_id):
        if self.dialogue.start(tree_id):
            self.dialogue_speaker = speaker
            return True
        return False

    def interact(self):
        """E: поговорить с NPC рядом, иначе обыскать контейнер, открыть дверь, подобрать."""
        reach = self.player.rect.inflate(60, 60)  # хитбокс узкий, достаём NPC с соседнего тайла
        for npc in self.npcs:
            if reach.colliderect(npc.rect) and self.talk_to(npc, npc.npc_id):
                return
        closed = [c["tile"] for c in self.level.containers if not c["opened"]]
        box = self.level.adjacent(closed, self.player.rect)
        if box:
            self.open_container(next(c for c in self.level.containers if c["tile"] == box))
            return
        door = self.level.adjacent(self.level.doors, self.player.rect)
        if door:
            self.open_door(door)
            return
        self.level.collect_pickups(self.player.rect.inflate(6, 6), self.inventory, log_fn=self.log)

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
            self.log("Шрам: Эй! Я же сказал — склад наш!")
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

    def switch_weapon(self):
        """Как «сменить руку» в Fallout: без затрат ОД."""
        if self.player.weapon == "melee":
            if not self.inventory.has(WEAPONS["pistol"]["item"]):
                self.log("Другого оружия нет. Говорят, где-то в руинах лежит самопал...")
                return
            self.player.weapon = "pistol"
        else:
            self.player.weapon = "melee"
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
