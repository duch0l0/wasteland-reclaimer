"""Разговоры, контейнеры, двери, смена оружия, перки и награды за убийства."""
import pygame

from .. import perks
from ..weapons import WEAPONS, available


class InteractionMixin:
    def talk_to(self, speaker, tree_id):
        if speaker in self.npcs and self.scared_line(speaker):   # город видел убийцу — не разговаривают
            return True
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
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:   # Shift + E — напасть на жителя рядом
            npc = next((n for n in self.npcs if reach.colliderect(n.rect)), None)
            if npc is not None:
                self.attack_npc(npc)
                return
        if self.ally is not None and not self.ally.down and reach.colliderect(self.ally.rect) \
                and self.talk_to(self.ally, f"ally_{self.ally.type_id}"):
            return
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

    def open_door(self, tile):
        gate = getattr(self.level, "gate_at", lambda t: None)(tile)
        if gate:
            self.use_gate(gate)
            return
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

    def _check_cleared(self):
        if self.action.hordes_left():
            return   # в экшене район чист, только когда вышли все толпы из домов
        """Стая крысолюдов в ливнёвке перебита (или отравлена) — шерифу будет что рассказать."""
        if self.loc.id == "drain" and not any(e.alive and e.pack == "ratmen" for e in self.enemies):
            if not self.flags.get("rats_cleared"):
                self.flags["rats_cleared"] = True
                self.log("Крысолюдов в ливнёвке больше нет. Шериф Брэддок будет рад это услышать.")
                self.sync_story()
        if self.loc.id == "vault57" and not any(e.alive for e in self.enemies):
            self.flags["vault_cleared"] = True
        from ..location import LOCATION_DEFS
        flag = LOCATION_DEFS.get(self.loc.id, {}).get("clear_flag")
        # зачищено — когда враги были (или жители взялись за оружие) и никого с оружием не осталось:
        # и враждебных, и тех, у кого есть сторона (Анклав у ворот молчит, но жив — значит, не зачищено)
        if flag and not self.flags.get(flag) and self.enemies and \
                not any(e.alive and (e.hostile or getattr(e, "faction", None)) for e in self.enemies):
            self.flags[flag] = True
            name = LOCATION_DEFS[self.loc.id]["name"]
            self.log(f"Район зачищен: {name}. Тишина — даже мухи не жужжат.")
            self.gain_xp(50)   # за героя; в экшене за Дэкса опыта нет
            self.sync_story()

    def use_gate(self, gate):
        """Гермодверь: открыта флагом (терминал) или ключ-картой из рюкзака;
        pry — простой засов, который поддевается ломом (лом у героя всегда при себе)."""
        if self.flags.get(gate["flag"]):
            self.level.open_gate(gate)
        elif gate.get("pry") or gate.get("key") and self.inventory.has(gate["key"]):
            self.flags[gate["flag"]] = True
            self.level.open_gate(gate)
            self.log(gate.get("open_msg") or
                     f"Карта «{gate['key']}» пищит в замке. Гермодверь с рёвом откатывается в сторону.")
            self.audio.play("hit")
            self.sync_story()
        else:
            self.log(gate["msg"])

    def sync_gates(self):
        """Двери, открытые флагом (терминал, загрузка сохранения), — открыть на карте."""
        for g in getattr(self.level, "gates", []):
            if not g["open"] and self.flags.get(g["flag"]):
                self.level.open_gate(g)

    def join_ally(self, ally_id):
        """Спутник-человек (src/companion.ALLIES) идёт с героем; житель с карты уходит вместе с ним."""
        from ..companion import ALLIES, make_ally, _place_one
        if self.ally is not None:
            self.dismiss_ally()
        prof = ALLIES[ally_id]
        home = next((n for n in self.npcs if n.npc_id == prof["npc"]), None)
        self.ally = make_ally(ally_id)
        if home is not None:
            self.ally.rect.center = home.rect.center
            self.loc.npcs[:] = [n for n in self.npcs if n is not home]
        else:
            _place_one(self, self.ally)
        self.flags[f"{prof['npc']}_left"] = True
        self.flags[f"{ally_id}_with_hero"] = True
        self.log(f"{self.ally.name} теперь с вами. В бою действует сама; поговорить — E рядом.")

    def dismiss_ally(self):
        """Спутник-человек возвращается туда, где его встретили."""
        if self.ally is None:
            return
        from ..companion import ALLIES
        prof = ALLIES[self.ally.type_id]
        self.flags.pop(f"{prof['npc']}_left", None)
        for loc in self.locations.values():   # житель снова на своём месте (в следующий заход)
            home = next((n for n in getattr(loc, "npcs_all", []) if n.npc_id == prof["npc"]), None)
            if home is not None and home not in loc.npcs:
                loc.npcs.append(home)
        self.flags.pop(f"{self.ally.type_id}_with_hero", None)
        self.log(f"{self.ally.name} уходит обратно — вас там будут ждать.")
        self.ally = None

    def join_dog(self):
        """Пёс с цепи у лагеря рейдеров становится спутником."""
        from ..entities import Companion
        from ..location import npc_animations
        dog = next((n for n in self.npcs if n.npc_id == "dog"), None)
        pos = dog.rect.topleft if dog else self.player.rect.topleft
        self.companion = Companion((0, 0), npc_animations("dog"))
        self.companion.rect.topleft = pos
        self.loc.npcs[:] = [n for n in self.npcs if n.npc_id != "dog"]
        self.flags["dog_joined"] = True
        self.log(f"{self.companion.name} теперь с вами. В бою он кусает ближайшего врага сам.")

    def switch_weapon(self, to=None):
        """Как «сменить руку» в Fallout: без затрат ОД. Без аргумента — следующее по кругу."""
        if self.action.active:
            self.action.switch()
            return
        guns = available(self.inventory)
        if to is None:
            if len(guns) == 1:
                self.log("Огнестрела нет. Шериф Брэддок, говорят, платит оружием за работу.")
                return
            to = guns[(guns.index(self.player.weapon) + 1) % len(guns)] if self.player.weapon in guns else "melee"
        if to not in guns:
            return
        self.player.weapon = to
        from ..weapons import shortfall, SKILL_NAMES
        short = shortfall(self.player, to)
        if short:
            w = WEAPONS[to]
            self.log(f"В руках: {self.weapon_name()} — но не по руке: нужно {SKILL_NAMES[w.get('skill', 'guns')]} "
                     f"{w['req']}, не хватает {short}. Мажет, очередью не стрелять.")
        else:
            self.log(f"В руках: {self.weapon_name()}.")

    def weapon_name(self):
        if self.player.weapon == "melee" and self.inventory.has("заточенный лом"):
            return "Заточенный лом"
        return WEAPONS[self.player.weapon]["name"]

    def gain_xp(self, amount):
        if self.merc_mode:
            return   # Барстоу за Дэкса — экшен без опыта и уровней
        msgs = self.player.gain_xp(amount)
        for msg in msgs:
            self.log(msg)
        if msgs:
            self.audio.play("levelup")

    def take_perk(self, perk):
        """Выбор в окне повышения уровня: навык (+10) или перк."""
        from .. import skills
        self.perk_choices = None
        if perk.get("kind") == "skill":
            skills.raise_skill(self.player, perk["id"])
            self.player.pending_skills -= 1
            s = skills.SKILL_BY_ID[perk["id"]]
            self.log(f"Навык «{s['name']}» теперь {self.player.skill(perk['id'])}.")
            return
        perks.take(self.player, perk)
        self.player.pending_perks -= 1
        self.log(f"Новый перк: {perk['name']}.")

    def on_enemy_killed(self, enemy):
        """Вызывается боевым модулем: добыча, опыт, перки, флаги квестов."""
        if not self.action.active:   # в экшене счёт убитых — на экране, лог не засоряем
            self.log(f"{enemy.name[:1].upper() + enemy.name[1:]} повержен.")
        if getattr(enemy, "npc_id", None):   # убитый житель не воскреснет при следующем приходе
            self.flags[f"killed_{enemy.npc_id}"] = True
        mult = 2 if self.player.perk_rank("looter") else 1
        from ..balance import roll_loot
        loot = {item: cnt * mult for item, cnt in roll_loot(enemy.loot).items()}
        self.level.add_corpse(enemy, loot)
        if loot and not self.action.active:
            self.log("На теле что-то есть — можно обыскать.")
        if self.player.perk_rank("scavenger") and self.player.hp < self.player.max_hp:
            self.player.hp = min(self.player.max_hp, self.player.hp + 5)
            self.log("Падальщик: +5 HP.")
        from ..skills import xp_for_kill
        xp = xp_for_kill(enemy.xp_reward, getattr(enemy, "level", 1), self.player.level_sys.level)
        if xp and not self.merc_mode:
            self.log(f"+{xp} опыта." + (" Слабый противник — опыта мало." if xp < enemy.xp_reward else ""))
        self.gain_xp(xp)
        if enemy.type_id == "raider" and not any(e.alive and e.type_id == "raider" for e in self.enemies):
            self.flags["raiders_dead"] = True
            if any(n.npc_id == "dog" for n in self.npcs):
                self.log("Лагерь рейдеров пуст. Где-то у палаток скулит пёс на цепи.")
            self.sync_story()
        self._check_cleared()
        if enemy.faction == "gang" and not self.loc.faction_members("gang"):
            self.flags["gang_dead"] = True
            self.log("Бензо-банды больше нет. Гена будет рад. Наверное.")
