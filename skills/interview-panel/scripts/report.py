#!/usr/bin/env python3
"""interview-panel: the deterministic half of the debrief.

The model rates each answer (judgement) and writes the prose. This script does everything
that is a fixed rule in references/rubric.md: assigning levels, edge, depth and breadth from topic areas,
bars, each panelist's feedback picks,
strongest/weakest, radar points, filler counts, the session record, and filling the HTML template.

Usage:
  report.py score   session.json             # print computed results as JSON (spoken summary)
  report.py build   session.json -o out.html # render the report, print the session record
  report.py check   session.json             # mechanical transcript checks (subset of evals.md)
  report.py selftest

Python 3.8+, standard library only. session.json format: references/session-schema.md.
"""
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "references" / "report-template.html"

LEVELS = ["J", "I", "S", "St"]
NAMES = {"J": "Junior", "I": "Intermediate", "S": "Senior", "St": "Staff"}
# The radar's seven generic axes, identical in both modes, in radar order.
AXES = ["depth", "breadth", "design", "problem", "tradeoffs", "edge", "communication"]
LABELS = {
    "depth": "Depth", "breadth": "Breadth", "design": "Design", "problem": "Problem solving",
    "tradeoffs": "Trade-offs", "edge": "Reasoning at the edge", "communication": "Communication",
}
RADAR_LABELS = {"problem": "Problem solving", "edge": "At the edge"}  # short enough for the radar
# Radar points per axis (in radar order) for J, I, S, St. Centre 170,170.
RADAR = [
    ["170,140", "170,110", "170,80", "170,50"],
    ["193,151", "217,133", "240,114", "264,95"],
    ["199,177", "228,183", "258,190", "287,197"],
    ["183,197", "196,224", "209,251", "222,278"],
    ["157,197", "144,224", "131,251", "118,278"],
    ["141,177", "112,183", "82,190", "53,197"],
    ["147,151", "123,133", "100,114", "76,95"],
]
CENTRE = "170,170"
# Feedback lens per panelist (generic axes, both modes).
KEY_SKILLS = {"Leslie": ["depth", "design", "edge"], "Dennis": ["problem", "breadth", "design"],
              "Freda": ["tradeoffs", "communication", "breadth"]}
# Keys from records v1-v3, mapped onto the generic axes (Phase 0 reads old records).
OLD_KEYS = {"depth": "depth", "concepts": "breadth", "design": "design", "coding": "problem",
            "debugging": "problem", "tradeoffs": "tradeoffs", "edge": "edge", "communication": "communication"}
FILLERS = ["basically", "actually", "literally", "you know", "i mean", "kind of", "sort of", "um", "uh", "erm"]
FOOTNOTE = ("Panel names nod to Leslie Lamport (logical clocks, Paxos), Dennis Ritchie (C, Unix) "
            "and Fred Brooks (The Mythical Man-Month).")


def idx(level):
    return LEVELS.index(level)


def effective(ans):
    """Level an answer demonstrates after the hinted, skipped and wrong rules (rubric: Rating)."""
    flag = ans.get("flag")
    if flag == "skipped":
        return "J"
    lvl = ans["level"]
    if flag in ("wrong", "bluff"):
        lvl = "J"
    if flag == "hinted":
        lvl = LEVELS[max(0, idx(lvl) - 1)]
    return lvl


def assign(answers):
    """Rubric: Assigning the level. Returns level or 'n/o'."""
    if not answers:
        return "n/o"
    effs = [effective(a) for a in answers]
    best = max(range(len(effs)), key=lambda i: idx(effs[i]))
    level = effs[best]
    # Lower by one if a later answer on the same topic demonstrated a lower level.
    topic = answers[best].get("topic")
    if topic is not None:
        for a, e in zip(answers[best + 1:], effs[best + 1:]):
            if a.get("topic") == topic and idx(e) < idx(level):
                level = LEVELS[max(0, idx(level) - 1)]
                break
    return level


