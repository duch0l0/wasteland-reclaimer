"""
Экшен-режим: Барстоу за наёмника Дэкса — стрельба в реальном времени.

Вместо пошагового боя: WASD — бежать, мышь — целиться, зажатая ЛКМ — стрелять,
ПКМ / F / 1 / 2 — сменить ствол, R — перезарядить. Патроны бесконечные, но магазин
кончается — и Дэкс перезаряжается:
  автомат  — 30 патронов очередью, перезарядка 3 с;
  дробовик — 8 выстрелов веером дроби (отбрасывает), перезарядка 5 с — патроны
             закладываются по одному, это видно на полоске.
Гули бродят по городу; кто заметил Дэкса — бежит к нему по кратчайшему пути (карта
расстояний от Дэкса по клеткам, пересчитывается несколько раз в секунду), вблизи — бьёт.
У некоторых домов, стоит подойти, из двери вываливается толпа в 15–20 гулей («hordes»
в карте, tools/build_barstow.py). От них можно убежать: Дэкс быстрее почти всех.

Какие локации в этом режиме — "action": true в data/locations.json (и только за Дэкса).
"""
import math
import random
from collections import deque

import pygame

from . import settings as S
from .combat import tile_of, rect_pos_for_tile, has_los, voice_of

T = S.TILE


class Gun:
    def __init__(self, name, mag, reload_ms, fire_ms, dmg, pellets, spread, rng, snd, knock=0):
        self.name, self.mag, self.reload_ms, self.fire_ms = name, mag, reload_ms, fire_ms
        self.dmg, self.pellets, self.spread, self.range, self.snd, self.knock = dmg, pellets, spread, rng, snd, knock


GUNS = {
    "ar": Gun("Автомат", 30, 3000, 100, (10, 10), 1, 3.5, 13 * T, "ar", knock=2),
    "sg": Gun("Дробовик", 8, 5000, 700, (5, 5), 7, 22, 7 * T, "sg", knock=16),
}
# здоровье гулей в экшене — ровно в пулях автомата (по 10): бегун 2, обычный 3, светящийся 5
ACTION_HP = {"ghoul_runner": 20, "feral": 30, "mutant": 30, "rad_mutant": 50}


def set_action_hp(e):
    hp = ACTION_HP.get(e.type_id)
    if hp:
        e.hp = e.max_hp = hp
ORDER = ["ar", "sg"]

# скорость гулей, пикс. мира в секунду (Дэкс бежит 180) и урон вблизи
SPEED = {"feral": 105, "ghoul_runner": 170, "rad_mutant": 72, "mutant": 95}
ATTACK_MS = 850
REACH = 40


