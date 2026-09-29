"""
Управление мышью, как в Fallout.

Вне боя (ЛКМ):
  земля — идти туда (по пути в обход стен);
  NPC — подойти и заговорить;  ящик/дверь — подойти и открыть;
  враг — напасть (если рядом и виден — сразу бой, первый ход ваш; иначе подойти).
В бою, в свой ход:
  ЛКМ по клетке — идти (1 ОД за клетку, путь и цена видны под курсором);
  ЛКМ по врагу — атаковать (в ближнем бою сначала подойти);
  ПКМ по врагу — прицельная атака (меню частей тела).
Кнопки, строки меню и варианты ответа — через кликабельные зоны (ui/common.py).
"""
from collections import deque

import pygame

from .. import settings as S
from ..combat import tile_of, rect_pos_for_tile, chebyshev
from ..entities import sprite_of
from .. import loader
from .. import props as P
from ..ui.common import hotspot_at, over_ui

T = S.TILE
NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class MouseMixin:
    # ------------------------------------------------------ что под курсором
    def view_pos(self, pos):
        """Точка экрана -> точка на холсте мира (он нарисован с масштабом self.zoom)."""
        return int(pos[0] / self.zoom), int(pos[1] / self.zoom)

    def world_pos(self, pos):
        vx, vy = self.view_pos(pos)
        return vx + int(self.cam.x), vy + int(self.cam.y)

    def tile_at_screen(self, pos):
        wx, wy = self.world_pos(pos)
        return wx // T, wy // T

    def entity_at_screen(self, pos):
        """Персонаж под курсором — по непрозрачным пикселям спрайта, передний первым."""
        people = [e for e in self.enemies if e.alive] + list(self.npcs)
        people.sort(key=lambda e: e.rect.bottom, reverse=True)
        screen_pos, pos = pos, self.view_pos(pos)
        for e in people:
            frame, r = sprite_of(e, self.cam)
            if r.collidepoint(pos):
                x, y = pos[0] - r.x, pos[1] - r.y
                if frame.get_at((x, y)).a > 40:
                    return e
        # промахнулся мимо силуэта — считаем кликом по клетке, где стоит персонаж
        tile = self.tile_at_screen(screen_pos)
        return next((e for e in people if tile_of(e) == tile), None)

    def object_at_screen(self, pos):
        """Терминал или контейнер по картинке (высокий шкаф кликается и за верхнюю часть),
        иначе объект в клетке. Предметы на земле — по иконке."""
        item = self.level.pickup_at(self.world_pos(pos))
        if item:
            return ("pickup", item)
        body = self.level.corpse_at(self.world_pos(pos))
        if body:
            return ("container", body)
        if hasattr(self.level, "terminal_sprite_at"):
            t = self.level.terminal_sprite_at(self.world_pos(pos))
            if t:
                return ("terminal", t)
        if hasattr(self.level, "container_sprite_at"):
            c = self.level.container_sprite_at(self.world_pos(pos))
            if c:
                return ("container", c)
        return self.object_at_tile(self.tile_at_screen(pos))

    def barrel_at_screen(self, pos):
        """Красная бочка под курсором (в неё можно выстрелить)."""
        wx, wy = self.world_pos(pos)
        for o in getattr(self.level, "objects", []):
            if not o.get("hidden") and P.info(o["name"]).get("explosive") and o["rect"].collidepoint(wx, wy):
                return o
        return None

    def object_at_tile(self, tile):
        """Закрытый контейнер или запертая дверь в клетке."""
        t = self.level.terminal_at(tile)
        if t and t["id"]:
            return ("terminal", t)
        c = self.level.container_at(tile)
        if c:
            return ("container", c)
        if tile in self.level.doors:
            return ("door", tile)
        return None

    # ------------------------------------------------------------- клики
    def handle_click(self, pos, button):
        key = hotspot_at(pos)
        if key is not None:
            self.last_button = button  # обыск: ЛКМ — вся стопка, ПКМ — одна штука
            if callable(key):
                key()
            elif button == 1:
                self.handle_key(key)  # зона, равная клавише
            return
        if self.game_over or self.mode != "local" or self.menu:
            return
        if self.combat.aim_menu:  # клик мимо меню прицеливания — закрыть его
            self.combat.aim_menu = False
            return
        if self.modal_open() or over_ui(pos):
            return
        if self.combat.active:
            self._combat_click(pos, button)
        elif button == 1:
            self._explore_click(pos)

    def _explore_click(self, pos):
        target = self.entity_at_screen(pos)
        if target in self.npcs:
            self._go_next_to(tile_of(target), lambda: self._talk_when_near(target))
        elif target is not None and target.talk and not target.hostile:
            self._go_next_to(tile_of(target), lambda: self.talk_to(target, target.talk)
                             if self.player.rect.inflate(60, 60).colliderect(target.rect) else None)
        elif target is not None:
            self._attack_from_explore(target)
        else:
            tile = self.tile_at_screen(pos)
            obj = self.object_at_screen(pos)
            if obj:
                kind, what = obj
                if kind == "pickup":
                    t = (what["rect"].x // T, what["rect"].y // T)
                    self._go_to(lambda c: chebyshev(c, t) <= 1,
                                lambda: self.level.take_pickup(what, self.inventory, log_fn=self.log))
                elif kind in ("container", "terminal"):
                    tiles = what["tiles"]
                    action = (lambda: self.open_container(what)) if kind == "container" else \
                        (lambda: self.open_terminal(what["id"]))
                    self._go_to(lambda c: c not in tiles and any(chebyshev(c, t) <= 1 for t in tiles), action)
                else:
                    self._go_next_to(what, lambda: self.open_door(what))
            elif not self.level.is_wall(*tile):
                self._go_to(lambda c: c == tile)

    def _talk_when_near(self, npc, tries=3):
        """NPC мог отойти, пока мы шли, — догоняем (несколько раз) и заговариваем."""
        if self.player.rect.inflate(60, 60).colliderect(npc.rect):
            self.talk_to(npc, npc.npc_id)
        elif tries > 0:
            self._go_next_to(tile_of(npc), lambda: self._talk_when_near(npc, tries - 1))

    def _attack_from_explore(self, enemy):
        if self.combat.start(player_first=True):
            if enemy in self.combat.enemies_in_combat():
                self.combat.target = enemy
            return
        self._go_next_to(tile_of(enemy), lambda: self._attack_from_explore(enemy)
                         if enemy.alive and not self.combat.active else None)

    # ---------------------------------------------- ходьба по клику вне боя
    def _explore_path(self, done):
        """BFS по клеткам без стен (NPC не мешают — сквозь них можно пройти)."""
        start = tile_of(self.player)
        q, prev = deque([start]), {start: None}
        while q:
            c = q.popleft()
            if done(c):
                path = []
                while c != start:
                    path.append(c)
                    c = prev[c]
                return path[::-1]
            for dx, dy in NEIGHBORS:
                n = (c[0] + dx, c[1] + dy)
                if n not in prev and not self.level.is_wall(*n):
                    prev[n] = c
                    q.append(n)
        return None

    def _go_to(self, done, then=None):
        path = self._explore_path(done)
        if path is None:
            self.log("Туда не пройти.")
            self.autowalk = None
            return
        # сначала встать ровно в свою клетку — иначе можно зацепиться за угол стены
        self.autowalk = {"path": [tile_of(self.player)] + path, "then": then, "stuck_ms": 0}

    def _go_next_to(self, tile, then):
        """Подойти вплотную (в том числе по диагонали) к клетке и сделать then()."""
        self._go_to(lambda c: c != tile and chebyshev(c, tile) <= 1, then)

    def _finish_autowalk(self):
        then = self.autowalk["then"] if self.autowalk else None
        self.autowalk = None
        self.player.anim.set_action("idle")
        if then:
            then()

    def update_autowalk(self, dt_ms):
        """Шаг автоходьбы. True — герой идёт по клику (клавиши движения его прерывают)."""
        aw = self.autowalk
        if not aw:
            return False
        if not aw["path"]:
            self._finish_autowalk()
            return False
        p = self.player
        target = pygame.Vector2(rect_pos_for_tile(p, aw["path"][0]))
        delta = target - pygame.Vector2(p.rect.topleft)
        step = S.PLAYER_SPEED * dt_ms / 1000

        def axis(d):  # целые пиксели, но не застревать на остатке меньше пикселя
            if abs(d) <= step:
                return int(round(d))
            return int(round(step)) * (1 if d > 0 else -1)

        before = p.rect.topleft
        p.walk(axis(delta.x), axis(delta.y), self.level.solids_near(p.rect))
        if p.rect.topleft == tuple(int(v) for v in target):
            aw["path"].pop(0)
            aw["stuck_ms"] = 0
        elif p.rect.topleft == before:
            aw["stuck_ms"] += dt_ms
            if aw["stuck_ms"] > 400:
                self.autowalk = None
                p.anim.set_action("idle")
        return True

    # ------------------------------------------------------------- бой
    def _combat_click(self, pos, button):
        c = self.combat
        if not c.player_can_act():
            return
        target = self.entity_at_screen(pos)
        barrel = self.barrel_at_screen(pos) if target is None else None
        if barrel is not None and button == 1:
            c.player_shoot_barrel(barrel)
            return
        if target in self.enemies and target.alive:
            if target not in c.enemies_in_combat():
                return
            c.target = target
            if button == 3:
                c.aim_menu = True
                return
            ok, reason = c.can_attack(self.player, target)
            if ok:
                c.player_attack(0)
            elif reason == "подойдите вплотную":
                goal = tile_of(target)
                path = c.find_path(self.player, lambda t: chebyshev(t, goal) == 1)
                if path is None:
                    self.log("К цели не подобраться.")
                else:
                    self.combat_queue = {"path": path, "attack": target}
            else:
                self.log(f"Атаковать нельзя: {reason}.")
        elif button == 1 and target is None:
            tile = self.tile_at_screen(pos)
            path = self.combat_path_to(tile)
            if path:
                self.combat_queue = {"path": path, "attack": None}

    def combat_path_to(self, tile):
        if self.combat.game.level.is_wall(*tile):
            return None
        return self.combat.find_path(self.player, lambda t: t == tile)

    def run_combat_queue(self):
        """Выполняет по шагу за раз путь, заданный кликом, и удар в конце."""
        q, c = self.combat_queue, self.combat
        if not q:
            return
        if not c.active or not c.is_player_turn():
            self.combat_queue = None
            return
        if not c.player_can_act() or c.aim_menu:
            return
        p = self.player
        if q["path"]:
            nxt = q["path"].pop(0)
            cur = tile_of(p)
            if not c.try_step(p, nxt[0] - cur[0], nxt[1] - cur[1]):
                if not c._can_pay_step(p):
                    self.log("Не хватает ОД, чтобы дойти. R — конец хода.")
                self.combat_queue = None
        elif q["attack"] is not None:
            if q["attack"].alive:
                c.target = q["attack"]
                c.player_attack(0)
            self.combat_queue = None
        else:
            self.combat_queue = None

    # ---------------------------------------------------- подсказка курсора
    def hover_highlight(self):
        """Что обвести контуром под курсором: [(картинка, rect на экране)]."""
        pos = pygame.mouse.get_pos()
        if (self.mode != "local" or self.modal_open() or self.game_over or self.combat.active
                or over_ui(pos) or not pygame.mouse.get_focused()):
            return []
        cam_x, cam_y = int(self.cam.x), int(self.cam.y)
        target = self.entity_at_screen(pos)
        if target is not None and (target in self.npcs or (target.talk and not target.hostile)):
            frame, r = sprite_of(target, self.cam)
            return [(frame, r)]
        obj = self.object_at_screen(pos)
        if not obj:
            return []
        kind, what = obj
        if kind == "pickup":
            icon = loader.item_icon(what["kind"])
            r = self.level.pickup_icon_rect(what).move(-cam_x, -cam_y)
            return [(icon, r)]
        if kind == "container" and what.get("corpse"):
            return [(what["corpse"]["img"], what["corpse"]["rect"].move(-cam_x, -cam_y))]
        if kind in ("container", "terminal") and what.get("obj"):
            o = what["obj"]
            img = P.image(o["name"])
            return [(img, o["rect"].move(-cam_x, -cam_y))]
        tile = what["tiles"][0] if kind in ("container", "terminal") else what
        ch = {"container": "X", "terminal": "%", "door": "D"}[kind]
        img = loader.special_tile(ch)
        return [(img, img.get_rect(topleft=(tile[0] * T - cam_x, tile[1] * T - cam_y)))]

    def cursor_hint(self):
        """Что показать у курсора: (текст, цвет, путь [клетки] или None, клетка под курсором)."""
        pos = pygame.mouse.get_pos()
        if self.mode != "local" or self.modal_open() or self.game_over or over_ui(pos):
            return None
        if not pygame.mouse.get_focused():
            return None
        c, p = self.combat, self.player
        target = self.entity_at_screen(pos)
        tile = self.tile_at_screen(pos)
        if c.active:
            if not c.player_can_act() or c.aim_menu:
                return None
            if target in self.enemies and target in c.enemies_in_combat():
                ok, reason = c.can_attack(p, target)
                cost = c.attack_cost(p)
                if ok:
                    enough = p.ap >= cost
                    return (f"{target.name}: {c.hit_chance(p, target)}% · {cost} ОД",
                            (230, 220, 190) if enough else (230, 90, 70), None, None)
                return (f"{target.name}: {reason}", (170, 160, 140), None, None)
            if target is None:
                path = self.combat_path_to(tile)
                if path:
                    can = p.ap + p.free_steps
                    color = (130, 230, 120) if len(path) <= can else (230, 90, 70)
                    return (f"{len(path)} ОД", color, path, tile)
            return None
        if target in self.npcs:
            return (f"Говорить: {target.name}", (230, 220, 190), None, None)
        if target is not None and target.talk and not target.hostile:
            return (f"Говорить: {target.name}", (230, 220, 190), None, None)
        if target is not None:
            return (f"Напасть: {target.name}", (235, 120, 100), None, None)
        obj = self.object_at_screen(pos)
        if obj:
            kind, what = obj
            if kind == "container" and what.get("corpse"):
                label = f"Обыскать тело: {what['who']}"
            elif kind == "container":
                label = f"Обыскать: {what['name']}"
            elif kind == "pickup":
                label = f"Подобрать: {what['kind']}" + (f" ×{what['count']}" if what["count"] > 1 else "")
            elif kind == "terminal":
                label = "Читать: доска объявлений" if what["id"].startswith("doc:") else "Терминал RobCo"
            else:
                label = "Дверь: заперта"
            return (label, (230, 220, 190), None, None)
        if not self.level.is_wall(*tile):
            return ("", None, None, tile)
        return None
