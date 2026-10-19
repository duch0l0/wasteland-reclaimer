"""
Роли врагов (docs/combat_plan.md): враг — не мясо, у каждого в отряде своя работа.

Роль задаёт поле "role" в data/enemies.json. Каждый ход врага сначала спрашивает свою роль (act); роль
либо делает ход сама (True), либо отдаёт его обычному поведению ai: melee / ranged (False).

  cover      стрелок из укрытия — бежит за мешки/машину, оттуда стреляет; обошли — ищет новое
  flanker    фланговый — не лезет в лоб, заходит со спины (удар в спину точнее — для всех)
  medic      медик — держится сзади, лечит самого раненого своего; снять первым
  commander  командир — свои рядом точнее и с лишним ОД, «все на одного»; убит — отряд дрогнет
  gunner     пулемётчик — после очереди держит сектор: кто двинется в конусе, получит очередь в свой ход
  grenadier  гренадёр — бросает в скопление и выкуривает из укрытия
  ambush     засада — невидим, пока герой не подойдёт; бьёт первым (Выживание замечает следы)
  runner     гонец — бежит за подмогой; добежал (3 хода не задет) — приходит подкрепление
  shield     щитоносец — встаёт между героем и ценным своим (медик, гренадёр, снайпер, командир) — тот в укрытии
  sniper     снайпер — ход целится (виден луч), следующий — выстрел в голову; ушёл с линии — сбил прицел

Мораль: гибель командира или половины отряда — живые могут дрогнуть и бежать (роботы не бегут).
"""
import math
import random

from . import settings as S

ROLE_NAMES = {"cover": "стрелок из укрытия", "flanker": "фланговый", "medic": "медик", "commander": "командир",
              "gunner": "пулемётчик", "grenadier": "гренадёр", "ambush": "засада", "runner": "гонец",
              "shield": "щитоносец", "sniper": "снайпер"}
ROLE_HINTS = {
    "cover": "Прячется за укрытием. Обойдите сбоку или выкурите гранатой.",
    "flanker": "Заходит со спины. Держитесь спиной к стене.",
    "medic": "Лечит своих. Снимите первым.",
    "commander": "Ведёт отряд: свои рядом точнее. Убейте — отряд дрогнет.",
    "gunner": "Держит сектор очередью. Не входите в конус — обойдите или подавите издали.",
    "grenadier": "Бросает гранаты в скопление. Не стойте кучей.",
    "ambush": "Сидит в засаде. Выживание замечает следы.",
    "runner": "Побежит за подмогой. Перехватите.",
    "shield": "Закрывает собой ценных. Обойдите.",
    "sniper": "Целится ход, стреляет следующим. Уйдите с линии огня.",
}
VALUABLE = ("medic", "grenadier", "sniper", "commander")
GUNNER_CONE = 50          # полуугол сектора пулемётчика, градусы
MEDIC_HEAL = 20
MEDIC_AP = 4
AIM_AP = 3


def _cap(s):
    return s[:1].upper() + s[1:]


def role_of(e):
    return getattr(e, "role", None)


# ================================================================ вход из боя
def act(c, e):
    """Ход врага с ролью. True — ход (или его часть) сделан ролью."""
    fn = ACTS.get(role_of(e))
    return bool(fn and fn(c, e))


def begin_turn(c, ent):
    """Начало хода бойца: аура командира, пулемётчик снимает сектор, снайпер проверяет прицел."""
    if ent is c.game.player or c.is_ally(ent):
        for g in c.enemies_in_combat():
            g.ow_fired = False          # пулемётчик стреляет по движению раз за ход героя
        return
    ent.inspired = False
    ent.cover_tried = False          # за ход можно один раз перебежать в укрытие
    if role_of(ent) == "gunner":
        ent.overwatch = None
    from .combat import tile_of, chebyshev
    here = tile_of(ent)
    for cmd in c.enemies_in_combat():
        if cmd is not ent and role_of(cmd) == "commander" and chebyshev(here, tile_of(cmd)) <= 8 and c.los(cmd, ent):
            ent.inspired = True
            ent.ap += 1
            break


def hit_bonus(c, attacker, defender):
    """Поправки к попаданию от ролей и позиции: удар в спину, приказ командира, прицел снайпера."""
    bonus = 0
    if getattr(attacker, "inspired", False):
        bonus += 10
    if behind(attacker, defender):
        bonus += 15
    return bonus


