"""
Как выглядит герой: слои из assets/hero/ (tools/make_hero.py) склеиваются по тому,
что надето и что в руках, — каска на голове, бронежилет из дорожных знаков на теле,
дробовик в руках видны на спрайте.

  основа + броня на теле + головной убор + оружие; если герой смотрит вверх,
  оружие кладётся первым — оно за спиной.

Анимации те же, что у остальных персонажей (src/loader.load_directional_animations):
walk/idle/attack по сторонам, melee — удар ломом, shoot — выстрел из того, что в руках,
плюс вздрагивание/уворот и атаки из стоячего кадра. Наборы кадров кэшируются по
сочетанию (броня, шлем, оружие) — переодевание мгновенное.
"""
import os

import pygame

from . import loader

ROOT = os.path.join("assets", "hero")
DIRS = ("down", "left", "right", "up")
BODY = {"куртка из покрышек": "body_tire", "бронежилет из дорожных знаков": "body_signs",
        "балахон послушника": "body_robe"}
HEAD = {"каска строителя": "head_hardhat", "мотошлем": "head_moto"}
FRAMES = {"walk": 4, "melee": 3, "shoot": 3}
_LAYERS = {}
_LOOKS = {}


def available():
    return os.path.isdir(os.path.join(ROOT, "base"))


def _layer(name, action, d, i):
    key = (name, action, d, i)
    if key not in _LAYERS:
        path = os.path.join(ROOT, name, action, d, f"{i}.png")
        img = None
        if os.path.isfile(path):
            img = pygame.image.load(path)
            if pygame.display.get_surface() is not None:
                img = img.convert_alpha()
        _LAYERS[key] = img
    return _LAYERS[key]


def look_key(player):
    body = BODY.get(player.equipped("body"))
    head = HEAD.get(player.equipped("head"))
    return body, head, player.weapon


def animations(body=None, head=None, weapon="melee"):
    """Кадры героя для сочетания слоёв — в формате load_directional_animations."""
    key = (body, head, weapon)
    if key in _LOOKS:
        return _LOOKS[key]
    wlayer = f"weapon_{weapon}"
    out = {}
    for d in DIRS:
        for action, n in FRAMES.items():
            frames = []
            for i in range(n):
                base = _layer("base", action, d, i)
                if base is None:
                    continue
                img = pygame.Surface(base.get_size(), pygame.SRCALPHA)
                order = [wlayer, "base", body, head] if d == "up" else ["base", body, head, wlayer]
                for name in order:
                    lay = _layer(name, action, d, i) if name else None
                    if lay is not None:
                        img.blit(lay, (0, 0))
                frames.append(img)
            if frames:
                out[f"{action}_{d}"] = frames
        walk = out[f"walk_{d}"]
        out[f"idle_{d}"] = [walk[1]]
        hit_src = walk[1]
        out[f"attack_{d}"] = out.get(f"melee_{d}" if weapon == "melee" else f"shoot_{d}", walk)
        if weapon == "melee":
            out.pop(f"shoot_{d}", None)
        else:
            out.pop(f"melee_{d}", None)
        out[f"hit_{d}"], out[f"dodge_{d}"] = loader.make_reactions(hit_src, d)
        out[f"attack_melee_{d}"], out[f"attack_ranged_{d}"] = loader.make_attacks(hit_src, d)
    # запасные кадры без стороны: аниматор берёт их, если сторона чужая (после изометрии — «se»)
    out["idle"], out["walk"], out["attack"] = out["idle_down"], out["walk_down"], out["attack_down"]
    _LOOKS[key] = out
    return out
