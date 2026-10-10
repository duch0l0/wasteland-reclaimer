"""
Игровое время (docs/city_plan.md, этап 4). В городе 1 секунда — 1 игровая минута (сутки — 24 минуты), на карте
мира время бежит по расстоянию: 1,5 минуты на единицу пути (до соседнего города — полдня). Время — в флаге
time_min (минуты с начала игры; старт — день 1, понедельник, 8:00), поэтому живёт в сохранениях.

Медленные последствия — data/deadlines.json: квест начат — через N дней, если герой не успел, мир решает сам.
Журнал показывает, сколько осталось. Условия диалогов и изменений городов знают «ночь» и день недели.
"""
import json

with open("data/deadlines.json", encoding="utf-8") as _f:
    DEADLINES = {k: v for k, v in json.load(_f).items() if not k.startswith("_")}
START_MIN = 8 * 60
DAY = 24 * 60
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
MAP_MIN_PER_UNIT = 1.5


class ClockMixin:
    @property
    def time_min(self):
        return self.flags.get("time_min", START_MIN)

    def advance_time(self, minutes):
        self.flags["time_min"] = self.time_min + minutes
        self._clock_acc = 0.0
        self.check_deadlines()

    def tick_clock(self, dt_ms):
        """Локально: 1 с = 1 мин; набираем дробные минуты, чтобы не терять."""
        self._clock_acc = getattr(self, "_clock_acc", 0.0) + dt_ms / 1000
        if self._clock_acc >= 1:
            whole = int(self._clock_acc)
            self._clock_acc -= whole
            self.flags["time_min"] = self.time_min + whole
            if self.time_min // 60 != (self.time_min - whole) // 60:   # раз в игровой час
                self.check_deadlines()

    def game_day(self):
        return self.time_min // DAY + 1

    def game_hour(self):
        return self.time_min % DAY // 60

    def is_night(self):
        return self.game_hour() >= 20 or self.game_hour() < 5

    def clock_text(self):
        t = self.time_min
        return f"День {self.game_day()} · {WEEKDAYS[(self.game_day() - 1) % 7]} {t % DAY // 60:02d}:{t % 60:02d}"

    # ------------------------------------------------------------ сроки
    def check_deadlines(self):
        f = self.flags
        for did, d in DEADLINES.items():
            key = f"dl_{did}"
            if f.get(f"{key}_fired") or not f.get(d["start"]):
                continue
            if key not in f:
                f[key] = self.time_min           # срок пошёл с того момента, как квест начат
                continue
            if any(f.get(u) for u in d["unless"]):
                continue
            if self.time_min - f[key] >= d["days"] * DAY:
                if not all(f.get(n) for n in d.get("need", [])):   # исход «если успел помочь» — не случился
                    f[f"{key}_fired"] = True
                    continue
                f[f"{key}_fired"] = True
                for eff in d["effects"]:
                    self.apply_effect(eff)
                self.log(d["log"])

    def deadline_left(self, quest_id):
        """Сколько минут осталось до последствия по квесту (None — срока нет или он неактуален)."""
        f = self.flags
        for did, d in DEADLINES.items():
            key = f"dl_{did}"
            if d.get("quest") == quest_id and key in f and not f.get(f"{key}_fired") and not d.get("need") \
                    and not any(f.get(u) for u in d["unless"]):
                return max(0, f[key] + d["days"] * DAY - self.time_min)
        return None
