"""
Аудит квестов без запуска игры: по data/*.json и STORY_STEPS для каждого квеста из data/quests.json —
кто выдаёт и где, какие пути ведут к выполнению, закрыт ли каждый путь навыком/перком, награда,
связи с другими квестами (флаги одного квеста в условиях другого).

  .venv/bin/python tools/quest_audit.py              — таблица по всем квестам
  .venv/bin/python tools/quest_audit.py sq_thermo    — подробно по одному
  .venv/bin/python tools/quest_audit.py --json out.json
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src.game.quests import STORY_STEPS, QUESTS  # noqa: E402

GATE_KEYS = ("skill", "perk", "min_level", "karma_ge", "karma_lt", "rep_ge", "title")


def load(name):
    with open(f"data/{name}.json", encoding="utf-8") as f:
        return json.load(f)


def cond_flags(cond):
    """Флаги, которые читает условие (if)."""
    out = set()
    if not isinstance(cond, dict):
        return out
    for k in ("flag", "not_flag"):
        if k in cond:
            out.add(cond[k])
    for k in ("flags_any", "flags_all", "not_flags"):
        out.update(cond.get(k, []))
    for k in ("flag_eq", "flag_ge"):
        if k in cond:
            out.add(cond[k][0])
    if "count_flags" in cond:
        out.update(cond["count_flags"][0])
    return out


def cond_quests(cond):
    out = set()
    if isinstance(cond, dict):
        for k in ("stage", "stage_lt"):
            if k in cond:
                out.add(cond[k][0])
    return out


def gates(cond):
    if not isinstance(cond, dict):
        return []
    return [f"{k}={cond[k]}" for k in GATE_KEYS if k in cond]


class Option:
    """Реплика/пункт терминала/событие со своими эффектами и условием (с учётом условий узла выше)."""

    def __init__(self, src, label, cond, effects):
        self.src, self.label, self.cond, self.effects = src, label, cond, effects

    def sets_flags(self):
        return {e["flag"] for e in self.effects if e.get("type") in ("set_flag", "inc")}

    def stages(self):
        return [(e["id"], e["stage"]) for e in self.effects if e.get("type") == "quest"]


def walk_dialogues():
    opts = []
    for did, d in load("dialogues").items():
        if did.startswith("_") or not isinstance(d, dict):
            continue
        start_conds = {s.get("node"): s.get("if") for s in d.get("start", []) if isinstance(s, dict)}
        for nid, node in d.get("nodes", {}).items():
            ncond = node.get("if") or start_conds.get(nid)
            if node.get("effects"):
                opts.append(Option(f"dlg:{did}/{nid}", "(узел)", ncond, node["effects"]))
            for o in node.get("options", []):
                c = dict(ncond or {})
                c.update(o.get("if") or {})
                opts.append(Option(f"dlg:{did}/{nid}", o.get("label", ""), c, o.get("effects", [])))
    return opts


def walk_any(obj, src, cond=None, out=None):
    """Терминалы, слайды, сроки: любой список эффектов (effects, on_end…) внутри словаря."""
    out = [] if out is None else out
    if isinstance(obj, dict):
        c = obj.get("if", cond)
        for k, v in obj.items():
            if isinstance(v, list) and v and all(isinstance(e, dict) and "type" in e for e in v):
                out.append(Option(f"{src}/{k}", obj.get("label", ""), c, v))
            else:
                walk_any(v, f"{src}/{k}" if src.count("/") < 2 else src, c, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_any(v, src, cond, out)
    return out


def code_refs():
    """set_stage(...) и flags[...] = в коде src/ — стадии и флаги, которые ставит Python."""
    stages, flags = defaultdict(set), defaultdict(set)
    for path in glob.glob("src/**/*.py", recursive=True):
        txt = open(path, encoding="utf-8").read()
        for m in re.finditer(r'set_stage\("(\w+)",\s*(\d+)\)', txt):
            stages[m.group(1)].add((int(m.group(2)), path))
        for m in re.finditer(r'\bf(?:lags)?\["([\w{}]+)"\]\s*=', txt):
            flags[m.group(1)].add(path)
        for m in re.finditer(r'"type":\s*"set_flag",\s*"flag":\s*"(\w+)"', txt):
            flags[m.group(1)].add(path)
    return stages, flags


def npc_places():
    where = defaultdict(set)
    for f in glob.glob("data/maps/*.json"):
        lid = os.path.basename(f)[:-5]
        for n in json.load(open(f, encoding="utf-8")).get("npcs", []):
            where[n[0]].add(lid)
    return where


def build():
    global walk_cache
    opts = walk_dialogues()
    walk_cache = [o for o in opts if o.src.startswith("dlg:")]
    for name in ("terminals", "slides", "deadlines", "caravan_events"):
        if os.path.exists(f"data/{name}.json"):
            opts += walk_any(load(name), name)
    code_stages, code_flags = code_refs()
    places = npc_places()
    steps = {q: s for q, s in STORY_STEPS}

    flag_setters = defaultdict(list)
    for o in opts:
        for fl in o.sets_flags():
            flag_setters[fl].append(o)

    def step_flags(cond):
        if isinstance(cond, list):
            return [c for c in cond]
        return [cond]

    report = {}
    for qid, q in QUESTS.items():
        done = q.get("done", 100)
        stage_opts = [(st, o) for o in opts for (qq, st) in o.stages() if qq == qid]
        # флаги, через которые STORY_STEPS двигает стадии
        flag_stage = []
        for st, cond in steps.get(qid, []):
            for fl in step_flags(cond):
                flag_stage.append((st, fl))
        q_flags = {fl for _, fl in flag_stage if not fl.startswith("loc:")}
        # реплики квеста: ставят его стадию или его флаги
        own = {id(o): o for _, o in stage_opts}
        for fl in q_flags:
            for o in flag_setters.get(fl, []):
                own[id(o)] = o
        own = list(own.values())
        for o in own:
            q_flags |= o.sets_flags()

        # пути к выполнению
        done_paths = [o for st, o in stage_opts if st >= done]
        done_flags = [fl for st, fl in flag_stage if st >= done]
        for fl in done_flags:
            done_paths += flag_setters.get(fl, [])
        code_done = [p for st, p in code_stages.get(qid, ()) if st >= done]
        code_done += [p for fl in done_flags for p in code_flags.get(fl, ())]
        loc_done = [fl for fl in done_flags if fl.startswith("loc:")]
        free = [o for o in done_paths if not gates(o.cond)]
        # кто выдаёт: самая ранняя стадия
        first = min([st for st, _ in stage_opts] + [st for st, _ in flag_stage] + [10 ** 9])
        givers = sorted({o.src.split("/")[0] for st, o in stage_opts if st == first} |
                        {o.src.split("/")[0] for st, fl in flag_stage if st == first for o in flag_setters.get(fl, [])})
        giver_places = sorted({pl for g in givers if g.startswith("dlg:") for pl in places.get(g[4:], ())})
        # награда на путях выполнения
        xp = [sum(e.get("amount", 0) for e in o.effects if e.get("type") == "xp") for o in done_paths] or [0]
        caps = [sum(e.get("count", 0) for e in o.effects if e.get("type") == "caps" or
                    (e.get("type") == "give" and e.get("item") == "крышки")) for o in done_paths] or [0]
        items = sorted({e["item"] for o in done_paths for e in o.effects
                        if e.get("type") == "give" and e.get("item") != "крышки"})
        report[qid] = {
            "title": q["title"], "main": bool(q.get("main")), "stages": sorted(int(s) for s in q["stages"]),
            "givers": givers, "places": giver_places, "flags": sorted(q_flags),
            "done_paths": sorted({f"{o.src} «{o.label[:40]}» {' '.join(gates(o.cond))}".strip() for o in done_paths}),
            "done_free": len({o.src + o.label for o in free}), "done_total": len({o.src + o.label for o in done_paths}),
            "done_code": sorted(set(code_done)), "done_loc": loc_done,
            "xp_max": max(xp), "caps_max": max(caps), "items": items,
            "reads": set(), "read_by": set(),
            "_own": own, "dlgs": {o.src.split("/")[0] for o in own if o.src.startswith("dlg:")},
        }

    # связи: флаги/стадии квеста A в условиях реплик квеста B
    owner = defaultdict(set)
    for qid, r in report.items():
        for fl in r["flags"]:
            owner[fl].add(qid)
    for qid, r in report.items():
        dl_opts = [o for o in walk_cache if o.src.split("/")[0] in r["dlgs"]]
        for o in r["_own"] + dl_opts:
            for fl in cond_flags(o.cond):
                for other in owner.get(fl, ()):
                    if other != qid:
                        r["reads"].add(other)
                        report[other]["read_by"].add(qid)
            for other in cond_quests(o.cond):
                if other != qid and other in report:
                    r["reads"].add(other)
                    report[other]["read_by"].add(qid)
    # отклик мира: флаги квеста, которые читают другие файлы (барки, слухи, перемены городов, эпилог) —
    # упоминания минус места, где флаг ставится
    texts = {os.path.basename(p)[:-5]: open(p, encoding="utf-8").read() for p in glob.glob("data/*.json")
             if not p.endswith("quests.json")}
    src_py = "\n".join(open(p, encoding="utf-8").read() for p in glob.glob("src/**/*.py", recursive=True))
    for qid, r in report.items():
        echo = defaultdict(int)
        for fl in r["flags"]:
            if len(fl) < 5:
                continue
            for name, txt in texts.items():
                n = txt.count(f'"{fl}"') - txt.count(f'"flag": "{fl}"}}') - len(re.findall(
                    rf'"type":\s*"set_flag",\s*"flag":\s*"{re.escape(fl)}"', txt))
                if name == "dialogues":     # свои диалоги не в счёт
                    n = sum(1 for o in walk_cache if fl in cond_flags(o.cond) and
                            o.src.split("/")[0] not in r["dlgs"])
                if n > 0:
                    echo[name] += n
            n = src_py.count(f'"{fl}"') - src_py.count(f'["{fl}"] =')
            if n > 0:
                echo["код"] += n
        r["echo"] = dict(echo)
        # главный сюжет: флаги квеста двигают mq_*
        r["feeds_main"] = sorted(m for m, s in steps.items() if m.startswith("mq_") and m != qid and
                                 any(fl in r["flags"] for _, c in s for fl in step_flags(c)))
    for r in report.values():
        r.pop("_own")
        r.pop("dlgs")
        r["reads"], r["read_by"] = sorted(r["reads"]), sorted(r["read_by"])
    return report


def choices():
    """Развилки: узел диалога/терминала, где хотя бы две реплики ставят разные флаги и хотя бы одна
    двигает квест, карму или репутацию. Для каждой ветки — сколько мест читает её флаги (кроме места,
    где флаг ставится). Ветка, которую никто не читает, — пустой выбор."""
    build()            # заполняет walk_cache
    opts = list(walk_cache)
    for name in ("terminals",):
        opts += walk_any(load(name), name)
    texts = {os.path.basename(p)[:-5]: open(p, encoding="utf-8").read() for p in glob.glob("data/*.json")}
    src_py = "\n".join(open(p, encoding="utf-8").read() for p in glob.glob("src/**/*.py", recursive=True))
    tools_py = "\n".join(open(p, encoding="utf-8").read() for p in glob.glob("tools/build_*.py"))

    def readers(fl):
        out = {}
        for name, txt in texts.items():
            n = txt.count(f'"{fl}"') - len(re.findall(rf'"type":\s*"set_flag",\s*"flag":\s*"{re.escape(fl)}"', txt))
            if n > 0:
                out[name] = n
        n = src_py.count(f'"{fl}"') - src_py.count(f'["{fl}"] =')
        if n > 0:
            out["код"] = n
        return out

    # эффекты узла, в который ведёт реплика, — часть её решения (решение часто «проваливается» в узел)
    D = load("dialogues")
    for o in opts:
        o.full = list(o.effects)
        if o.src.startswith("dlg:"):
            did = o.src[4:].split("/")[0]
            for node in D.get(did, {}).get("nodes", {}).values():
                for oo in node.get("options", []):
                    if oo.get("label", "") == o.label and oo.get("next"):
                        nxt = D[did]["nodes"].get(oo["next"], {})
                        o.full += nxt.get("effects", [])
                        if len(nxt.get("options", [])) == 1:     # единственная реплика дальше — тоже итог
                            o.full += nxt["options"][0].get("effects", [])
        else:
            o.full = list(o.effects)
    Option.sets_flags = lambda self: {e["flag"] for e in getattr(self, "full", self.effects)
                                      if e.get("type") in ("set_flag", "inc", "npc_leave") and "flag" in e}
    by_node = defaultdict(list)
    for o in opts:
        if o.label != "(узел)":
            by_node[o.src].append(o)
    rows = []
    for src, os_ in by_node.items():
        branches = [o for o in os_ if o.sets_flags()]
        if len({frozenset(o.sets_flags()) for o in branches}) < 2:
            continue
        weighty = any(e.get("type") in ("quest", "karma", "rep", "town_fight", "fight", "join_ally", "npc_leave")
                      for o in branches for e in o.full)
        if not weighty:
            continue
        common = set.intersection(*[o.sets_flags() for o in branches])
        out = []
        for o in branches:
            own = o.sets_flags() - common
            rd = {fl: readers(fl) for fl in own}
            out.append((o.label[:46], sorted(own), rd))
        rows.append((src, out))
    return rows


def main():
    args = sys.argv[1:]
    if "--choices" in args:
        rows = choices()
        empty = 0
        for src, out in rows:
            print(src)
            for label, own, rd in out:
                total = sum(sum(v.values()) for v in rd.values())
                if own and total == 0:
                    empty += 1
                where = ", ".join(f"{fl}:{'/'.join(f'{k}{v}' for k, v in r.items()) or '—'}" for fl, r in rd.items())
                print(f"   {'ПУСТО ' if own and total == 0 else '      '}«{label}» → {where or '(общие флаги)'}")
        print(f"\nразвилок {len(rows)}, пустых веток {empty}")
        return
    rep = build()
    if "--json" in args:
        path = args[args.index("--json") + 1]
        json.dump(rep, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("записано:", path)
        return
    if args:
        for qid in args:
            print(json.dumps(rep[qid], ensure_ascii=False, indent=1))
        return
    print(f"{'квест':16} {'назв.':28} {'где':22} пути(своб) XP  крыш связи→/←  замечания")
    for qid, r in rep.items():
        notes = []
        if not r["givers"]:
            notes.append("нет выдачи")
        if not r["done_total"] and not r["done_code"] and not r["done_loc"]:
            notes.append("НЕ ЗАВЕРШИТЬ")
        elif r["done_total"] and not r["done_free"] and not r["done_code"]:
            notes.append("только через навык")
        if not r["reads"] and not r["read_by"] and not r["feeds_main"]:
            notes.append("изолирован")
        if sum(r["echo"].values()) < 2:
            notes.append("мир не замечает")
        print(f"{qid:16} {r['title'][:28]:28} {','.join(r['places'])[:22]:22} "
              f"{r['done_total']:>3}({r['done_free']})  {r['xp_max']:>4} {r['caps_max']:>4} "
              f"{len(r['reads'])}/{len(r['read_by'])}{'+M' if r['feeds_main'] else '  '} эхо{sum(r['echo'].values()):>3}  {'; '.join(notes)}")


if __name__ == "__main__":
    main()
