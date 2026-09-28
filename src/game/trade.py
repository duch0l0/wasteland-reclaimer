"""Торговля с NPC (data/traders.json). Цены — из data/items.json."""
import math

import pygame

from .. import items
from ..weapons import weapon_for_item
from .controls import number_key

SELL_RATE = 0.5          # торговец покупает за полцены
SILVER_TONGUE_BONUS = 0.2


class TradeMixin:
    def open_trade(self, trader_id):
        if trader_id == "gena" and self.flags.get("gena_robbed"):
            self.log("Гена демонстративно прячет товар за спину.")
            return
        self.trade = {"id": trader_id, "tab": "buy"}

    def trade_rows(self):
        """Строки текущей вкладки: (предмет, сколько за раз, цена за раз, в наличии)."""
        tr = self.traders[self.trade["id"]]
        silver = self.player.perk_rank("silver_tongue")
        rows = []
        if self.trade["tab"] == "buy":
            for name, have in tr["stock"].items():
                if have <= 0:
                    continue
                qty = min(5, have) if name == "патроны" else 1  # патроны — пачками
                mult = 1 - SILVER_TONGUE_BONUS if silver else 1
                rows.append((name, qty, max(1, math.ceil(items.price(name) * qty * mult)), have))
        else:
            for name, have in self.inventory.nonzero().items():
                base = items.price(name)
                if name == "крышки" or base <= 0:
                    continue
                qty = min(5, have) if name == "патроны" else 1
                mult = SELL_RATE * (1 + SILVER_TONGUE_BONUS if silver else 1)
                rows.append((name, qty, max(1, int(base * qty * mult)), have))
        return rows

    def trade_key(self, key):
        if key == pygame.K_TAB:
            self.trade["tab"] = "sell" if self.trade["tab"] == "buy" else "buy"
            return
        idx = number_key(key)
        rows = self.trade_rows()
        if idx is None or idx >= len(rows):
            return
        name, qty, price, _ = rows[idx]
        if self.trade["tab"] == "buy":
            self._buy(name, qty, price)
        else:
            self._sell(name, qty, price)

    def _buy(self, name, qty, price):
        tr = self.traders[self.trade["id"]]
        if not self.inventory.has("крышки", price):
            self.log("Не хватает крышек. Гена сочувственно кивает, но скидку не даёт.")
            return
        self.inventory.remove("крышки", price)
        tr["cash"] += price
        tr["stock"][name] -= qty
        self.inventory.add(name, qty)
        self.log(f"Куплено: {name} ×{qty} за {price} кр.")

    def _sell(self, name, qty, price):
        tr = self.traders[self.trade["id"]]
        if tr["cash"] < price:
            self.log("У Гены кончились крышки. Он предлагает расписку. Вы отказываетесь.")
            return
        tr["cash"] -= price
        tr["stock"][name] = tr["stock"].get(name, 0) + qty
        self.inventory.remove(name, qty)
        self.inventory.add("крышки", price)
        if weapon_for_item(name) == self.player.weapon and not self.inventory.has(name):
            self.player.weapon = "melee"
        self.log(f"Продано: {name} ×{qty} за {price} кр.")
