"""
Пустые ящики (docs/review_plan.md, п. 2.6): при загрузке карты контейнер без лута
получает 1-2 единицы хлама по типу места, а пустой остаётся только хвост, который
влезает в 8% контейнеров карты.

  - выбор детерминированный: crc32 от id карты и индекса контейнера, без random —
    одна и та же карта при каждом входе наполняется одинаково;
  - вскрытый и обысканный ящик не наполняется заново: сохранение кладёт loot
    контейнеров поверх данных карты (src/game/saveload.py: _loc_state / _restore_loc),
    а наполнение случается только при сборке карты;
  - сюжетные пустышки не трогаем: on_put (тайник «положи нужное»), requires (заперт),
    owner (кража), corpse (тело) и контейнеры, которые по имени задуманы пустыми
    (SKIP_NAMES) — они остаются пустыми всегда и считаются в квоту 8%;
  - пул зависит от типа места: music локации из data/locations.json (desert, caves,
    vats, lab, hub/junktown/reno, raiders) — пять разных наборов хлама;
  - предметы — только хлам и материалы из data/items.json (категория resource),
    без патронов, лечения, оружия и крышек.
"""
import json
import os
import zlib

EMPTY_SHARE = 0.08          # доля контейнеров карты, которым положено остаться пустыми

# pools: только resource-предметы (лом, ткань, изолента…). Ни патронов, ни аптек.
POOLS = {
    "wasteland": ("лом", "ткань", "верёвка", "спички", "старый ботинок"),
    "cave": ("лом", "пружина", "изолента", "спички", "старый ботинок"),
    "vault": ("изолента", "предохранитель Vault-Tec", "батарейки", "пружина", "лом"),
    "town": ("ткань", "верёвка", "спички", "изолента", "гаечный ключ"),
    "raider": ("лом", "моторное масло", "пружина", "ткань", "старый ботинок"),
}
MUSIC_POOL = {"desert": "wasteland", "caves": "cave", "vats": "vault", "lab": "vault",
              "hub": "town", "junktown": "town", "reno": "town", "raiders": "raider"}
# имена, которые по замыслу пустые (сюжетные «контейнеры ВРЭ», «пустой контейнер»)
SKIP_NAMES = ("контейнер ВРЭ", "пустой контейнер")

_MAP_MUSIC = None


def _map_music():
    """id карты -> music локации, которая её открывает (data/locations.json)."""
    global _MAP_MUSIC
    if _MAP_MUSIC is None:
        _MAP_MUSIC = {}
        try:
            with open("data/locations.json", "r", encoding="utf-8") as f:
                locs = json.load(f)
        except OSError:
            locs = {}
        for d in locs.values():
            m = d.get("map") if isinstance(d, dict) else None
            if isinstance(m, str) and m.endswith(".json"):
                _MAP_MUSIC[os.path.basename(m)[:-5]] = d.get("music")
    return _MAP_MUSIC


def place_type(map_id, style=None):
    """Тип места для пула: vault / cave / town / raider / wasteland."""
    if style in ("vault", "cave",):
        return style
    music = _map_music().get(map_id)
    if music in MUSIC_POOL:
        return MUSIC_POOL[music]
    low = (map_id or "").lower()          # карта без локации (встреча, тест) — по имени
    if "vault" in low or low.startswith(("v11_", "v15_", "v22_", "v4_")):
        return "vault"
    if any(w in low for w in ("cave", "mine", "crypt", "tunnel", "drain", "sewer", "cellar")):
        return "cave"
    if any(w in low for w in ("raider", "camp", "hideout")):
        return "raider"
    if any(w in low for w in ("town", "hub", "vegas", "reno", "junk", "city")):
        return "town"
    return "wasteland"


def _hash(map_id, index, salt=0):
    return zlib.crc32(f"{map_id}#{index}#{salt}".encode("utf-8"))


def is_special(c):
    """Контейнер не трогаем: сюжетный, запертый, чужой, тело или задуман пустым."""
    return bool(c.get("on_put") or c.get("requires") or c.get("owner") or c.get("corpse")
                or c.get("quest") or c.get("flag") or c.get("name") in SKIP_NAMES)


def looks_empty(c):
    """Пустой и это видно: не запертый и не тайник «положи нужное» — те выглядят закрытыми."""
    return not c.get("loot") and not c.get("requires") and not c.get("on_put")


def plan(map_id, containers, style=None):
    """Что положить: {индекс: {предмет: сколько}} — только для пустых контейнеров.
    Оставленные пустыми в план не входят; план не меняет containers."""
    n = len(containers)
    if not n:
        return {}
    pool = POOLS[place_type(map_id, style)]
    empties = [i for i, c in enumerate(containers) if not c.get("loot")]
    specials = [i for i in empties if is_special(containers[i])]
    quota = int(n * EMPTY_SHARE)                        # пустых на карте — вниз, ≤ 8%
    need_empty = max(0, quota - len(specials))
    cand = [i for i in empties if i not in set(specials)]
    cand.sort(key=lambda i: (_hash(map_id, i), i))      # кого оставить пустым — по хэшу
    keep_empty = set(cand[:need_empty])
    out = {}
    for i in cand[need_empty:]:
        h = _hash(map_id, i, 1)
        out[i] = {pool[h % len(pool)]: 1 + (h // 997) % 2}   # 1-2 единицы
    return out


def fill(map_id, containers, style=None):
    """Наполнить пустые контейнеры карты. Возвращает сколько наполнено."""
    todo = plan(map_id, containers, style)
    for i, loot in todo.items():
        if not containers[i].get("loot"):               # только пустые: дважды не наполняем
            containers[i]["loot"] = dict(loot)
    return len(todo)


# ------------------------------------------------------------ вид: вскрытый проп
_OPEN = None


def _open_map():
    """Проп -> его «вскрытый/пустой» вариант из data/props*.json: crate → crate_open,
    locker_2 → locker_open_a, wardrobe → wardrobe_open. Только та же семья картинок."""
    global _OPEN
    if _OPEN is None:
        from . import props as P
        names = set(P.CATALOG)
        _OPEN = {}
        for n in names:
            if n.endswith(("_open", "_open_a", "_open_b", "_open_c", "_empty", "_broken")):
                continue
            cand = [n + "_open", n + "_open_a", n + "_empty"]
            base, _, tail = n.rpartition("_")
            if base and (tail.isdigit() or tail in ("b", "c", "d", "e")):
                cand += [base + s for s in ("_open", "_open_a", "_open_b", "_empty")]
            _OPEN[n] = next((c for c in cand if c in names), None)
    return _OPEN


def open_variant(name):
    """«Вскрытый» вариант пропа или None, если пары нет."""
    return _open_map().get(name)


def has_open_variant(name):
    return open_variant(name) is not None