def edge_level(answers):
    """Rubric: Thinking skills, edge. Most common floor rating, tie -> lower. n/o without floors."""
    for a in answers:
        if a.get("floor") and "edge" not in a and a.get("flag") not in ("wrong", "bluff"):
            raise SystemExit(f"answer with floor {a['floor']!r} needs an 'edge' rating")
    rated = [("J" if a.get("flag") in ("wrong", "bluff") else a["edge"]) for a in answers if a.get("floor")]
    if not rated:
        return "n/o"
    counts = Counter(rated)
    top = max(counts.values())
    return min((l for l, c in counts.items() if c == top), key=idx)


def floor_of(key, answers, level):
    for a in answers:
        if a.get("floor"):
            return a["floor"]
    if level == "St":
        return "none"
    return "not reached"


def before_floor(answers):
    """Rubric: an area's level comes from answers before its first floor; a first-answer floor rates it."""
    for i, a in enumerate(answers):
        if a.get("floor"):
            return answers[:i] if i else answers[:1]
    return answers


def keys_of(a):
    """An answer rates its key and, optionally, one or more generic axes named in `also`."""
    also = a.get("also", [])
    return [a["key"]] + ([also] if isinstance(also, str) else list(also))


def breadth_level(levels):
    """Rubric: the highest level that at least two-thirds of the rated areas reach."""
    if not levels:
        return "n/o"
    for lvl in reversed(LEVELS):
        if 3 * sum(1 for l in levels if idx(l) >= idx(lvl)) >= 2 * len(levels):
            return lvl
    return "J"


def score(s):
    mode = s["mode"]
    target = s.get("target", "S")
    answers = s.get("answers", [])
    by_key = {}
    for a in answers:
        for k in keys_of(a):
            by_key.setdefault(k, []).append(a)

    areas = s.get("areas", []) if mode == "topics" else []
    area_keys = [a["key"] for a in areas]
    if set(area_keys) & set(AXES):
        raise SystemExit("an area key may not reuse a generic axis name")
    core = [a["key"] for a in areas if a.get("core")]
    if len(core) > 3:
        raise SystemExit("rubric: at most three core areas")

    known = set(area_keys) | ({"design", "problem", "tradeoffs"} if mode == "topics"
                              else {"depth", "breadth", "design", "problem", "tradeoffs"})
    for a in answers:
        bad = [k for k in keys_of(a) if k not in known]
        if bad:
            raise SystemExit(f"unknown or disallowed key(s) {bad} in answer {a} (mode {mode})")
        if mode == "topics" and a["key"] in area_keys and a.get("flag") and not a.get("floor"):
            raise SystemExit(f"topics mode: a {a['flag']} answer in {a['key']!r} is a floor; add 'floor' and 'edge'")
    levels = {k: assign(before_floor(by_key.get(k, []))) for k in area_keys}
    rated_areas = [k for k in area_keys if levels[k] != "n/o"]
    for k in AXES:
        if k == "edge":
            levels[k] = edge_level(answers)
        elif k == "communication":
            levels[k] = s.get("communication", "n/o")  # rated from all answers, not stepped
        elif mode == "topics" and k == "depth":
            levels[k] = max((levels[a] for a in rated_areas), key=idx) if rated_areas else "n/o"
        elif mode == "topics" and k == "breadth":
            levels[k] = breadth_level([levels[a] for a in rated_areas])
        else:
            levels[k] = assign(by_key.get(k, []))

    def bar(k):
        if k in area_keys and k not in core:
            return LEVELS[max(0, idx(target) - 1)]
        return target

    # Panel feedback picks (rubric: Panel feedback). The model writes the words; this picks the skills.
    panel = s.get("panel", ["Leslie", "Dennis", "Freda"])
    feedback = {}
    taken = {"landed": set(), "work_on": set()}
    for name in panel:
        keys = list(KEY_SKILLS[name])
        if name == "Leslie" and "Dennis" not in panel:
            keys += [k for k in KEY_SKILLS["Dennis"] if k not in keys]
        lens = [k for k in keys if levels.get(k) != "n/o"]
        if not lens:  # all key skills n/o: comment on any probed axis
            lens = [k for k in AXES if levels[k] != "n/o"]
        if not lens:
            continue
        lens.sort(key=AXES.index)  # ties go by radar order

        def choose(rank, slot, avoid=()):
            ordered = sorted(lens, key=rank)
            for k in ordered:
                if k not in taken[slot] and k not in avoid:
                    return k
            for k in ordered:
                if k not in avoid:
                    return k
            return ordered[0]

        landed = choose(lambda k: (-idx(levels[k]), AXES.index(k)), "landed")
        # Work on: furthest below target; when nothing is below, the lowest level (aim at the next one).
        work_on = choose(lambda k: (-(idx(target) - idx(levels[k])), idx(levels[k]), AXES.index(k)),
                         "work_on", avoid=(landed,))
        taken["landed"].add(landed)
        taken["work_on"].add(work_on)
        feedback[name] = {"landed": landed, "work_on": work_on, "lens": lens,
                          "work_on_gap": max(0, idx(target) - idx(levels[work_on]))}

    def answers_for(k):
        if mode == "topics" and k in ("depth", "breadth"):
            return [a for ak in rated_areas for a in before_floor(by_key.get(ak, []))]
        return by_key.get(k, [])

    def pick(pool, order, best):
        pool = [k for k in pool if levels[k] != "n/o"]
        if not pool:
            return None
        extreme = (max if best else min)(idx(levels[k]) for k in pool)
        tied = [k for k in pool if idx(levels[k]) == extreme]
        return max(tied, key=lambda k: (sum(1 for a in answers_for(k) if idx(effective(a)) == extreme),
                                        -order.index(k)))

    out = {
        "mode": mode, "target": target, "levels": levels, "feedback": feedback,
        "strongest": pick(AXES, AXES, True), "weakest": pick(AXES, AXES, False),
        # An unprobed axis is skipped in the polygon; its label says "not probed".
        "candidate_points": " ".join(RADAR[i][idx(levels[k])] for i, k in enumerate(AXES) if levels[k] != "n/o"),
        "target_points": " ".join(RADAR[i][idx(target)] for i in range(len(AXES))),
        "not_probed": [k for k in AXES if levels[k] == "n/o"],
    }
    if mode == "topics":
        out["areas"] = areas
        out["breadth"] = {"k": sum(1 for k in rated_areas if idx(levels[k]) >= idx("I")), "n": len(rated_areas),
                          "at_target": sum(1 for k in rated_areas if idx(levels[k]) >= idx(target))}
        out["bars"] = {k: bar(k) for k in area_keys}
        out["core"] = core
        out["floors"] = {k: floor_of(k, by_key.get(k, []), levels[k]) for k in area_keys}
        out["strongest_area"] = pick(area_keys, area_keys, True)
        out["weakest_area"] = pick(area_keys, area_keys, False)
    out["fillers"] = fillers(s)
    out["record"] = record(s, out)
    return out