def behind(attacker, defender):
    """Нападающий за спиной цели (цель смотрит в другую сторону)."""
    ax, dx = attacker.rect.centerx, defender.rect.centerx
    if abs(ax - dx) < S.TILE // 2:
        return False
    return ax > dx if getattr(defender, "facing_left", False) else ax < dx


def focus_target(c, enemy):
    """Цель по приказу командира (если он жив и приказал)."""
    t = getattr(c, "focus", None)
    if t is not None and t.alive and (t is c.game.player or t in c.allies_in_combat()):
        if any(role_of(x) == "commander" for x in c.enemies_in_combat()):
            return t
    return None


def shields_cover(c, attacker_tile, defender):
    """Щитоносец рядом с целью со стороны стрелка — цель за «живым укрытием»."""
    from .combat import tile_of, chebyshev
    dt = tile_of(defender)
    for s in c.enemies_in_combat():
        if s is defender or role_of(s) != "shield":
            continue
        st = tile_of(s)
        if chebyshev(st, dt) == 1 and chebyshev(st, attacker_tile) < chebyshev(dt, attacker_tile):
            return True
    return False


# ================================================================ роли
def _cover_shooter(c, e):
    from .combat import tile_of, chebyshev, has_los, tile_center
    p = c._enemy_target(e)
    pt, here = tile_of(p), tile_of(e)
    if c.cover_between(pt, here):
        return False                                    # уже за укрытием — стрелять как обычно
    if e.ap < S.AP_MOVE + c.attack_cost(e) or getattr(e, "cover_moves", 0) >= 4:
        return False
    lv = c.game.level
    good = lambda t: (t != here and c.cover_between(pt, t) and chebyshev(t, pt) <= e.range
                      and has_los(lv, tile_center(t), tile_center(pt)))
    path = c.find_path(e, good, max_len=4)
    if not path:
        return False
    if not getattr(e, "said_cover", False):
        e.said_cover = True
        c.shout(e, "Прикрой!")
    e.cover_moves = getattr(e, "cover_moves", 0) + 1
    step = (path[0][0] - here[0], path[0][1] - here[1])
    return c.try_step(e, *step)


def _flanker(c, e):
    from .combat import tile_of, chebyshev
    p = c._enemy_target(e)
    pt, here = tile_of(p), tile_of(e)
    if e.ap < S.AP_MOVE or behind(e, p):
        return False                                    # за спиной — бить как обычно (в спину точнее)
    face_left = getattr(p, "facing_left", False)
    back = lambda t: chebyshev(t, pt) == 1 and ((t[0] > pt[0]) if face_left else (t[0] < pt[0]))
    adjacent = chebyshev(here, pt) == 1
    path = c.find_path(e, back, max_len=4 if adjacent else 10)
    if not path or (adjacent and e.ap < len(path) * S.AP_MOVE + c.attack_cost(e)):
        return False                                    # обойти не успеть — бьёт в лицо
    step = (path[0][0] - here[0], path[0][1] - here[1])
    return c.try_step(e, *step)


def _medic(c, e):
    from .combat import tile_of, chebyshev
    here = tile_of(e)
    hurt = [x for x in c.enemies_in_combat() if x.hp < x.max_hp * 0.6 and not getattr(x, "robot", False)]
    if hurt and getattr(e, "medkits", 0) > 0:
        t = min(hurt, key=lambda x: (x.hp / x.max_hp, chebyshev(here, tile_of(x))))
        if t is e or chebyshev(here, tile_of(t)) == 1:
            if e.ap < MEDIC_AP:
                return False
            heal = min(MEDIC_HEAL, t.max_hp - t.hp)
            t.hp += heal
            e.ap -= MEDIC_AP
            e.medkits -= 1
            c._float(t, f"+{heal}", (120, 230, 120))
            who = "себя" if t is e else t.name
            c.game.log(f"{_cap(e.name)} перевязывает {who}: +{heal} HP.")
            c.shout(e, "Держись!")
            c.busy_ms = S.COMBAT_ATTACK_MS
            return True
        if e.ap >= S.AP_MOVE:
            path = c.find_path(e, lambda q: chebyshev(q, tile_of(t)) == 1, max_len=8)
            if path:
                return c.try_step(e, path[0][0] - here[0], path[0][1] - here[1])
    p = c._enemy_target(e)
    if chebyshev(here, tile_of(p)) < 4 and e.ap >= S.AP_MOVE and c._flee_step(e, p):
        return True                                     # медик держится сзади
    return False


