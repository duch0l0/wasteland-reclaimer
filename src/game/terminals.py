"""
Терминалы RobCo и читаемые документы (data/terminals.json).

Терминал — меню записей. Запись может быть закрыта (lock): её открывает
пароль (если герой его узнал — флаг know_flag) или взлом — мини-игра из
Fallout 3/NV: в «дампе памяти» спрятаны слова, после каждой попытки
терминал говорит, сколько букв совпало с паролем на своих местах.
Четыре попытки, потом блокировка — останется только пароль.

Записки и голозаписи из рюкзака показываются тем же экраном.
"""
import json
import random

import pygame

from .controls import number_key

with open("data/terminals.json", "r", encoding="utf-8") as f:
    _DATA = json.load(f)
TERMINALS = _DATA["terminals"]
DOCS = _DATA["docs"]
HACK_WORDS = {int(k): [w for w in v if len(w) == int(k)] for k, v in _DATA["hack_words"].items()}

HACK_TRIES = 4
DUMP_ROWS, DUMP_COLS = 14, 12   # строк в каждом из двух столбцов «памяти», символов в строке
JUNK = "!@#$%^&*()-_=+[]{};:'\",.<>/?|\\"


class TerminalMixin:
    # ------------------------------------------------------------ открыть
    def open_terminal(self, tid):
        if tid.startswith("doc:"):   # доска объявлений и прочее, что просто читается
            self.autowalk = None
            self.open_document(tid[4:])
            return
        t = TERMINALS[tid]
        self.term = {"id": tid, "view": "menu", "sel": 0, "entry": None, "scroll": 0, "hack": None}
        self.autowalk = None
        self.log("Терминал RobCo оживает с сухим щелчком.")
        for eff in t.get("on_open", []):
            self.apply_effect(eff)

    def open_document(self, doc_id):
        d = DOCS[doc_id]
        self.term = {"id": None, "doc": doc_id, "view": "doc", "sel": 0, "entry": None, "scroll": 0, "hack": None}
        self._apply_once(f"doc_{doc_id}", d.get("effects", []))

    def close_terminal(self):
        self.term = None

    # ------------------------------------------------------------ состояние
    def term_entries(self):
        """Видимые записи текущего терминала: [(номер в данных, запись)]."""
        t = TERMINALS[self.term["id"]]
        return [(i, e) for i, e in enumerate(t["entries"]) if self.check_condition(e.get("if", {}))]

    def lock_key(self, entry):
        return f"term_{self.term['id']}_{entry['lock']['id']}"

    def is_unlocked(self, entry):
        return "lock" not in entry or self.flags.get(self.lock_key(entry) + "_open")

    def is_locked_out(self, entry):
        return self.flags.get(self.lock_key(entry) + "_lockout")

    def knows_password(self, entry):
        kf = entry["lock"].get("know_flag")
        return bool(kf and self.flags.get(kf))

    def _apply_once(self, key, effects):
        """Эффекты записи срабатывают один раз (опыт за чтение — не бесконечный)."""
        if self.flags.get(f"read_{key}"):
            return
        self.flags[f"read_{key}"] = True
        for eff in effects:
            self.apply_effect(eff)

    # ------------------------------------------------------------ действия
    def term_open_entry(self, idx):
        entries = self.term_entries()
        if not (0 <= idx < len(entries)):
            return
        i, e = entries[idx]
        self.term.update(entry=i, scroll=0, sel=idx)
        if not self.is_unlocked(e):
            self.term["view"] = "locked"
            self.term["lock_sel"] = 0
            return
        self._show_entry(i, e)

    def _show_entry(self, i, e):
        if e.get("doc"):
            self.term["view"] = "entry"
            self._apply_once(f"doc_{e['doc']}", DOCS[e["doc"]].get("effects", []))
        else:
            self.term["view"] = "entry"
        self._apply_once(f"{self.term['id']}_{i}", e.get("effects", []))

    def term_entry_text(self):
        t = TERMINALS[self.term["id"]]
        e = t["entries"][self.term["entry"]]
        return DOCS[e["doc"]]["text"] if e.get("doc") else e.get("text", "")

    def lock_options(self):
        """Пункты экрана закрытой записи: (подпись, действие)."""
        e = TERMINALS[self.term["id"]]["entries"][self.term["entry"]]
        opts = []
        if self.knows_password(e):
            opts.append((f"Ввести пароль: {e['lock']['password']}", self._unlock_current))
        if not self.is_locked_out(e):
            opts.append(("Взломать", self._start_hack))
        opts.append(("Назад", self.term_back))
        return opts

    def _unlock_current(self):
        e = TERMINALS[self.term["id"]]["entries"][self.term["entry"]]
        self.flags[self.lock_key(e) + "_open"] = True
        self.log("Доступ разрешён.")
        self._show_entry(self.term["entry"], e)

    def term_back(self):
        if self.term.get("doc") or self.term["view"] == "menu":
            self.close_terminal()
        else:
            self.term.update(view="menu", entry=None, hack=None, scroll=0)

    # ------------------------------------------------------------ взлом
    def _start_hack(self):
        e = TERMINALS[self.term["id"]]["entries"][self.term["entry"]]
        pw = e["lock"]["password"]
        pool = [w for w in HACK_WORDS.get(len(pw), []) if w != pw]
        rnd = random.Random()
        words = rnd.sample(pool, min(len(pool), e["lock"].get("words", 12) - 1)) + [pw]
        rnd.shuffle(words)
        rows = rnd.sample(range(DUMP_ROWS * 2), len(words))  # у каждого слова своя строка
        dump = []
        placed = {}
        for r in range(DUMP_ROWS * 2):
            line = [rnd.choice(JUNK) for _ in range(DUMP_COLS)]
            if r in rows:
                w = words[rows.index(r)]
                start = rnd.randint(0, DUMP_COLS - len(w))
                line[start:start + len(w)] = list(w)
                placed[w] = (r, start)
            dump.append("".join(line))
        self.term["view"] = "hack"
        self.term["hack"] = {"password": pw, "words": words, "placed": placed, "dump": dump,
                             "tries": HACK_TRIES, "tried": [], "log": [], "cursor": 0,
                             "base": rnd.randrange(0xF000, 0xFF00, 0x10)}

    def hack_guess(self, word):
        h = self.term["hack"]
        if word in h["tried"] or h["tries"] <= 0:
            return
        e = TERMINALS[self.term["id"]]["entries"][self.term["entry"]]
        h["log"].append(f">{word}")
        if word == h["password"]:
            h["log"] += [">Точное совпадение!", ">Вход..."]
            self.flags[self.lock_key(e) + "_open"] = True
            self.log("Терминал взломан.")
            self.gain_xp(10)
            self._show_entry(self.term["entry"], e)
            return
        likeness = sum(a == b for a, b in zip(word, h["password"]))
        h["tried"].append(word)
        h["tries"] -= 1
        h["log"] += [">Отказ в доступе.", f">Совпадение={likeness}"]
        if h["tries"] <= 0:
            self.flags[self.lock_key(e) + "_lockout"] = True
            h["log"].append(">ТЕРМИНАЛ ЗАБЛОКИРОВАН")
            self.log("Терминал заблокирован. Остаётся только узнать пароль.")

    def hack_words_left(self):
        h = self.term["hack"]
        return [w for w in h["words"] if w not in h["tried"]]

    # ------------------------------------------------------------ клавиши
    def terminal_key(self, key):
        t = self.term
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            if t["view"] in ("entry", "locked", "hack") and not t.get("doc"):
                t.update(view="menu", hack=None, scroll=0)
            else:
                self.close_terminal()
            return
        view = t["view"]
        if view == "menu":
            n = len(self.term_entries())
            if key in (pygame.K_UP, pygame.K_w):
                t["sel"] = (t["sel"] - 1) % n
            elif key in (pygame.K_DOWN, pygame.K_s):
                t["sel"] = (t["sel"] + 1) % n
            elif key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.term_open_entry(t["sel"])
            else:
                idx = number_key(key)
                if idx is not None:
                    self.term_open_entry(idx)
        elif view in ("entry", "doc"):
            if key in (pygame.K_UP, pygame.K_w):
                t["scroll"] = max(0, t["scroll"] - 1)
            elif key in (pygame.K_DOWN, pygame.K_s):
                t["scroll"] += 1
            elif key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.term_back()
        elif view == "locked":
            opts = self.lock_options()
            if key in (pygame.K_UP, pygame.K_w):
                t["lock_sel"] = (t["lock_sel"] - 1) % len(opts)
            elif key in (pygame.K_DOWN, pygame.K_s):
                t["lock_sel"] = (t["lock_sel"] + 1) % len(opts)
            elif key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                opts[t["lock_sel"]][1]()
        elif view == "hack":
            h = t["hack"]
            left = self.hack_words_left()
            if h["tries"] <= 0:
                if key in (pygame.K_RETURN, pygame.K_SPACE):
                    t.update(view="menu", hack=None)
                return
            if key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                h["cursor"] = (h["cursor"] - 1) % len(left)
            elif key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d, pygame.K_s, pygame.K_TAB):
                h["cursor"] = (h["cursor"] + 1) % len(left)
            elif key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.hack_guess(left[h["cursor"] % len(left)])
