"""Торговля с NPC (data/traders.json). Цены — из data/items.json."""
import math

import pygame

from .. import items
from ..weapons import weapon_for_item
from .controls import number_key

SELL_RATE = 0.5          # торговец покупает за полцены
SILVER_TONGUE_BONUS = 0.2
RESTOCK_MS = 8 * 60 * 1000   # через столько игрового времени торговец пополняет товар и кассу


def speech_mult(speech):
    """Красноречие торгуется: при 20 — покупка +10%, продажа ×0.9; при 100 — покупка −10%, продажа ×1.1."""
    k = max(-1.0, min(1.0, (speech - 60) / 40))
    return 1 - 0.1 * k, 1 + 0.1 * k


def _packed(name):
    """Мелочь продаётся пачками по 5: патроны, дробь, ячейки, топливо, метательные ножи."""
    return (items.category(name) == "ammo" and items.price(name) <= 6) or name == "метательный нож"


class TradeMixin:
    def open_trade(self, trader_id):
        if self.flags.get(f"{trader_id}_robbed"):
            self.log(f"{self.traders[trader_id]['name']} демонстративно прячет товар за спину.")
            return
        self._restock(trader_id)
        self.trade = {"id": trader_id, "tab": "buy"}

    def _restock(self, trader_id):
        """Прошло время — у торговца снова есть ходовой товар и касса (не больше, чем было изначально)."""
        import json
        tr = self.traders[trader_id]
        last = tr.get("restocked_ms", 0)
        if self.play_ms - last < RESTOCK_MS and last:
            return
        tr["restocked_ms"] = self.play_ms
        if not hasattr(self, "_traders_base"):
            with open("data/traders.json", encoding="utf-8") as f:
                self._traders_base = json.load(f)
        base = self._traders_base.get(trader_id)
        if not base:
            return
        tr["cash"] = max(tr["cash"], base["cash"])
        for name, qty in base["stock"].items():
            if items.ITEMS.get(name, {}).get("cat") in ("ammo", "meds") or name in (
                    "отмычка", "изолента", "пружина", "метательный нож", "граната"):
                tr["stock"][name] = max(tr["stock"].get(name, 0), qty)

    def trade_rows(self):
        """Строки текущей вкладки: (предмет, сколько за раз, цена за раз, в наличии)."""
        tr = self.traders[self.trade["id"]]
        silver = self.player.perk_rank("silver_tongue")
        buy_k, sell_k = speech_mult(self.player.skill("speech"))
        rows = []
        if self.trade["tab"] == "buy":
            for name, have in tr["stock"].items():
                if have <= 0:
                    continue
                qty = min(5, have) if _packed(name) else 1  # патроны — пачками
                mult = (1 - SILVER_TONGUE_BONUS if silver else 1) * buy_k
                rows.append((name, qty, max(1, math.ceil(items.price(name) * qty * mult)), have))
        else:
            for name, have in self.inventory.nonzero().items():
                base = items.price(name)
                if name == "крышки" or base <= 0:
                    continue
                qty = min(5, have) if _packed(name) else 1
                mult = SELL_RATE * (1 + SILVER_TONGUE_BONUS if silver else 1) * sell_k
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
            self.log(f"Не хватает крышек. {tr['name']} сочувственно кивает, но скидку не даёт.")
            return
        self.inventory.remove("крышки", price)
        tr["cash"] += price
        tr["stock"][name] -= qty
        self.inventory.add(name, qty)
        self.log(f"Куплено: {name} ×{qty} за {price} кр.")

    def _sell(self, name, qty, price):
        tr = self.traders[self.trade["id"]]
        if tr["cash"] < price:
            self.log(f"У торговца ({tr['name']}) кончились крышки. Предлагает расписку. Вы отказываетесь.")
            return
        tr["cash"] -= price
        tr["stock"][name] = tr["stock"].get(name, 0) + qty
        self.inventory.remove(name, qty)
        self.inventory.add("крышки", price)
        if weapon_for_item(name) == self.player.weapon and not self.inventory.has(name):
            self.player.weapon = "melee"
        self.log(f"Продано: {name} ×{qty} за {price} кр.")