def _commander(c, e):
    if getattr(e, "ordered", 0) != c.round:
        e.ordered = c.round
        cands = [c.game.player] + c.allies_in_combat()
        t = min(cands, key=lambda x: (x.hp / max(1, x.max_hp), x is not c.game.player))
        if getattr(c, "focus", None) is not t:
            c.focus = t
            c.shout(e, "Все на него!" if t is c.game.player else f"Сначала {t.name}!")
            c.game.log(f"{_cap(e.name)} указывает на цель: {'вы' if t is c.game.player else t.name}.")
    return False


def _gunner(c, e):
    if not getattr(e, "fired", False):
        return False                                    # первая очередь — как обычный стрелок (отметит fired)
    if getattr(e, "overwatch", None) is None and e.ap >= c.attack_cost(e):
        from .combat import tile_of
        p = c._enemy_target(e)
        (gx, gy), (px, py) = tile_of(e), tile_of(p)
        e.overwatch = {"dir": math.atan2(py - gy, px - gx), "range": e.range}
        c.shout(e, "Держу сектор!")
        c.game.log(f"{_cap(e.name)} залегает и держит сектор — двинетесь в конусе, получите очередь.")
    c.end_turn()
    return True


def in_sector(c, gunner, tile):
    from .combat import tile_of, chebyshev, has_los, tile_center
    ow = getattr(gunner, "overwatch", None)
    if not ow:
        return False
    gt = tile_of(gunner)
    if tile == gt or chebyshev(gt, tile) > ow["range"]:
        return False
    ang = math.atan2(tile[1] - gt[1], tile[0] - gt[0])
    diff = abs((ang - ow["dir"] + math.pi) % (2 * math.pi) - math.pi)
    return math.degrees(diff) <= GUNNER_CONE and has_los(c.game.level, tile_center(gt), tile_center(tile))


def overwatch_react(c, mover, tile):
    """Герой или спутник шагнул в сектор — пулемётчик бьёт очередью (раз за ход героя)."""
    for g in c.enemies_in_combat():
        if (role_of(g) == "gunner" and not getattr(g, "ow_fired", False) and g.ap >= c.attack_cost(g)
                and in_sector(c, g, tile)):
            g.ow_fired = True
            c.game.log(f"{_cap(g.name)} бьёт по движению!")
            c.attack(g, mover)
            return True
    return False


def _grenadier(c, e):
    from .combat import tile_of, chebyshev
    if not e.grenades or e.ap < c.THROW_AP:
        return False
    here = tile_of(e)
    foes = [c.game.player] + c.allies_in_combat()
    mine = c.enemies_in_combat()
    best, score = None, 0
    for f in foes:
        t = tile_of(f)
        d = chebyshev(here, t)
        if not (2 <= d <= c.THROW_RANGE) or not c.los(e, f):
            continue
        if any(chebyshev(tile_of(m), t) <= 1 for m in mine):
            continue                                    # своих не задеть
        hits = sum(1 for o in foes if chebyshev(tile_of(o), t) <= 1)
        s = hits * 2 + (2 if c.cover_between(here, t) else 0)
        if s > score:
            best, score = t, s
    if best is None or (score < 3 and random.random() > 0.35):
        return False
    e.grenades -= 1
    c.shout(e, "Граната!")
    c.game.log(f"{_cap(e.name)} швыряет гранату {'в кучу' if score >= 4 else 'за укрытие'}!")
    c.throw(e, best, "grenade")
    return True


def _runner(c, e):
    from .combat import tile_of
    if getattr(e, "help_called", False):
        return False
    if not getattr(e, "running", False):
        e.running = True
        e.run_turns = 0
        c.shout(e, "За подмогой!")
        c.game.log(f"{_cap(e.name)} бросается бежать — за подмогой! Перехватите его.")
    if e.crippled_legs:
        e.help_called = True
        c.game.log(f"{_cap(e.name)} с перебитыми ногами далеко не убежит.")
        return False
    if getattr(e, "run_round", None) != c.round:   # считаются ходы, а не шаги
        e.run_round = c.round
        e.run_turns += 1
    if e.run_turns > 3:
        e.help_called = True
        c.call_reinforcements(e)
        c.end_turn()
        return True
    p = c._enemy_target(e)
    moved = False
    while e.ap >= S.AP_MOVE and c._flee_step(e, p):
        moved = True
        break
    if not moved:
        c.end_turn()
    return True


