"""
Значки рыбы для рыбалки в Нидлсе (src/game/fishing.py): пиксельный карп 16×16, увеличенный до 64×64 —
обычный и «светящийся» (зеленоватый, с бликами), сом и бутылка с запиской уже есть (bottle).

    .venv/bin/python tools/make_fish_icons.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

FISH = [
    "................",
    "................",
    "................",
    "......####......",
    "....##oooo##..#.",
    "...#oooooooo#.##",
    "..#oo*oooooo###.",
    "..#ooooooooooo#.",
    "..#bbbbbbbbbbb#.",
    "...#bbbbbbbb#.##",
    "....##bbbb##..#.",
    "......####......",
    "................",
    "................",
    "................",
    "................",
]
CATFISH = [
    "................",
    "................",
    "................",
    ".....#####......",
    "...##ooooo##..##",
    "..#ooooooooo####",
    ".#o*ooooooooo##.",
    "##ooooooooooo#..",
    "#.#bbbbbbbbbb##.",
    "#..##bbbbbb##.##",
    "......####....##",
    "................",
    "................",
    "................",
    "................",
    "................",
]


def draw(rows, body, belly, eye=(20, 20, 20), glow=None):
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pal = {"#": (40, 32, 26), "o": body, "b": belly, "*": eye}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                s.set_at((x, y), pal[ch])
    big = pygame.transform.scale(s, (64, 64))
    if glow:
        halo = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.ellipse(halo, (*glow, 70), (2, 10, 60, 40))
        halo.blit(big, (0, 0))
        big = halo
    return big


def main():
    pygame.init()
    out = os.path.join("assets", "items")
    pygame.image.save(draw(FISH, (150, 140, 110), (205, 195, 160)), os.path.join(out, "fish.png"))
    pygame.image.save(draw(FISH, (120, 190, 90), (190, 240, 140), glow=(130, 255, 90)), os.path.join(out, "fish_glow.png"))
    pygame.image.save(draw(CATFISH, (95, 90, 80), (160, 150, 130)), os.path.join(out, "catfish.png"))
    print("ok")


if __name__ == "__main__":
    main()