def fillers(s):
    text = " ".join(t["text"] for t in s.get("transcript", []) if t.get("speaker") == "candidate").lower()
    counts = {f: len(re.findall(r"\b" + re.escape(f) + r"\b", text)) for f in FILLERS}
    return {f: c for f, c in sorted(counts.items(), key=lambda x: -x[1]) if c >= 3}


def record(s, out):
    lv = out["levels"]
    head = (f"date: {s['date']} | target: {s.get('target_label', NAMES[out['target']])} | "
            f"mode: {s.get('length', 'full')} | format: {out['mode']} | panel: {', '.join(s.get('panel', ['Leslie', 'Dennis', 'Freda']))}")
    focus = " ".join(f"{i}) {f}" for i, f in enumerate(s.get("focus", []), 1))
    lines = ["interview-panel record v4", head, "levels: " + " ".join(f"{k}={lv[k]}" for k in AXES)]
    if out["mode"] == "topics":
        lines.append("topics: " + " ".join(f"{a['key']}{'*' if a.get('core') else ''}={lv[a['key']]}"
                                           for a in out["areas"]))
        lines.append(f"breadth: {out['breadth']['k']}/{out['breadth']['n']}")
    lines.append(f"focus: {focus}")
    return "\n".join(lines)


# ---------- rendering ----------

def e(x):
    return html.escape(str(x), quote=True)


