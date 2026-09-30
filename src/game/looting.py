"""
Обыск в два окна, как в Fallout: слева рюкзак, справа контейнер (ящик,
шкаф, тело). Вещи переносятся в обе стороны: взять, положить, взять всё.

Кража засчитывается не при открытии, а при первой взятой вещи: у Гены —
он узнает; у банды — если кто-то из неё видит вора, будет драка.
"""
import pygame

from .. import items
from ..weapons import weapon_for_item
from .controls import number_key

COLS = 6


class LootingMixin:
    def open_container(self, c):
        req = c.get("requires")
        if req and not self.check_condition(req):
            self.log(req.get("msg", f"{c['name'].capitalize()}: заперто."))
            return
        first = not c["opened"]
        c["opened"] = True
        self.audio.play("open")
        self.autowalk = None
        self.loot = {"box": c, "side": "box" if c["loot"] else "me", "sel": 0, "stolen_checked": False}
        if first and not c["loot"]:
            self.log(f"{c['name'][:1].upper() + c['name'][1:]}: пусто. Кто-то успел раньше.")

    def close_loot(self):
        if self.loot:
            self.audio.play("close")
        self.loot = None

    # ------------------------------------------------------------ списки
    def loot_list(self, side):
        """Предметы стороны в порядке показа: крышки первыми, дальше по категориям."""
        src = self.loot["box"]["loot"] if side == "box" else self.inventory.items
        order = {c: i for i, c in enumerate(items.CATEGORY_ORDER)}
        names = [n for n, v in src.items() if v > 0]
        return sorted(names, key=lambda n: (n != "крышки", order.get(items.category(n), 99), n))

    def loot_count(self, side, name):
        src = self.loot["box"]["loot"] if side == "box" else self.inventory.items
        return src.get(name, 0)

    # ------------------------------------------------------------ перенос
    def loot_take(self, name, count=None):
        box = self.loot["box"]
        have = box["loot"].get(name, 0)
        if have <= 0:
            return
        if not self._theft_check(box):
            return
        n = have if count is None else min(count, have)
        box["loot"][name] = have - n
        if box["loot"][name] <= 0:
            del box["loot"][name]
        self.inventory.add(name, n)
        self.audio.play("pickup")
        self.log(f"Взято: {name}" + (f" ×{n}" if n > 1 else ""))

    def loot_put(self, name, count=None):
        have = self.inventory.count(name)
        if have <= 0:
            return
        n = have if count is None else min(count, have)
        self.inventory.remove(name, n)
        box = self.loot["box"]
        box["loot"][name] = box["loot"].get(name, 0) + n
        if weapon_for_item(name) == self.player.weapon and not self.inventory.has(name):
            self.player.weapon = "melee"
        self.log(f"Положено: {name}" + (f" ×{n}" if n > 1 else "") + f" ({box['name']})")
        hook = box.get("on_put")
        if hook and hook["item"] == name:   # сюжетный тайник: положил нужное — что-то случилось
            box["on_put"] = None
            self.close_loot()
            for eff in hook["effects"]:
                self.apply_effect(eff)

    def loot_take_all(self):
        for name in list(self.loot_list("box")):
            if not self.loot:
                return  # кражу заметили — окно закрылось
            self.loot_take(name)

    def loot_click(self, side, name):
        """ЛКМ — вся стопка, ПКМ — одна штука."""
        count = 1 if getattr(self, "last_button", 1) == 3 else None
        self.loot["side"] = side
        (self.loot_take if side == "box" else self.loot_put)(name, count)

    def _theft_check(self, box):
        """Чужое брать — с последствиями. False — брать нельзя (началась драка)."""
        if self.loot.get("stolen_checked"):
            return True
        self.loot["stolen_checked"] = True
        owner = box.get("owner")
        npc = next((n for n in self.npcs if n.npc_id == owner), None) if owner else None
        if npc is not None:
            p = self.player
            sees = (pygame.Vector2(npc.rect.center).distance_to(p.rect.center) <= 6 * 48
                    and self.combat.los(npc, p))
            if owner == "gena" or sees:   # Гена всё видит — у него на всё свои глаза
                self.flags[f"{owner}_robbed"] = True
                self.log(f"Вы чувствуете на спине чей-то взгляд... {npc.name} это так не оставит.")
            else:
                self.log("Кажется, никто не заметил.")
        elif owner and self.loc.faction_members(owner):
            p = self.player
            seen = [e for e in self.loc.faction_members(owner)
                    if pygame.Vector2(e.rect.center).distance_to(p.rect.center) <= e.aggro and self.combat.los(e, p)]
            if not seen:
                self.log("Кажется, никто не заметил.")
                return True
            self.log(f"{seen[0].name.capitalize()}: Эй! Это наше!")
            self.make_hostile(owner)
            self.close_loot()
            self.combat.start(player_first=False)
            return False
        return True

    # ------------------------------------------------------------ клавиши
    def loot_key(self, key):
        L = self.loot
        if key in (pygame.K_ESCAPE, pygame.K_i):
            self.close_loot()
            return
        if key == pygame.K_r:
            self.loot_take_all()
            return
        if key == pygame.K_TAB:
            L["side"] = "me" if L["side"] == "box" else "box"
            L["sel"] = 0
            return
        names = self.loot_list(L["side"])
        moves = {pygame.K_LEFT: -1, pygame.K_a: -1, pygame.K_RIGHT: 1, pygame.K_d: 1,
                 pygame.K_UP: -COLS, pygame.K_w: -COLS, pygame.K_DOWN: COLS, pygame.K_s: COLS}
        if key in moves and names:
            L["sel"] = max(0, min(len(names) - 1, L["sel"] + moves[key]))
        elif key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE) and names:
            name = names[min(L["sel"], len(names) - 1)]
            (self.loot_take if L["side"] == "box" else self.loot_put)(name)
        else:
            idx = number_key(key)
            if idx is not None and idx < len(names):
                (self.loot_take if L["side"] == "box" else self.loot_put)(names[idx])
