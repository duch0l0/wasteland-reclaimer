"""
Конструктор живого населения: у каждого жителя своя анкета (data/folks.json) и свои разговоры между конкретными жителями
(data/folk_talks.json). Авторские файлы — tools/folks_*.py, сборка — tools/build_folks.py.

  F(loc, key, name, sh, g, greet, bio, dream, news, world, barks, seek=None, tip=None, stroll=None)
      loc    id локации (ruins, hub, needles…); key — уникальный короткий ключ жителя (нужен для разговоров)
      name   имя над головой, например «Огородница Нюра»; sh — лист спрайтов: adult small kid old scav pilgrim nurse ghoul ghoulkid
      g      m/f (для грамматики при необходимости)
      greet  как встречает (одна строка, уникальная)
      bio    [два куска личной истории: откуда он, что потерял, как выживает]
      dream  цель, мечта, план на жизнь
      seek   кого или что ищет (или от кого прячется) — необязательно
      news   [два слуха: что в городе / в соседних городах]; элемент может быть [текст, условие] — показывается, когда условие верно
      world  как он видит мир: война, Vault-Tec, культ, Братство, Анклав…
      barks  3–4 коротких реплики, которые он бросает на ходу (уникальные)
      tip    необязательно: [текст, [эффекты], условие] — подсказка, облегчающая задание
  T(loc, id, keyA, keyB, lines, hint=None, effects=None, once=False, cond=None)
      разговор двух жителей по очереди (lines чередуются A, B, A, B…); подслушивание работает как у обычных (hint/effects).
"""
FOLKS = {}
TALKS = {}
_KEYS, _NAMES, _TALK_IDS = set(), set(), set()
SHEETS = ("adult", "small", "kid", "old", "scav", "pilgrim", "nurse", "ghoul", "ghoulkid")


def F(loc, key, name, sh, g, greet, bio, dream, news, world, barks, seek=None, tip=None, stroll=None):
    assert key not in _KEYS, f"ключ жителя повторён: {key}"
    assert name not in _NAMES, f"имя повторено: {name}"
    assert sh in SHEETS, f"{key}: нет листа {sh}"
    assert g in ("m", "f") and len(bio) == 2 and len(news) == 2 and 3 <= len(barks) <= 5, f"{key}: форма анкеты"
    _KEYS.add(key)
    _NAMES.add(name)
    FOLKS.setdefault(loc, []).append({"key": key, "name": name, "sh": sh, "g": g, "greet": greet, "bio": bio, "dream": dream,
                                      "news": news, "world": world, "barks": barks, "seek": seek, "tip": tip,
                                      "stroll": stroll})


def T(loc, tid, a, b, lines, hint=None, effects=None, once=False, cond=None):
    assert tid not in _TALK_IDS, f"разговор повторён: {tid}"
    assert a in _KEYS and b in _KEYS, f"{tid}: нет жителя {a} или {b}"
    _TALK_IDS.add(tid)
    roles = ["A", "B"]
    conv = {"id": tid, "pair": [a, b], "lines": [[roles[i % 2], t] for i, t in enumerate(lines)]}
    if hint:
        conv["hint"] = hint
    if effects:
        conv["effects"] = effects
    if once or hint:
        conv["once"] = True
    if cond:
        conv["if"] = cond
    TALKS.setdefault(loc, []).append(conv)