def evidence(s, k):
    p = s.get("prose", {}).get(k, {})
    quote = p.get("quote", "")
    q = f'<blockquote>"{e(quote)}"</blockquote>' if quote else ""
    return q + e(p.get("why", "")), e(p.get("next", ""))


def build(s):
    out = score(s)
    t = TEMPLATE.read_text()
    mode = out["mode"]
    lv = out["levels"]
    keep, drop = ("CV mode", "topics mode") if mode == "cv" else ("topics mode", "CV mode")
    t = re.sub(r"\s*<!-- MODE SECTION: " + drop + r" -->.*?<!-- END MODE SECTION -->", "", t, flags=re.S)
    t = re.sub(r"\s*<!-- (MODE SECTION: " + keep + r"|END MODE SECTION) -->", "", t)
    t = re.sub(r"<!--.*?-->\n?", "", t, flags=re.S)  # authoring notes are not part of the report

    def lvl(k):
        return NAMES.get(lv[k], lv[k])

    rows_skills = rows_topics = ""
    for k in AXES:
        if lv[k] == "n/o":
            rows_skills += f"<tr><td>{LABELS[k]}</td><td>not probed</td><td>-</td><td>-</td></tr>\n"
            continue
        ev, nxt = evidence(s, k)
        rows_skills += f"<tr><td>{LABELS[k]}</td><td>{lvl(k)}</td><td>{ev}</td><td>{nxt}</td></tr>\n"
    if mode == "topics":
        for a in out["areas"]:
            k = a["key"]
            kind = "core" if a.get("core") else "peripheral"
            if lv[k] == "n/o":
                rows_topics += f"<tr><td>{e(a['label'])} ({kind})</td><td>not probed</td><td>-</td><td>-</td><td>-</td></tr>\n"
                continue
            ev, nxt = evidence(s, k)
            rows_topics += (f"<tr><td>{e(a['label'])} ({kind})</td><td>{lvl(k)} / {NAMES[out['bars'][k]]}</td>"
                            f"<td>{ev}</td><td>{e(out['floors'][k])}</td><td>{nxt}</td></tr>\n")

    lines_by = s.get("feedback_lines", {})
    cards = ""
    for n, f in out["feedback"].items():
        txt = lines_by.get(n, {})
        cards += (f'<div class="card feedback"><b>{e(n)}</b>'
                  f'<p><i>What landed ({LABELS[f["landed"]]}):</i> {e(txt.get("landed", ""))}</p>'
                  f'<p><i>Work on ({LABELS[f["work_on"]]}):</i> {e(txt.get("work_on", ""))}</p></div>\n')
    c = s.get("coaching", {})
    fill = ", ".join(f'"{f}" x{n}' for f, n in out["fillers"].items()) or "none used three or more times"
    grammar = "".join(f"<p>{e(g['said'])} → {e(g['better'])}</p>\n" for g in c.get("grammar", []))
    overused = "; ".join(f"{e(w['word'])} (try {e(w['try'])})" for w in c.get("overused", [])) or "none"
    stronger = "".join(f"<p><i>{e(a['question'])}</i><br>{e(a['answer'])}</p>\n" for a in c.get("stronger", []))
    tl = NAMES[out["target"]]
    label_of = {a["key"]: a["label"] for a in out.get("areas", [])}
    subs = {
        "DATE": s["date"], "TARGET": s.get("target_label", tl), "MODE": f"{s.get('length', 'full')}, {mode}",
        "PANEL": ", ".join(s.get("panel", ["Leslie", "Dennis", "Freda"])),
        "TARGET_LEVEL": tl,
        "TARGET_POINTS": out["target_points"], "CANDIDATE_POINTS": out["candidate_points"],
        "STRONGEST": LABELS.get(out["strongest"], "-"), "WEAKEST": LABELS.get(out["weakest"], "-"),
        "K": out.get("breadth", {}).get("k", ""), "N": out.get("breadth", {}).get("n", ""),
        "K_TARGET": out.get("breadth", {}).get("at_target", ""),
        "STRONGEST_AREA": e(label_of.get(out.get("strongest_area"), "-")),
        "WEAKEST_AREA": e(label_of.get(out.get("weakest_area"), "-")),
        "AREA_LIST": e(", ".join(a["label"] for a in out.get("areas", []))),
        "NOT_PROBED": e(", ".join(LABELS[k] for k in out["not_probed"]) or "none"),
        "ROWS_SKILLS": rows_skills, "ROWS_TOPICS": rows_topics,
        "FEEDBACK_CARDS": cards, "FILLERS_WITH_COUNTS": fill, "GRAMMAR_LINES": grammar or "<p>none noted</p>",
        "OVERUSED": overused, "STRONGER_ANSWERS": stronger,
        "SESSION_RECORD": e(out["record"]), "EASTER_EGG_FOOTNOTE": FOOTNOTE,
    }
    for i, k in enumerate(AXES, 1):
        subs[f"AXIS_{i}"] = RADAR_LABELS.get(k, LABELS[k]) + (" (n/o)" if lv[k] == "n/o" else "")
    for k, v in subs.items():
        t = t.replace("{{" + k + "}}", str(v))
    hit = VERDICT_WORDS.search(cards)  # feedback only; a candidate quote may legitimately say "verdict"
    if hit:
        raise SystemExit(f"hiring-verdict language in the panel feedback: {hit.group(0)!r}")
    left = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", t)))
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    return t, out


