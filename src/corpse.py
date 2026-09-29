"""Картинка трупа: стоячий кадр персонажа, уложенный на бок, темнее, с лужей крови."""
import pygame

_CACHE = {}


def corpse_image(enemy):
    fb = enemy.anim.frames_by_action
    frame = (fb.get("idle_down") or fb.get("idle"))[0]
    key = (id(frame), getattr(enemy, "facing_left", False))
    if key not in _CACHE:
        body = pygame.transform.rotate(frame, -90 if not getattr(enemy, "facing_left", False) else 90)
        body = body.copy()
        body.fill((150, 135, 130, 255), special_flags=pygame.BLEND_RGBA_MULT)
        w, h = body.get_size()
        out = pygame.Surface((w + 16, h + 12), pygame.SRCALPHA)
        pool = pygame.Surface(out.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(pool, (95, 12, 10, 150), (6, h // 2, w + 4, h // 2 + 8))
        pygame.draw.ellipse(pool, (130, 20, 16, 120), (14, h // 2 + 4, w - 12, h // 2 - 2))
        out.blit(pool, (0, 0))
        out.blit(body, (8, 2))
        _CACHE[key] = out
    return _CACHE[key]
