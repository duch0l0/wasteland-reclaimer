"""Крафт и использование предметов из рюкзака (в бою — за ОД)."""
import pygame

from .. import settings as S
from .. import items
from .controls import number_key


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
        if recipe.get("effect", {}).get("type") == "damage_buff":
            self.player.base_damage += recipe["effect"]["amount"]
        self.log(f"Скрафтено: {recipe['name']}")

    def usable_items(self):
        return [n for n in self.inventory.nonzero() if items.usable(n)]

    def inventory_key(self, key):
        if key == pygame.K_i:
            self.inv_open = False
            return
        idx = number_key(key)
        usable = self.usable_items()
        if idx is not None and idx < len(usable):
            self.use_item(usable[idx])

    def use_item(self, name):
        if self.player.hp >= self.player.max_hp:
            self.log("Вы и так целы. Не переводите добро.")
            return
        if not self.combat.spend_player_ap(S.AP_CRAFT):
            return
        use = items.ITEMS[name]["use"]
        before = self.player.hp
        if use.get("heal_full"):
            self.player.hp = self.player.max_hp
        else:
            self.player.hp = min(self.player.max_hp, self.player.hp + use.get("heal", 0))
        self.inventory.remove(name)
        self.log(f"Использовано: {name} (+{self.player.hp - before} HP).")
        if self.combat.active:
            self.inv_open = False