# ---------- mechanical transcript checks ----------

NO_QUESTION_OK = {"intro", "hint", "answer"}
VERDICT_WORDS = re.compile(r"\b(strong (yes|no)|no hire|would hire|would not hire|wouldn't hire|hiring decision|verdicts?)\b", re.I)
PRAISE = re.compile(r"\b(great|excellent|exactly|good point|well done|nice answer|perfect|spot on)\b", re.I)
MD = re.compile(r"^\s*([-*] |#{1,6} |\d+\. |\|)", re.M)


def check(s):
    fails = []
    panel = s.get("panel", ["Leslie", "Dennis", "Freda"])
    run, prev, streak = 0, None, 0
    for n, t in enumerate(s.get("transcript", []), 1):
        sp, text, kind = t.get("speaker"), t.get("text", ""), t.get("kind", "question")
        if sp == "candidate":
            continue
        if not text.startswith(f"{sp} here."):
            fails.append(f"turn {n}: does not start with '{sp} here.'")
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        q = prose.count("?")
        if q != 1 and not (q == 0 and kind in NO_QUESTION_OK):
            fails.append(f"turn {n}: {q} question marks (kind={kind})")
        if MD.search(prose):
            fails.append(f"turn {n}: markdown in a spoken turn")
        for block in re.findall(r"```.*?\n(.*?)```", text, flags=re.S):
            if len(block.strip().splitlines()) > 15:
                fails.append(f"turn {n}: code block over 15 lines")
        if s["mode"] == "topics" and "```" in text:
            fails.append(f"turn {n}: code snippet in topics mode")
        if PRAISE.search(prose):
            fails.append(f"turn {n}: possible praise: {PRAISE.search(prose).group(0)!r}")
        run = run + 1 if sp == prev and not t.get("followup") else (1 if sp != prev else run)
        if run > 2:
            fails.append(f"turn {n}: {sp} asks a third question in a row without followup")
        streak = streak + 1 if sp == prev else 1
        if streak > 4:
            fails.append(f"turn {n}: {sp} asks a fifth turn in a row; rotate speakers")
        prev = sp
        if sp not in panel:
            fails.append(f"turn {n}: speaker {sp} not in panel")
    said = re.sub(r"\s+", " ", " ".join(t["text"] for t in s.get("transcript", [])
                                          if t.get("speaker") == "candidate")).lower()

    def verbatim(q):
        return re.sub(r"\s+", " ", q).strip().lower().strip("\"'.") in said

    for k, p in s.get("prose", {}).items():
        if p.get("quote") and s.get("transcript") and not verbatim(p["quote"]):
            fails.append(f"prose {k}: quote is not verbatim from the candidate's turns")
    if len(s.get("focus", [])) != 3:
        fails.append(f"focus: expected 3 items, got {len(s.get('focus', []))}")
    if s["mode"] == "topics":
        setup = s.get("setup", "")
        if not setup:
            fails.append("setup: the setup line is not recorded")
        for a in s.get("areas", []):
            if setup and a["label"].lower() not in setup.lower():
                fails.append(f"setup: does not name area {a['label']!r}")
            first = next((x for x in s.get("answers", []) if x["key"] == a["key"]), None)
            if first and a.get("owner") and first.get("by") and first["by"] != a["owner"]:
                fails.append(f"area {a['key']}: opened by {first['by']}, owner is {a['owner']}")
    if s.get("transcript") and not s.get("summary"):
        fails.append("summary: the spoken summary is not recorded")
    elif VERDICT_WORDS.search(s.get("summary", "")) or any(
            n in s.get("summary", "") for n in ("What landed", "Work on")):
        fails.append("summary: contains verdict or panel feedback")
    for n, txt in s.get("feedback_lines", {}).items():
        for slot in ("landed", "work_on"):
            if not txt.get(slot):
                fails.append(f"feedback {n}: missing {slot}")
            elif VERDICT_WORDS.search(txt[slot]):
                fails.append(f"feedback {n}.{slot}: hiring-verdict language")
    return fails