class ActionMode:
    def __init__(self, game):
        self.g = game
        self.gun = "ar"
        self.ammo = {k: g.mag for k, g in GUNS.items()}
        self.reload_left = 0          # мс до конца перезарядки (0 — не перезаряжается)
        self.cool = 0                 # мс до следующего выстрела
        self.firing_ms = 0            # сколько ещё показывать стрельбу в анимации
        self.flow = {}                # клетка -> расстояние до Дэкса (шагов)
        self.flow_ms = 0
        self.spawn_queue = []         # [(мс, враг-вид, клетка)]
        self.shake_ms = 0
        self._last_pos = None

    # ------------------------------------------------------------ когда включён
    @property
    def active(self):
        g = self.g
        if not getattr(g, "merc_mode", False) or g.mode != "local":
            return False
        from .location import LOCATION_DEFS
        return bool(LOCATION_DEFS.get(g.loc.id, {}).get("action"))

    def paused(self):
        g = self.g
        return g.modal_open() or g.game_over or g.menu is not None or g.slides is not None

    # ------------------------------------------------------------ оружие
    def switch(self, to=None):
        if self.reload_left:
            self.reload_left = 0      # сменил ствол — перезарядку начинать заново
        self.gun = to or ORDER[(ORDER.index(self.gun) + 1) % len(ORDER)]
        self.g.log(f"В руках: {GUNS[self.gun].name}.")
        self.g.audio.play("button")

    def reload(self):
        gun = GUNS[self.gun]
        if self.reload_left or self.ammo[self.gun] >= gun.mag:
            return
        self.reload_left = gun.reload_ms
        self.g.audio.play(f"{gun.snd}_reload")

    def status(self):
        """Для панели: «Автомат 23/30» или «Перезарядка 1.4 с»."""
        gun = GUNS[self.gun]
        if self.reload_left:
            return f"{gun.name}: перезарядка {self.reload_left / 1000:.1f} с"
        return f"{gun.name} {self.ammo[self.gun]}/{gun.mag}"

    def reload_progress(self):
        if not self.reload_left:
            return None
        gun = GUNS[self.gun]
        return 1 - self.reload_left / gun.reload_ms

    def aim_world(self):
        return self.g.world_pos(pygame.mouse.get_pos())

    def trigger_held(self):
        from .ui.common import over_ui
        pos = pygame.mouse.get_pos()
        if not pygame.mouse.get_pressed()[0] or over_ui(pos):
            return False
        g = self.g
        target = g.entity_at_screen(pos)   # по жителю (Роза) — не стрелять, а говорить
        return target is None or target in g.enemies

    def _shoot(self):
        g, p = self.g, self.g.player
        gun = GUNS[self.gun]
        ox, oy = p.rect.centerx, p.rect.centery - 6
        ax, ay = self.aim_world()
        base = math.atan2(ay - oy, ax - ox)
        hits = {}
        for _ in range(gun.pellets):
            a = base + math.radians(random.uniform(-gun.spread / 2, gun.spread / 2))
            end, victim = self._ray(ox, oy, a, gun.range)
            g.combat.tracers.append({"from": pygame.Vector2(ox, oy), "to": pygame.Vector2(end), "t": 0})
            if victim is not None:
                hits.setdefault(id(victim), [victim, 0, a])[1] += random.randint(*gun.dmg)
        g.audio.play(f"{gun.snd}_shot", g.cam.p(ox, oy)[0], volume=0.7 if gun.pellets == 1 else 0.9)
        for victim, dmg, a in hits.values():
            self._damage(victim, dmg, a, gun)
        self.ammo[self.gun] -= 1
        self.firing_ms = 260
        p.anim.face(ax - ox, ay - oy)

    def _ray(self, ox, oy, a, rng):
        """Луч выстрела: до стены, до первого гуля или на всю дальность."""
        dx, dy = math.cos(a), math.sin(a)
        lv = self.g.level
        foes = [e for e in self.g.enemies if e.alive]
        step = 8
        x, y = ox, oy
        for _ in range(int(rng / step)):
            x += dx * step
            y += dy * step
            if lv.blocks_sight(int(x) // T, int(y) // T) and (int(x) // T, int(y) // T) != tile_of(self.g.player):
                return (x, y), None
            for e in foes:
                if e.rect.inflate(10, 16).collidepoint(x, y):
                    return (x, y), e
        return (x, y), None

    def _damage(self, e, dmg, a, gun):
        g = self.g
        e.apply_damage(dmg)
        e.awake = True
        fx, fy = g.cam.p(*e.rect.center)
        g.audio.play(f"{gun.snd}_hit", fx, volume=0.6)
        g.combat._float(e, f"-{dmg}", (230, 80, 60))
        g.gore.hit(g.level, e.rect, (e.rect.centerx - math.cos(a) * 40, e.rect.centery - math.sin(a) * 40),
                   "ranged", crit=gun.pellets > 1, kill=not e.alive, delay_ms=0)
        if gun.knock and e.alive:   # дробь отбрасывает
            self._move(e, math.cos(a) * gun.knock, math.sin(a) * gun.knock)
        if e.alive:
            e.anim.play_once("hit")
            if random.random() < 0.35:
                g.audio.play(f"{voice_of(e)}_hurt", fx, volume=0.6)
        else:
            g.audio.play(f"{voice_of(e)}_death", fx, volume=0.8)
            g.on_enemy_killed(e)

    # ------------------------------------------------------------ кадр
    def update(self, dt_ms):
        if not self.active or self.paused():
            return
        g, p = self.g, self.g.player
        if not p.alive:
            return
        self._guns(dt_ms)
        self._hordes(dt_ms)
        self._zombies(dt_ms)
        # анимация Дэкса: стреляет — повёрнут к прицелу, на бегу — стрельба на бегу
        pos = p.rect.topleft
        moving = self._last_pos is not None and pos != self._last_pos
        self._last_pos = pos
        if self.firing_ms > 0:
            self.firing_ms -= dt_ms
            ax, ay = self.aim_world()
            p.anim.face(ax - p.rect.centerx, ay - p.rect.centery)
            p.anim.set_action("runshoot" if moving else "shoot")
        if self.shake_ms > 0:
            self.shake_ms -= dt_ms

    def _guns(self, dt_ms):
        gun = GUNS[self.gun]
        if self.reload_left:
            self.reload_left = max(0, self.reload_left - dt_ms)
            if gun.pellets > 1:   # дробовик: патроны по одному — видно на полоске
                self.ammo[self.gun] = min(gun.mag, int((1 - self.reload_left / gun.reload_ms) * gun.mag))
            if not self.reload_left:
                self.ammo[self.gun] = gun.mag
            return
        self.cool = max(-gun.fire_ms, self.cool - dt_ms)
        if not self.trigger_held():
            return
        while self.cool <= 0:
            if self.ammo[self.gun] <= 0:
                self.g.audio.play("empty")
                self.reload()
                return
            self._shoot()
            self.cool += gun.fire_ms
            if self.ammo[self.gun] <= 0:   # магазин пуст — сразу перезаряжается
                self.reload()
                return

    # ------------------------------------------------------------ гули
    def _flow(self):
        """Карта расстояний от Дэкса по проходимым клеткам (BFS) — гули бегут вниз по ней."""
        lv, start = self.g.level, tile_of(self.g.player)
        dist = {start: 0}
        q = deque([start])
        while q:
            c = q.popleft()
            d = dist[c]
            if d > 40:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c[0] + dx, c[1] + dy)
                if n not in dist and not lv.is_wall(*n):
                    dist[n] = d + 1
                    q.append(n)
        self.flow = dist

    def _move(self, e, dx, dy):
        """Сдвиг гуля со стенами (по осям, как у героя)."""
        lv = self.g.level
        for ax, ay in ((dx, 0), (0, dy)):
            if not ax and not ay:
                continue
            e.rect.x += round(ax)
            e.rect.y += round(ay)
            for r in lv.solids_near(e.rect):
                if e.rect.colliderect(r):
                    e.rect.x -= round(ax)
                    e.rect.y -= round(ay)
                    break

    def _zombies(self, dt_ms):
        g, p = self.g, self.g.player
        self.flow_ms -= dt_ms
        if self.flow_ms <= 0:
            self._flow()
            self.flow_ms = 280
        pc = pygame.Vector2(p.rect.center)
        foes = [e for e in g.enemies if e.alive and e.hostile]
        for e in foes:
            ec = pygame.Vector2(e.rect.center)
            dist = ec.distance_to(pc)
            if not getattr(e, "awake", False):
                if dist <= e.aggro and has_los(g.level, e.rect.center, p.rect.center):
                    e.awake = True
                    if random.random() < 0.5:
                        g.audio.play(f"{voice_of(e)}_hurt", g.cam.p(*e.rect.center)[0], volume=0.4)
                else:
                    continue
            e.atk_ms = max(0, getattr(e, "atk_ms", 0) - dt_ms)
            if dist <= REACH:
                e.anim.face(pc.x - ec.x, pc.y - ec.y)
                if e.atk_ms <= 0 and not e.anim.busy:
                    e.atk_ms = ATTACK_MS
                    e.anim.play_once("attack_melee")
                    dmg = random.randint(max(1, e.damage - 1), e.damage + 1)
                    p.apply_damage(dmg)
                    g.combat._float(p, f"-{dmg}", (230, 80, 60))
                    g.audio.play("hit", g.cam.p(*p.rect.center)[0], volume=0.8)
                    if getattr(e, "rads", 0):   # в экшене бьют часто — облучают слабее
                        p.add_rads(max(1, e.rads // 3))
                    if random.random() < 0.4:
                        g.audio.play("human_hurt", volume=0.7)
                    if not p.alive:
                        g.log(f"{e.name.capitalize()} добирается до Дэкса. Барстоу забрал ещё одного.")
                continue
            # куда бежать: прямо, если видно и близко; иначе — вниз по карте расстояний
            if dist < 3 * T and has_los(g.level, e.rect.center, p.rect.center):
                goal = pc
            else:
                t = tile_of(e)
                best = min(((t[0] + dx, t[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))),
                           key=lambda c: self.flow.get(c, 10 ** 6))
                if self.flow.get(best, 10 ** 6) >= self.flow.get(t, 10 ** 6):
                    goal = pc
                else:
                    goal = pygame.Vector2(best[0] * T + T / 2, best[1] * T + T / 2)
            v = goal - ec
            if v.length() > 1:
                v.scale_to_length(SPEED.get(e.type_id, 95) * dt_ms / 1000)
                self._move(e, v.x, v.y)
                e.anim.face(v.x, v.y)
                if not e.anim.busy:
                    e.anim.set_action("run" if e.type_id == "ghoul_runner" else "walk")
        # не слипаться в одну точку
        for i, a in enumerate(foes):
            for b in foes[i + 1:]:
                d = pygame.Vector2(b.rect.center) - pygame.Vector2(a.rect.center)
                if 0 < d.length() < 30:
                    push = d.normalize() * (30 - d.length()) / 2
                    self._move(a, -push.x, -push.y)
                    self._move(b, push.x, push.y)

    # ------------------------------------------------------------ толпы из домов
    def _hordes(self, dt_ms):
        g = self.g
        lv = g.level
        me = tile_of(g.player)
        for h in getattr(lv, "hordes", []):
            if h["done"]:
                continue
            x0, y0, x1, y1 = h["trigger"]
            if x0 <= me[0] <= x1 and y0 <= me[1] <= y1:
                h["done"] = True
                for i in range(h["count"]):
                    self.spawn_queue.append([300 + i * 110, random.choice(h["kinds"]), tuple(h["door"])])
                g.log(h.get("msg", "Из двери вываливается толпа гулей!"))
                g.audio.play("ghoul_death", volume=1.0)
                g.audio.play("ghoul_hurt", delay_ms=200, volume=1.0)
                self.shake_ms = 400
        if not self.spawn_queue:
            return
        from .location import make_enemy
        for item in self.spawn_queue:
            item[0] -= dt_ms
        ready = [s for s in self.spawn_queue if s[0] <= 0]
        self.spawn_queue = [s for s in self.spawn_queue if s[0] > 0]
        for _, kind, door in ready:
            e = make_enemy((0, 0), kind, iso=True)
            set_action_hp(e)
            e.rect.topleft = rect_pos_for_tile(e, door)
            e.rect.x += random.randint(-10, 10)
            e.awake = True
            e.aggro = 2000
            e.horde = True
            g.loc.enemies.append(e)

    def hordes_left(self):
        return any(not h["done"] for h in getattr(self.g.level, "hordes", [])) or bool(self.spawn_queue)

    def chasing(self):
        """За Дэксом гонятся (сохраняться нельзя)."""
        return any(e.alive and getattr(e, "awake", False) for e in self.g.enemies) or bool(self.spawn_queue)

    # ------------------------------------------------------------ картинка поверх
    def draw_overlay(self, surf, cam, zoom):
        """Прицел у мыши, патроны и полоска перезарядки над Дэксом."""
        g = self.g
        mx, my = pygame.mouse.get_pos()
        col = (255, 220, 120) if not self.reload_left else (160, 150, 130)
        pygame.draw.circle(surf, (20, 16, 12), (mx, my), 11, 3)
        pygame.draw.circle(surf, col, (mx, my), 10, 1)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            pygame.draw.line(surf, col, (mx + dx * 5, my + dy * 5), (mx + dx * 14, my + dy * 14), 2)
        fx, fy = cam.foot(g.player)
        x, y = int(fx * zoom), int((fy - 120) * zoom)
        gun = GUNS[self.gun]
        prog = self.reload_progress()
        w = 64
        pygame.draw.rect(surf, (15, 12, 10), (x - w // 2 - 1, y - 1, w + 2, 7))
        if prog is not None:
            pygame.draw.rect(surf, (230, 190, 70), (x - w // 2, y, int(w * prog), 5))
        else:
            pygame.draw.rect(surf, (120, 200, 110), (x - w // 2, y, int(w * self.ammo[self.gun] / gun.mag), 5))
        for i in range(gun.mag if gun.mag <= 8 else 0):   # у дробовика — каждый патрон
            c = (230, 80, 50) if i < self.ammo[self.gun] else (60, 50, 44)
            pygame.draw.rect(surf, c, (x - 28 + i * 7, y + 8, 5, 8))
