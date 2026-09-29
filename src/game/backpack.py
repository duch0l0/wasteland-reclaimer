"""Крафт и использование предметов из рюкзака (в бою — за ОД)."""
import pygame

from .. import settings as S
from .. import items
from .controls import number_key
from ..weapons import weapon_for_item
from ..ui.inventory_ui import COLS as INV_COLS  # ячеек в ряду сетки рюкзака



class BackpackMixin:
    def craft_key(self, key):
        if key == pygame.K_c:
            self.craft_open = False
            return
        idx = number_key(key)
        ids = list(self.inventory.recipes.keys())
        if idx is None or idx >= len(ids):
            return
        rid = ids[idx]
        recipe = self.inventory.recipes[rid]
        if recipe.get("unique") and self.inventory.has(recipe["result"]):
            self.log("Это уже сделано — второй раз не выйдет.")
            return
        if not self.inventory.can_craft(rid):
            self.log("Не хватает ресурсов для этого рецепта.")
            return
        if not self.combat.spend_player_ap(S.AP_CRAFT):
            return
        self.inventory.craft(rid)
        self.log(f"Скрафтено: {recipe['name']}")

    # ---------------------------------------------------------- рюкзак
    def inventory_items(self):
        """Предметы текущей вкладки в порядке показа (крышки — отдельно, не в сетке)."""
        cats = dict((tid, c) for tid, _, c in items.CATEGORY_TABS)[self.inv_tab]
        names = [n for n in self.inventory.nonzero() if n != "крышки"
                 and (cats is None or items.category(n) in cats)]
        order = {c: i for i, c in enumerate(items.CATEGORY_ORDER)}
        return sorted(names, key=lambda n: (order.get(items.category(n), 99), n))

    def open_inventory(self):
        self.inv_open = True
        visible = self.inventory_items()
        if self.inv_sel not in visible:
            self.inv_sel = visible[0] if visible else None

    def usable_items(self):
        return [n for n in self.inventory.nonzero() if items.usable(n)]

    # ------------------------------------------------------ снаряжение
    def equip(self, name):
        slot = items.slot(name)
        if not slot or not self.inventory.has(name):
            return
        if self.combat.active:
            self.log("Переодеваться посреди драки — плохая идея. Сначала закончите бой.")
            return
        old = self.player.equipped(slot)
        self.player.equipment[slot] = name
        self.log(f"Надето: {name}" + (f" (вместо: {old})." if old else "."))

    def unequip(self, slot):
        name = self.player.equipped(slot)
        if not name:
            return
        if self.combat.active:
            self.log("Раздеваться посреди драки — ещё более плохая идея.")
            return
        self.player.equipment[slot] = None
        self.log(f"Снято: {name}.")

    def on_item_added(self, name, count):
        """Новая броня сама надевается в пустой слот (снять/поменять — в рюкзаке).
        Сюжетные предметы двигают квесты."""
        if hasattr(self, "quests"):
            self.sync_story()
        slot = items.slot(name)
        if slot and not self.player.equipped(slot) and not self.combat.active:
            self.player.equipment[slot] = name
            self.log(f"Вы сразу надеваете: {name}. Поменять можно в рюкзаке (I).")

    def item_action(self, name):
        """Главное действие с предметом: (подпись, функция) или None."""
        if name is None or not self.inventory.has(name):
            return None
        doc = items.ITEMS.get(name, {}).get("read")
        if doc:
            from .terminals import DOCS
            verb = "Прослушать" if DOCS[doc].get("kind") == "holotape" else "Читать"
            return (verb, lambda: self.open_document(doc))
        slot = items.slot(name)
        if slot:
            worn = self.player.equipped(slot)
            if worn == name:
                return ("Снять", lambda: self.unequip(slot))
            return (f"Надеть вместо: {worn}" if worn else "Надеть", lambda: self.equip(name))
        if items.usable(name):
            cost = f" ({S.AP_CRAFT} ОД)" if self.combat.active else ""
            return (f"Использовать{cost}", lambda: self.use_item(name))
        gun = weapon_for_item(name)
        if gun:
            if self.player.weapon == gun:
                return ("Убрать (взять лом)", lambda: self.switch_weapon("melee"))
            return ("Взять в руки", lambda: self.switch_weapon(gun))
        if name in ("лом", "заточенный лом") and self.player.weapon != "melee":
            return ("Взять в руки", lambda: self.switch_weapon("melee"))
        return None

    def inv_click(self, name):
        """Клик по ячейке: выбрать; повторный клик по той же ячейке (двойной) — действие."""
        now = pygame.time.get_ticks()
        if self.inv_sel == name and now - self.inv_last_click < 400:
            action = self.item_action(name)
            if action:
                action[1]()
        self.inv_sel = name
        self.inv_last_click = now

    def inv_set_tab(self, tab_id):
        self.inv_tab = tab_id
        visible = self.inventory_items()
        if self.inv_sel not in visible:
            self.inv_sel = visible[0] if visible else None

    def inventory_key(self, key):
        if key == pygame.K_i:
            self.inv_open = False
            return
        tabs = [t for t, _, _ in items.CATEGORY_TABS]
        if key == pygame.K_TAB:
            self.inv_set_tab(tabs[(tabs.index(self.inv_tab) + 1) % len(tabs)])
            return
        if key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            action = self.item_action(self.inv_sel)
            if action:
                action[1]()
            return
        moves = {pygame.K_LEFT: -1, pygame.K_a: -1, pygame.K_RIGHT: 1, pygame.K_d: 1,
                 pygame.K_UP: -INV_COLS, pygame.K_w: -INV_COLS, pygame.K_DOWN: INV_COLS, pygame.K_s: INV_COLS}
        visible = self.inventory_items()
        if key in moves and visible:
            i = visible.index(self.inv_sel) if self.inv_sel in visible else 0
            j = i + moves[key]
            if 0 <= j < len(visible):
                self.inv_sel = visible[j]
            return
        # цифры — быстро применить лечилку, как раньше
        idx = number_key(key)
        usable = self.usable_items()
        if idx is not None and idx < len(usable):
            self.use_item(usable[idx])

    def use_item(self, name):
        use = items.ITEMS[name]["use"]
        p = self.player
        if "rads" in use:
            if p.rads <= 0:
                self.log("Радиации в вас нет. Пока.")
                return
        elif p.hp >= p.hp_cap:
            self.log("Вы и так целы. Не переводите добро." if p.hp_cap == p.max_hp else
                     "Раны затянуты, но радиация съела часть здоровья — тут поможет антирадин у Дока.")
            return
        if not self.combat.spend_player_ap(S.AP_CRAFT):
            return
        before = p.hp
        if "rads" in use:
            was = p.rads
            p.add_rads(use["rads"])
            self.inventory.remove(name)
            self.log(f"Использовано: {name} (−{was - p.rads} рад).")
        else:
            if use.get("heal_full"):
                p.hp = p.hp_cap
            else:
                p.hp = min(p.hp_cap, p.hp + use.get("heal", 0))
            p.dots = [d for d in p.dots if d["kind"] != "poison"]   # лекарство снимает яд
            self.inventory.remove(name)
            self.log(f"Использовано: {name} (+{p.hp - before} HP).")
        if not self.inventory.has(name):
            visible = self.inventory_items()
            self.inv_sel = visible[0] if visible else None
        if self.combat.active:
            self.inv_open = False