# ---------- self-test ----------

def selftest():
    docker = [("images-builds", "Images and builds", True, "Leslie"), ("runtime", "Runtime and isolation", True, "Dennis"),
              ("networking", "Networking", True, "Dennis"), ("storage", "Storage and volumes", False, "Dennis"),
              ("security", "Security", False, "Leslie"), ("orchestration", "Orchestration and operations", False, "Dennis")]
    s = {
        "mode": "topics", "length": "short", "date": "2026-11-19", "target": "S",
        "panel": ["Leslie", "Dennis", "Freda"], "communication": "S",
        "focus": ["storage: volume drivers", "edge: label guesses", "security: image signing"],
        "setup": ("Panel ready: Leslie, Dennis and Freda, about 20 minutes. Core: images and builds, runtime and "
                  "isolation, networking; also: storage and volumes, security, orchestration and operations."),
        "summary": "Strongest: depth. Weakest: reasoning at the edge. Type report for the full debrief.",
        "areas": [{"key": k, "label": l, "core": c, "owner": o} for k, l, c, o in docker],
        "answers": [
            {"key": "design", "level": "S", "by": "Leslie"},
            {"key": "images-builds", "level": "S", "by": "Leslie"},
            {"key": "runtime", "level": "S", "by": "Dennis", "also": "tradeoffs"},
            {"key": "networking", "level": "S", "by": "Dennis", "also": ["problem"]},
            {"key": "networking", "level": "I", "by": "Dennis", "floor": "overlay network internals", "edge": "S"},
            {"key": "storage", "level": "J", "flag": "bluff", "by": "Dennis", "floor": "volume drivers", "edge": "J"},
            {"key": "security", "level": "S", "flag": "hinted", "by": "Leslie", "floor": "image signing", "edge": "I"},
        ],
        "transcript": [{"speaker": "candidate", "text": "basically basically basically yes"},
                       {"speaker": "Leslie", "text": "Leslie here. Why?"}],
    }
    o = score(s)
    lv = o["levels"]
    assert [lv[k] for k in AXES] == ["S", "I", "S", "S", "S", "J", "S"], lv  # depth max, breadth 2/3 rule
    assert lv["security"] == "I" and lv["storage"] == "J" and lv["orchestration"] == "n/o"
    assert (o["breadth"]["k"], o["breadth"]["n"]) == (4, 5), o["breadth"]
    assert breadth_level(["S", "S", "I", "J"]) == "I" and breadth_level(["St"]) == "St" and breadth_level([]) == "n/o"
    fb = o["feedback"]
    assert (fb["Leslie"]["landed"], fb["Leslie"]["work_on"]) == ("depth", "edge"), fb["Leslie"]
    assert (fb["Dennis"]["landed"], fb["Dennis"]["work_on"]) == ("design", "breadth"), fb["Dennis"]
    assert (fb["Freda"]["landed"], fb["Freda"]["work_on"]) == ("tradeoffs", "communication"), fb["Freda"]
    # Derived depth gets credit for its areas' answers (3 at Senior), so it wins the Senior tie.
    assert (o["strongest"], o["weakest"]) == ("depth", "edge"), (o["strongest"], o["weakest"])
    assert o["breadth"]["at_target"] == 3
    assert (o["strongest_area"], o["weakest_area"]) == ("images-builds", "storage")
    assert o["floors"]["images-builds"] == "not reached" and o["floors"]["networking"] == "overlay network internals"
    assert o["candidate_points"] == "170,80 217,133 258,190 209,251 131,251 141,177 100,114", o["candidate_points"]
    assert o["target_points"] == "170,80 240,114 258,190 209,251 131,251 82,190 100,114"
    assert o["fillers"] == {"basically": 3}
    assert "record v4" in o["record"] and "levels: depth=S breadth=I design=S problem=S" in o["record"]
    assert "images-builds*=S" in o["record"] and "orchestration=n/o" in o["record"] and "breadth: 4/5" in o["record"]
    page, _ = build(s)
    assert "{{" not in page and "Topics and evidence" in page and "Breadth:" in page and "Networking" in page
    assert check(s) == [], check(s)
    # Answers after an area's floor don't raise its level.
    late = dict(s, answers=s["answers"] + [{"key": "networking", "level": "St", "by": "Dennis"}])
    assert score(late)["levels"]["networking"] == "S"
    for broken in ({"key": "desing", "level": "S"}, {"key": "depth", "level": "S"},
                   {"key": "storage", "level": "S", "flag": "hinted"}):
        try:
            score(dict(s, answers=s["answers"] + [broken]))
            raise AssertionError(f"must reject {broken}")
        except SystemExit:
            pass
    assert any("not verbatim" in f for f in check(dict(s, prose={"depth": {"quote": "never said this"}})))
    assert any("setup" in f for f in check(dict(s, setup="Panel ready.")))
    assert check(dict(s, feedback_lines={"Leslie": {"landed": "x", "work_on": "Strong yes from me"}})) != []
    cv = {"mode": "cv", "date": "2026-11-19", "target": "S", "communication": "S", "focus": ["a", "b", "c"],
          "answers": [{"key": "problem", "level": "St"}, {"key": "depth", "level": "S", "topic": "x"},
                      {"key": "depth", "level": "I", "topic": "x"}, {"key": "breadth", "level": "I"}]}
    o = score(cv)
    assert o["levels"]["depth"] == "I" and o["levels"]["problem"] == "St" and o["levels"]["breadth"] == "I"
    assert o["not_probed"] == ["design", "tradeoffs", "edge"]
    assert len(o["candidate_points"].split()) == 4  # unprobed axes are skipped in the polygon
    assert o["feedback"]["Leslie"]["landed"] == "depth"
    page, _ = build(cv)
    assert "Topics and evidence" not in page and "Trade-offs (n/o)" in page and "Not probed:</b> Design, Trade-offs, Reasoning at the edge" in page
    try:
        score(dict(s, areas=s["areas"] + [{"key": "design", "label": "x"}]))
        raise AssertionError("area key reusing an axis name must fail")
    except SystemExit:
        pass
    # The template's fallback coordinate table must match RADAR.
    rows = re.findall(r"^\s*\|\s*\w+\s*\|\s*\w+\s*\|((?:\s*\d+,\d+\s*\|){4})", TEMPLATE.read_text(), re.M)
    assert [[c.strip() for c in r.split("|") if c.strip()] for r in rows] == RADAR, "template radar table drifted"
    print("selftest ok")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("score", "build", "check", "selftest"):
        print(__doc__)
        return 2
    if argv[1] == "selftest":
        selftest()
        return 0
    s = json.loads(Path(argv[2]).read_text())
    if argv[1] == "score":
        print(json.dumps(score(s), indent=2))
    elif argv[1] == "check":
        fails = check(s)
        print("\n".join(fails) or "all mechanical checks pass")
        return 1 if fails else 0
    else:
        dest = Path(argv[argv.index("-o") + 1]) if "-o" in argv else Path(f"interview-report-{s['date']}.html")
        page, out = build(s)
        dest.write_text(page)
        print(f"wrote {dest}\n\n{out['record']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