def _shield(c, e):
    from .combat import tile_of, chebyshev
    p = c._enemy_target(e)
    pt, here = tile_of(p), tile_of(e)
    vip = [x for x in c.enemies_in_combat() if role_of(x) in VALUABLE]
    if not vip or e.ap < S.AP_MOVE:
        return False
    v = min(vip, key=lambda x: chebyshev(tile_of(x), pt))
    vt = tile_of(v)
    good = lambda t: chebyshev(t, vt) == 1 and chebyshev(t, pt) < chebyshev(vt, pt)
    if good(here):
        return False                                    # стоит где надо — бьёт, если герой рядом
    path = c.find_path(e, good, max_len=6)
    if not path:
        return False
    return c.try_step(e, path[0][0] - here[0], path[0][1] - here[1])


def _sniper(c, e):
    p = c._enemy_target(e)
    ok, _ = c.can_attack(e, p)
    aim = getattr(e, "aiming", None)
    if aim is not None and aim is p and ok and not c.cover_between_ents(e, p):
        if e.ap < c.attack_cost(e):
            return False
        e.aiming = None
        e.aimed_shot = True
        c.game.log(f"{_cap(e.name)} стреляет — прицельно, в голову!")
        c.attack(e, p, 1)                               # 1 — голова (BODY_PARTS)
        e.aimed_shot = False
        return True
    if aim is not None:
        e.aiming = None
        c.game.log(f"{_cap(e.name)} теряет прицел.")
    if ok and e.ap >= AIM_AP:
        e.aiming = p
        e.ap = 0
        c.shout(e, "Есть цель…")
        c.game.log(f"{_cap(e.name)} берёт вас на прицел — красный луч. Уйдите с линии!")
        c.end_turn()
        return True
    return False


def _ambush(c, e):
    return False                                        # засада работает до боя (reveal); в бою — как обычно


ACTS = {"cover": _cover_shooter, "flanker": _flanker, "medic": _medic, "commander": _commander,
        "gunner": _gunner, "grenadier": _grenadier, "runner": _runner, "shield": _shield,
        "sniper": _sniper, "ambush": _ambush}


# ================================================================ засада (вне боя)
def ambush_check(c, e):
    """Каждый кадр вне боя: затаившийся враг. True — выскочил (бой начинается, он бьёт первым)."""
    from .combat import tile_of, chebyshev
    if not getattr(e, "hidden", False):
        return False
    g = c.game
    d = chebyshev(tile_of(e), tile_of(g.player))
    if not getattr(e, "spotted", False) and d <= 6 and g.player.skill("survival") >= 50:
        e.spotted = True
        e.hidden = False
        g.log("Свежие следы и примятая трава — тут кто-то затаился. Засада раскрыта.")
        return False
    if d <= 2:
        e.hidden = False
        e.ambusher = True
        g.log(f"{_cap(e.name)} выскакивает из засады!")
        return True
    return False


# ================================================================ мораль
def on_death(c, dead):
    """Убит враг: гибель командира или половины отряда может обратить живых в бегство."""
    if not c.active:
        return
    alive = [e for e in c.enemies_in_combat() if e is not dead]
    if not alive:
        return
    squad = getattr(c, "squad_size", len(alive) + 1)
    lost = squad - len(alive)
    if role_of(dead) == "commander":
        chance = 0.6
        c.game.log(f"{_cap(dead.name)} падает — отряд без командира.")
    elif (lost * 2 >= squad and not getattr(c, "half_lost", False)
          and any(role_of(x) for x in c.order if x is not c.game.player)):   # только у отрядов с ролями
        c.half_lost = True
        chance = 0.3
    else:
        return
    for e in alive:
        if (getattr(e, "robot", False) or getattr(e, "broken", False) or role_of(e) == "commander"
                or getattr(e, "talk", None) or e.type_id == "boss"):
            continue                                    # именные враги (Шрам, главари с разговором) не бегут
        if random.random() < chance:
            e.broken = True
            c.shout(e, "Валим!")
            c.game.log(f"{_cap(e.name)} дрогнул и бежит!")
