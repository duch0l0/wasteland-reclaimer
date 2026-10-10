"""
Рыбалка в Нидлсе (docs/city_plan.md, этап 2). Удочка и наживка — у лавочницы Роуз; рыбачить — с причала,
спросить рыбака Джо. Заброс съедает одну наживку; поплавок бегает по шкале — подсечь (Space или клик),
пока он в зелёной зоне. Зона тем шире, чем выше Выживание; поплавок быстрее у крупной рыбы.

Улов зависит от баржи с жёлтыми треугольниками: залил течь (barge_done) — чистые карп и сом;
не залил — «светящийся карп»: дёшев и, говорят, полезен только тем, кто уже светится.
Изредка — бутылка с запиской (раз за игру): письмо мужа Мамаши Кейт, утонувшего с первой «Мэри».
Рыбу покупает торговка Пег.
"""
import random

CATCH = [("карп", 60), ("сом", 25), ("старый ботинок", 15)]


class FishingMixin:
    def fishing_start(self):
        if not self.inventory.has("удочка"):
            self.log("Без удочки рыба только смеётся. Удочка — у Роуз в лавке.")
            return
        if not self.inventory.has("наживка"):
            self.log("Наживки нет. Червей Роуз продаёт по две крышки — не спрашивай, где она их копает.")
            return
        self.fishing = {"pos": 0.0, "dir": 1, "speed": 0.0, "zone": (0.0, 0.0), "state": "wait", "t": 0, "msg": "",
                        "fish": None, "casts": 0}
        self._cast()

    def _cast(self):
        f = self.fishing
        self.inventory.remove("наживка", 1)
        f["casts"] += 1
        rnd = random.random
        f["fish"] = random.choices([c for c, _ in CATCH], weights=[w for _, w in CATCH])[0]
        if not self.flags.get("fish_bottle") and f["casts"] >= 3 and rnd() < 0.25:
            f["fish"] = "бутылка с запиской"
        width = 0.12 + min(0.16, self.player.skill("survival") / 600)
        start = 0.15 + rnd() * (0.85 - width - 0.15)
        f.update(state="wait", t=random.randint(700, 1700), pos=0.0, dir=1,
                 speed={"сом": 1.45, "бутылка с запиской": 0.7}.get(f["fish"], 1.0) * (0.9 + rnd() * 0.3),
                 zone=(start, start + width), msg="Поплавок качается на воде… ждите поклёвки.")

    def update_fishing(self, dt_ms):
        f = self.fishing
        if not f:
            return
        if f["state"] == "wait":
            f["t"] -= dt_ms
            if f["t"] <= 0:
                f["state"] = "bite"
                f["msg"] = "Клюёт! Подсекайте, когда поплавок в зелёном (Space)!"
        elif f["state"] == "bite":
            f["pos"] += f["dir"] * f["speed"] * dt_ms / 1000
            if f["pos"] >= 1:
                f["pos"], f["dir"] = 1.0, -1
            elif f["pos"] <= 0:
                f["pos"], f["dir"] = 0.0, 1

    def fishing_strike(self):
        f = self.fishing
        if f["state"] == "wait":
            f["msg"] = "Рано! Рыба почуяла и ушла. Наживка — тоже."
            f["state"] = "done"
            return
        if f["state"] != "bite":
            if self.inventory.has("наживка"):
                self._cast()
            return
        lo, hi = f["zone"]
        f["state"] = "done"
        if not lo <= f["pos"] <= hi:
            f["msg"] = "Сорвалась! Только круги по воде. (Space — забросить ещё, Esc — смотать удочку)"
            return
        name = f["fish"]
        if name == "карп" and not self.flags.get("barge_done"):
            name = "светящийся карп"
        if name == "бутылка с запиской":
            self.flags["fish_bottle"] = True
        self.inventory.add(name, 1)
        self.flags["fish_caught"] = self.flags.get("fish_caught", 0) + 1
        f["msg"] = {"старый ботинок": "Вытащили… старый ботинок. Левый. Река шутит.",
                    "бутылка с запиской": "Что-то тяжёлое и гладкое — бутылка! Внутри свёрнутая бумага."}.get(
            name, f"Попалась! {name[:1].upper() + name[1:]}.") + " (Space — ещё, Esc — смотать)"
        self.apply_effect({"type": "xp", "amount": 5})

    def fishing_key(self, key):
        import pygame
        if key in (pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
            self.fishing_strike()
        elif key == pygame.K_ESCAPE:
            self.fishing = None
            self.log("Вы сматываете удочку.")
