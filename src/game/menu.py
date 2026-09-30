"""
Меню: главное (при запуске) и пауза (Esc в игре), экраны слотов для
сохранения и загрузки, подтверждения. Быстрое сохранение — F5, загрузка — F9.

self.menu = {"screen": main | pause | save | load | confirm, "sel": пункт,
             "confirm": {"text", "yes"}, "back": куда вернуться}
"""
import pygame

from .saveload import SLOTS, QUICK, slot_info


class MenuMixin:
    def open_menu(self, screen="pause"):
        if screen == "pause":
            self.last_frame = self.screen.copy()  # миниатюра для сохранения — без меню поверх
        self.menu = {"screen": screen, "sel": 0, "back": None}
        self.autowalk = None

    def close_menu(self):
        self.menu = None

    # ------------------------------------------------------------ пункты
    def menu_items(self):
        """(подпись, действие, доступно) для текущего экрана."""
        m = self.menu
        scr = m["screen"]
        latest = self.latest_save()
        if scr == "main":
            return [("Продолжить", lambda: self._load_and_play(latest), latest is not None),
                    ("Новая игра", self.new_game, True),
                    ("Загрузить", lambda: self._goto("load"), any(slot_info(s) for s in SLOTS + [QUICK])),
                    ("Звук", lambda: self._goto("sound"), True),
                    ("Выход", self.quit_game, True)]
        if scr == "pause":
            why = self.can_save()
            return [("Продолжить", self.close_menu, True),
                    ("Сохранить", lambda: self._goto("save"), why is None),
                    ("Загрузить", lambda: self._goto("load"), any(slot_info(s) for s in SLOTS + [QUICK])),
                    ("Звук", lambda: self._goto("sound"), True),
                    ("Главное меню", lambda: self._confirm("Выйти в главное меню? Несохранённое пропадёт.",
                                                           lambda: self.open_menu("main")), True),
                    ("Выход из игры", lambda: self._confirm("Выйти из игры? Несохранённое пропадёт.",
                                                            self.quit_game), True)]
        if scr in ("save", "load"):
            slots = SLOTS if scr == "save" else [QUICK] + SLOTS
            out = []
            for s in slots:
                info = slot_info(s)
                if scr == "save":
                    act = (lambda s=s: self._confirm("Перезаписать сохранение?", lambda: self._save_and_close(s))) \
                        if info else (lambda s=s: self._save_and_close(s))
                    out.append((s, act, True))
                else:
                    out.append((s, lambda s=s: self._load_and_play(s), info is not None))
            return out + [("Назад", self._back, True)]
        if scr == "sound":  # ползунки: действие по Enter/клику — ничего, громкость — стрелками или мышью
            return [("Музыка", lambda: None, True), ("Звуки", lambda: None, True), ("Назад", self._back, True)]
        if scr == "confirm":
            return [("Да", m["confirm"]["yes"], True), ("Нет", self._back, True)]
        return []

    def _goto(self, screen):
        self.menu = {"screen": screen, "sel": 0, "back": self.menu}

    def _back(self):
        back = self.menu.get("back")
        if back:
            self.menu = back
        elif self.menu["screen"] != "main":
            self.close_menu()

    def _confirm(self, text, yes):
        self.menu = {"screen": "confirm", "sel": 1, "confirm": {"text": text, "yes": yes}, "back": self.menu}

    def _save_and_close(self, slot):
        if self.save_game(slot):
            self.close_menu()

    def _load_and_play(self, slot):
        if slot and self.load_game(slot):
            self.close_menu()

    def latest_save(self):
        import os
        from . import saveload
        best = None
        for s in SLOTS + [QUICK]:
            p = os.path.join(saveload.SAVE_DIR, f"{s}.json")
            if os.path.isfile(p) and slot_info(s) and (best is None or os.path.getmtime(p) > best[1]):
                best = (s, os.path.getmtime(p))
        return best[0] if best else None

    def new_game(self):
        """Всё с нуля: пересоздаём игру, но в том же окне, и запускаем пролог."""
        screen = self.screen
        self.__init__(intro=False, _screen=screen, _prologue=True)

    def quit_game(self):
        self.running = False

    # ------------------------------------------------------------ клавиши
    def menu_key(self, key):
        items = self.menu_items()
        m = self.menu
        if key == pygame.K_ESCAPE:
            if m["screen"] == "main":
                return
            self._back()
            return
        if m["screen"] == "sound" and key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d) and m["sel"] < 2:
            kind = ("music", "sfx")[m["sel"]]
            step = 0.1 if key in (pygame.K_RIGHT, pygame.K_d) else -0.1
            self.audio.set_volume(kind, self.audio.volume[kind] + step)
            if kind == "sfx":
                self.audio.play("button")  # сразу слышно, как громко
            return
        if key in (pygame.K_UP, pygame.K_w):
            m["sel"] = (m["sel"] - 1) % len(items)
        elif key in (pygame.K_DOWN, pygame.K_s):
            m["sel"] = (m["sel"] + 1) % len(items)
        elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            label, action, enabled = items[m["sel"]]
            if enabled:
                action()

    def quick_save(self):
        self.last_frame = self.screen.copy()
        self.save_game(QUICK)

    def quick_load(self):
        if slot_info(QUICK):
            self.load_game(QUICK)
        else:
            self.log("Быстрого сохранения ещё нет (F5 — сохранить).")
