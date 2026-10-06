"""
Баланс по актам: игра длинная, герой растёт — мир должен расти вместе с ним.

  act_of(loc_id)        к какому акту относится локация (по префиксу id карты);
  scale_enemy(e, act)   враги второго и третьего акта (и тайных мест) крепче: HP, урон, меткость, уровень —
                        и опыта за них дают больше; первый акт — как задумано в data/enemies.json;
  scale_loot(loot, act) добыча в контейнерах: в первом акте меньше крышек и стимуляторов (их легко
                        «нафармить» в начале), в третьем и тайных местах — крышек больше: снаряжение дорогое.

Всё детерминировано: одна и та же карта всегда даёт одинаковую добычу (сохранения не ломаются).
"""
import math

ACT_PREFIXES = {
    1: ("ruins", "fifteen", "drain", "vault57", "baker", "barstow", "zzyzx", "needles", "station", "spot", "cellar",
        "school", "den", "gas"),
    2: ("hub", "junktown", "necropolis", "vault12", "aradesh", "boneyard", "vault15", "vault4"),
    3: ("primm", "goodsprings", "vault22", "nipton", "searchlight", "fort", "vegas", "poseidon", "mariposa", "repconn"),
    4: ("catalina", "nova", "ares"),   # тайные места — уровень третьего акта и выше
}
# (×HP, +урон, +навык, +уровень, ×опыт)
ENEMY_SCALE = {1: (1.0, 0, 0, 0, 1.0), 2: (1.3, 1, 5, 2, 1.3), 3: (1.45, 4, 10, 4, 1.6), 4: (1.55, 5, 12, 5, 1.7)}


def act_of(loc_id):
    for act, prefixes in ACT_PREFIXES.items():
        if loc_id.startswith(prefixes):
            return act
    return 1


def scale_enemy(e, act):
    k_hp, dmg, skill, lvl, k_xp = ENEMY_SCALE.get(act, ENEMY_SCALE[1])
    if act <= 1:
        return
    e.hp = e.max_hp = max(1, round(e.max_hp * k_hp))
    e.damage += dmg
    e.skill += skill
    e.level += lvl
    e.xp_reward = round(e.xp_reward * k_xp)


def scale_loot(loot, act):
    out = dict(loot)
    if "крышки" in out:
        k = {1: 0.7, 2: 1.0, 3: 1.15, 4: 1.25}.get(act, 1.0)
        out["крышки"] = max(1, math.floor(out["крышки"] * k))
    if act <= 1 and out.get("стимулятор", 0) > 0:   # в начале стимулятор — редкость, чаще бинт
        n = out["стимулятор"]
        keep = n // 2
        if keep:
            out["стимулятор"] = keep
        else:
            out.pop("стимулятор")
        out["бинт"] = out.get("бинт", 0) + (n - keep)
    return out


# Награда крышками за выполненное побочное/городское задание (сюжетные — без неё: там платят люди).
# В Fallout деньги приходят прежде всего за задания — без этого к акту II не на что купить патроны.
QUEST_ACT = {
    "sq_hub": 2, "sq_junktown": 2, "sq_necropolis": 2, "sq_aradesh": 2, "sq_boneyard": 2, "sq_vault15": 2, "sq_vault4": 2,
    "sq_primm": 3, "sq_goodsprings": 3, "sq_vault22": 3, "sq_nipton": 3, "sq_searchlight": 3, "sq_vegas": 3,
    "sq_poseidon": 3, "sq_catalina": 4, "sq_nova": 4, "sq_ares": 4, "sq_order": 4,
}
QUEST_CAPS = {1: 60, 2: 150, 3: 200, 4: 250}


def quest_caps(quest_id, main=False):
    if main:
        return 0
    return QUEST_CAPS[QUEST_ACT.get(quest_id, 1)]


def roll_loot(loot):
    """Добыча с тела: целое — столько и есть, дробь меньше 1 — шанс выпасть одной штуке
    (редкое оружие падает не с каждого: {"плазменная винтовка": 0.3})."""
    import random
    out = {}
    for item, cnt in (loot or {}).items():
        if isinstance(cnt, float) and cnt < 1:
            if random.random() < cnt:
                out[item] = 1
        elif cnt:
            out[item] = int(cnt)
    return out
