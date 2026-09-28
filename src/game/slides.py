"""Слайд-шоу (data/slides.json): пролог и концовки глав."""
import json

import pygame

from ..ui.slides_ui import slide_text, typed_chars

with open("data/slides.json", "r", encoding="utf-8") as f:
    SLIDES = {k: v for k, v in json.load(f).items() if not k.startswith("_")}


class SlidesMixin:
    def show_slides(self, show_id):
        d = SLIDES[show_id]
        slides = []
        for sl in d["slides"]:  # абзацы с условиями отбираются в момент показа
            parts = [p for p in sl["parts"] if self.check_condition(p.get("if", {}))]
            if parts:
                slides.append({**sl, "parts": parts})
        self.slides = {"id": show_id, "list": slides, "i": 0, "t": 0}
        self.autowalk = None

    def update_slides(self, dt_ms):
        self.slides["t"] += dt_ms

    def slides_next(self):
        show = self.slides
        slide = show["list"][show["i"]]
        full = len(slide_text(slide))
        if typed_chars(show) < full:  # текст ещё печатается — показать целиком
            show["t"] = full * 1000 // 50 + 1000
            return
        show["i"] += 1
        show["t"] = 0
        if show["i"] >= len(show["list"]):
            self._end_slides()

    def _end_slides(self):
        d = SLIDES[self.slides["id"]]
        self.slides = None
        for eff in d.get("on_end", []):
            self.apply_effect(eff)

    def slides_key(self, key):
        if key == pygame.K_ESCAPE:
            self._end_slides()
        elif key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e, pygame.K_RIGHT):
            self.slides_next()
