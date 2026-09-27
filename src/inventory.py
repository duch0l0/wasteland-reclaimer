"""Инвентарь и крафт из подобранных на уровне ресурсов."""
import json


class Inventory:
    def __init__(self, recipes_path):
        self.items = {}  # name -> count
        with open(recipes_path, "r", encoding="utf-8") as f:
            self.recipes = json.load(f)

    def add(self, name, count=1):
        self.items[name] = self.items.get(name, 0) + count

    def has(self, name, count=1):
        return self.items.get(name, 0) >= count

    def remove(self, name, count=1):
        self.items[name] = max(0, self.items.get(name, 0) - count)

    def count(self, name):
        return self.items.get(name, 0)

    def nonzero(self):
        return {k: v for k, v in self.items.items() if v > 0}

    def can_craft(self, recipe_id):
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return False
        if recipe.get("unique") and self.has(recipe["result"]):
            return False
        return all(self.has(ing, need) for ing, need in recipe["ingredients"].items())

    def craft(self, recipe_id):
        if not self.can_craft(recipe_id):
            return None
        recipe = self.recipes[recipe_id]
        for ing, need in recipe["ingredients"].items():
            self.remove(ing, need)
        self.add(recipe["result"], recipe.get("result_count", 1))
        return recipe

    def craftable_ids(self):
        return [rid for rid in self.recipes if self.can_craft(rid)]
