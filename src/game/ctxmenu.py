"""
Меню действий по ПКМ, как в Fallout 2: правой кнопкой по жителю, врагу, ящику, телу, предмету,
терминалу или двери — список того, что с ним можно сделать. Вне боя; в бою ПКМ по врагу —
прицельная атака, как раньше. Выбор — клик или цифра, Esc или клик мимо — закрыть.

  житель   Говорить · Осмотреть · Обокрасть (Ловкость рук N) · Напасть
  враг     Напасть · Осмотреть (· Говорить, если с ним можно говорить)
  ящик     Обыскать · Осмотреть (чужое ли, заперто ли)
  предмет  Подобрать · Осмотреть
  терминал Включить / Читать;  дверь — Открыть
"""
import random

from .. import items
from ..combat import tile_of, chebyshev
from ..settings import TILE as T
from .mouse import threat_name


class CtxMenuMixin:
    def open_ctx_menu(self, pos):
        """ПКМ вне боя: собрать действия для того, что под курсором. False — там ничего нет."""
        target = self.entity_at_screen(pos)
        acts = []
        if target in self.npcs:
            npc = target
            title = npc.name
            acts = [("Говорить", lambda: self._go_next_to(tile_of(npc), lambda: self._talk_when_near(npc))),
                    ("Осмотреть", lambda: self.look_at_npc(npc)),
                    (f"Обокрасть  (Ловкость рук {self.player.skill('steal')})",
                     lambda: self._go_next_to(tile_of(npc), lambda: self.pickpocket(npc) if npc in self.npcs else None)),
                    ("Напасть", lambda: self._go_next_to(tile_of(npc), lambda: self.attack_npc(npc) if npc in self.npcs else None))]
        elif target is not None:
            enemy = target
            title = threat_name(enemy, self.player)
            if enemy.talk and not enemy.hostile:
                acts.append(("Говорить", lambda: self._go_next_to(tile_of(enemy), lambda: self.talk_to(enemy, enemy.talk)
                             if self.player.rect.inflate(60, 60).colliderect(enemy.rect) else None)))
            acts += [("Напасть", lambda: self._attack_from_explore(enemy)),
                     ("Осмотреть", lambda: self.log(f"{title}. HP {enemy.hp}/{enemy.max_hp}"
                                                     + (f", панцирь гасит {enemy.armor} урона" if enemy.armor else "")
                                                     + ("." if enemy.hostile else ". Пока не нападает.")))]
        else:
            obj = self.object_at_screen(pos)
            if not obj:
                return False
            kind, what = obj
            if kind == "pickup":
                title = what["kind"]
                t = (what["rect"].x // T, what["rect"].y // T)
                desc = items.ITEMS.get(what["kind"], {}).get("desc", "Ничего особенного.")
                acts = [("Подобрать", lambda: self._go_to(lambda c: chebyshev(c, t) <= 1,
                                                          lambda: self.level.take_pickup(what, self.inventory, log_fn=self.log))),
                        ("Осмотреть", lambda: self.log(f"{title[:1].upper() + title[1:]}: {desc}"))]
            elif kind in ("container", "terminal"):
                tiles = what["tiles"]
                near = lambda c: c not in tiles and any(chebyshev(c, t) <= 1 for t in tiles)
                if kind == "container":
                    title = f"тело: {what['who']}" if what.get("corpse") else what["name"]
                    acts = [("Обыскать", lambda: self._go_to(near, lambda: self.open_container(what))),
                            ("Осмотреть", lambda: self.look_at_box(what))]
                else:
                    doc = what["id"].startswith("doc:")
                    title = "доска объявлений" if doc else "терминал RobCo"
                    acts = [("Читать" if doc else "Включить", lambda: self._go_to(near, lambda: self.open_terminal(what["id"])))]
            else:
                title = "дверь"
                acts = [("Открыть", lambda: self._go_next_to(what, lambda: self.open_door(what)))]
        self.ctx_menu = {"pos": pos, "title": title[:1].upper() + title[1:], "items": acts}
        return True

    def ctx_choose(self, i):
        menu, self.ctx_menu = self.ctx_menu, None
        if menu and 0 <= i < len(menu["items"]):
            menu["items"][i][1]()

    def ctx_key(self, key):
        import pygame
        if pygame.K_1 <= key <= pygame.K_9:
            self.ctx_choose(key - pygame.K_1)
        elif key in (pygame.K_ESCAPE, pygame.K_SPACE):
            self.ctx_menu = None

    # ------------------------------------------------------------ «Осмотреть»
    def look_at_npc(self, npc):
        lines = self.bark_lines(npc)
        if lines:   # житель бормочет что-то своё — облачко над головой
            self.speech = {"ent": npc, "text": random.choice(lines), "t": 3200}
        p = self.player.skill("steal")
        mood = ("держит руку на кармане и не сводит с вас глаз" if self.flags.get(f"{npc.npc_id}_robbed")
                else "занят своим делом")
        self.log(f"{npc.name}: {mood}. Карманы — ПКМ → «Обокрасть» или K рядом (Ловкость рук {p}).")

    def look_at_box(self, box):
        if box.get("corpse"):
            self.log(f"Тело: {box['who']}. Обыскать — ПКМ → «Обыскать» или E рядом.")
            return
        note = box["name"][:1].upper() + box["name"][1:] + "."
        if box.get("owner"):
            note += " Чужое: возьмёте при хозяине — заметит."
        req = box.get("requires")
        if req and not self.check_condition(req):
            note += " " + req.get("msg", "Заперто.")
        self.log(note)
