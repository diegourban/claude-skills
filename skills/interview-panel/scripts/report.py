#!/usr/bin/env python3
"""interview-panel: the deterministic half of the debrief.

The model rates each answer (judgement) and writes the prose. This script does everything
that is a fixed rule in references/rubric.md: assigning levels, edge, bars, breadth, each panelist's feedback picks,
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
CV_AXES = ["depth", "design", "coding", "debugging", "concepts", "tradeoffs", "communication"]
TOPIC_AXES = ["frontend", "backend", "databases", "security", "performance", "infrastructure", "methodology"]
THINKING = ["design", "tradeoffs", "edge", "communication"]
LABELS = {
    "depth": "Depth", "design": "Design", "coding": "Coding", "debugging": "Debugging",
    "concepts": "Concepts", "tradeoffs": "Trade-offs", "communication": "Communication",
    "edge": "Reasoning at the edge", "frontend": "Frontend", "backend": "Backend",
    "databases": "Databases", "security": "Security", "performance": "Performance",
    "infrastructure": "Infrastructure", "methodology": "Methodology",
}
# Radar points per axis (in radar order) for J, I, S, St. Centre 170,170 = n/o or n/a.
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
KEY_SKILLS = {
    "cv": {"Leslie": ["design", "coding", "concepts"], "Dennis": ["debugging", "design", "depth"],
           "Freda": ["tradeoffs", "depth", "communication"]},
    "topics": {"Leslie": ["backend", "databases", "edge"], "Dennis": ["infrastructure", "security", "design"],
               "Freda": ["methodology", "tradeoffs", "communication"]},
}
SHARED_TOPIC_AREAS = ["performance", "frontend"]  # count for every panelist who asked in them
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


def score(s):
    mode = s["mode"]
    target = s.get("target", "S")
    answers = s.get("answers", [])
    by_key = {}
    for a in answers:
        by_key.setdefault(a["key"], []).append(a)

    if mode == "cv":
        axes = CV_AXES
        rows = CV_AXES
    else:
        axes = TOPIC_AXES
        rows = TOPIC_AXES + THINKING
    na = set(s.get("na", [])) if mode == "topics" else set()
    core = set(s.get("core", [])) if mode == "topics" else set()
    if len(core) > 3:
        raise SystemExit("rubric: at most three core areas")

    levels = {}
    for k in rows:
        if k in na:
            levels[k] = "n/a"
        elif k == "edge":
            levels[k] = edge_level(answers)
        elif k == "communication" and "communication" in s:
            levels[k] = s["communication"]  # rated from all answers, not stepped
        else:
            levels[k] = assign(by_key.get(k, []))

    def bar(k):
        if mode == "topics" and k in TOPIC_AXES and k not in core:
            return LEVELS[max(0, idx(target) - 1)]
        return target

    # Panel feedback picks (rubric: Panel feedback). The model writes the words; this picks the skills.
    panel = s.get("panel", ["Leslie", "Dennis", "Freda"])
    feedback = {}
    taken = {"landed": set(), "work_on": set()}
    for name in panel:
        keys = list(KEY_SKILLS[mode][name])
        if mode == "topics":
            if "Dennis" not in panel and name == "Leslie":
                keys += ["infrastructure", "security"]
            for area in SHARED_TOPIC_AREAS:
                if any(a.get("by") == name for a in by_key.get(area, [])) and area not in keys:
                    keys.append(area)
        lens = [k for k in keys if levels.get(k) not in ("n/o", "n/a", None)]
        if not lens:  # all key skills n/o: comment on anything probed
            lens = [k for k in rows if levels.get(k) not in ("n/o", "n/a")]
        if not lens:
            continue
        lens.sort(key=rows.index)  # ties go by radar (row) order

        def choose(rank, slot, avoid=()):
            ordered = sorted(lens, key=rank)
            for k in ordered:
                if k not in taken[slot] and k not in avoid:
                    return k
            for k in ordered:
                if k not in avoid:
                    return k
            return ordered[0]

        landed = choose(lambda k: (-idx(levels[k]), rows.index(k)), "landed")
        # Work on: furthest below its bar; when nothing is below, the lowest level (aim at the next one).
        work_on = choose(lambda k: (-(idx(bar(k)) - idx(levels[k])), idx(levels[k]), rows.index(k)),
                         "work_on", avoid=(landed,))
        taken["landed"].add(landed)
        taken["work_on"].add(work_on)
        feedback[name] = {"landed": landed, "work_on": work_on, "lens": lens,
                          "work_on_gap": max(0, idx(bar(work_on)) - idx(levels[work_on]))}

    # Strongest / weakest: CV = all skills, topics = areas only; exclude n/o and n/a.
    pool = [k for k in axes if levels[k] not in ("n/o", "n/a")]

    def pick(best):
        if not pool:
            return None
        extreme = (max if best else min)(idx(levels[k]) for k in pool)
        tied = [k for k in pool if idx(levels[k]) == extreme]
        return max(tied, key=lambda k: (sum(1 for a in by_key.get(k, []) if idx(effective(a)) == extreme),
                                        -axes.index(k)))

    out = {
        "mode": mode, "target": target, "levels": levels,
        "feedback": feedback,
        "strongest": pick(True), "weakest": pick(False),
        "candidate_points": " ".join(CENTRE if levels[k] in ("n/o", "n/a") else RADAR[i][idx(levels[k])]
                                     for i, k in enumerate(axes)),
        "target_points": " ".join(CENTRE if k in na else RADAR[i][idx(bar(k))] for i, k in enumerate(axes)),
    }
    if mode == "topics":
        applicable = [k for k in TOPIC_AXES if levels[k] not in ("n/a", "n/o")]
        out["breadth"] = {"k": sum(1 for k in applicable if idx(levels[k]) >= idx("I")), "n": len(applicable)}
        out["bars"] = {k: ("n/a" if k in na else bar(k)) for k in TOPIC_AXES}
        out["core"] = sorted(core, key=TOPIC_AXES.index)
        out["floors"] = {k: ("-" if k in na else floor_of(k, by_key.get(k, []), levels[k])) for k in TOPIC_AXES}
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
    lines = ["interview-panel record v3", head]
    if out["mode"] == "cv":
        lines.append("levels: " + " ".join(f"{k}={lv[k]}" for k in CV_AXES))
    else:
        lines.append("topics: " + " ".join(f"{k}{'*' if k in out['core'] else ''}={lv[k]}" for k in TOPIC_AXES))
        lines.append("levels: " + " ".join(f"{k}={lv[k]}" for k in THINKING))
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

    axes = CV_AXES if mode == "cv" else TOPIC_AXES
    rows_cv = rows_topics = rows_thinking = ""
    if mode == "cv":
        for k in CV_AXES:
            ev, nxt = evidence(s, k)
            rows_cv += f"<tr><td>{LABELS[k]}</td><td>{lvl(k)}</td><td>{ev}</td><td>{nxt}</td></tr>\n"
    else:
        for k in TOPIC_AXES:
            if lv[k] == "n/a":
                rows_topics += f"<tr><td>{LABELS[k]}</td><td>n/a</td><td>-</td><td>-</td><td>-</td></tr>\n"
                continue
            ev, nxt = evidence(s, k)
            kind = "core" if k in out["core"] else "peripheral"
            rows_topics += (f"<tr><td>{LABELS[k]} ({kind})</td><td>{lvl(k)} / {NAMES[out['bars'][k]]}</td>"
                            f"<td>{ev}</td><td>{e(out['floors'][k])}</td><td>{nxt}</td></tr>\n")
        for k in THINKING:
            ev, nxt = evidence(s, k)
            rows_thinking += f"<tr><td>{LABELS[k]}</td><td>{lvl(k)}</td><td>{ev}</td><td>{nxt}</td></tr>\n"

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
    subs = {
        "DATE": s["date"], "TARGET": s.get("target_label", tl), "MODE": f"{s.get('length', 'full')}, {mode}",
        "PANEL": ", ".join(s.get("panel", ["Leslie", "Dennis", "Freda"])),
        "SKILL_OR_AREA": "skill" if mode == "cv" else "topic area",
        "TARGET_LEGEND": f"Target ({tl})" if mode == "cv" else f"Bar per area (target {tl})",
        "TARGET_POINTS": out["target_points"], "CANDIDATE_POINTS": out["candidate_points"],
        "STRONGEST": LABELS.get(out["strongest"], "-"), "WEAKEST": LABELS.get(out["weakest"], "-"),
        "K": out.get("breadth", {}).get("k", ""), "N": out.get("breadth", {}).get("n", ""),
        "AREA_MAPPING": e(s.get("area_mapping", "one to one")),
        "ROWS_CV": rows_cv, "ROWS_TOPICS": rows_topics, "ROWS_THINKING": rows_thinking,
        "FEEDBACK_CARDS": cards, "FILLERS_WITH_COUNTS": fill, "GRAMMAR_LINES": grammar or "<p>none noted</p>",
        "OVERUSED": overused, "STRONGER_ANSWERS": stronger,
        "SESSION_RECORD": e(out["record"]), "EASTER_EGG_FOOTNOTE": FOOTNOTE,
    }
    for i, k in enumerate(axes, 1):
        subs[f"AXIS_{i}"] = LABELS[k]
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
    run, prev = 0, None
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
        if s["mode"] == "topics" and s.get("answers") is not None and "```" in text:
            fails.append(f"turn {n}: code snippet in topics mode")
        if PRAISE.search(prose):
            fails.append(f"turn {n}: possible praise: {PRAISE.search(prose).group(0)!r}")
        run = run + 1 if sp == prev and not t.get("followup") else (1 if sp != prev else run)
        if run > 2:
            fails.append(f"turn {n}: {sp} asks a third question in a row without followup")
        prev = sp
        if sp not in panel:
            fails.append(f"turn {n}: speaker {sp} not in panel")
    for n, txt in s.get("feedback_lines", {}).items():
        for slot in ("landed", "work_on"):
            if not txt.get(slot):
                fails.append(f"feedback {n}: missing {slot}")
            elif VERDICT_WORDS.search(txt[slot]):
                fails.append(f"feedback {n}.{slot}: hiring-verdict language")
    return fails


# ---------- self-test ----------

def selftest():
    s = {
        "mode": "topics", "length": "short", "date": "2026-11-18", "target": "S",
        "panel": ["Leslie", "Dennis", "Freda"], "core": ["backend", "databases", "performance"],
        "na": ["frontend"], "communication": "S", "focus": ["security: service identity"],
        "answers": [
            {"key": "design", "level": "S", "by": "Leslie"},
            {"key": "backend", "level": "S", "by": "Leslie"},
            {"key": "tradeoffs", "level": "S", "by": "Freda"},
            {"key": "databases", "level": "S", "by": "Leslie"},
            {"key": "databases", "level": "I", "by": "Leslie", "floor": "MVCC read views", "edge": "S"},
            {"key": "performance", "level": "S", "by": "Dennis"},
            {"key": "methodology", "level": "S", "by": "Freda"},
            {"key": "security", "level": "J", "flag": "bluff", "by": "Dennis", "floor": "service identity", "edge": "J"},
            {"key": "infrastructure", "level": "S", "flag": "hinted", "by": "Dennis"},
        ],
        "transcript": [{"speaker": "candidate", "text": "basically basically basically yes"},
                       {"speaker": "Leslie", "text": "Leslie here. Why?"}],
    }
    o = score(s)
    assert o["levels"]["edge"] == "J", o["levels"]  # tie S/J -> lower, no further penalty
    assert o["levels"]["infrastructure"] == "I"
    assert o["levels"]["security"] == "J"
    assert o["breadth"] == {"k": 5, "n": 6}, o["breadth"]
    fb = o["feedback"]
    assert fb["Leslie"]["landed"] == "backend" and fb["Leslie"]["work_on"] == "edge", fb["Leslie"]
    assert fb["Dennis"]["work_on"] == "security" and fb["Dennis"]["landed"] == "performance", fb["Dennis"]
    assert fb["Freda"]["landed"] == "methodology" and fb["Freda"]["work_on"] == "tradeoffs", fb["Freda"]
    assert o["strongest"] == "backend", o["strongest"]  # four-way S tie, one S answer each -> radar order
    assert o["weakest"] == "security"
    assert o["floors"]["backend"] == "not reached" and o["floors"]["databases"] == "MVCC read views"
    assert o["candidate_points"].startswith("170,170 240,114 258,190 183,197")
    assert o["target_points"] == "170,170 240,114 258,190 196,224 131,251 112,183 123,133"
    assert o["fillers"] == {"basically": 3}
    assert "backend*=S" in o["record"] and "breadth: 5/6" in o["record"]
    assert "record v3" in o["record"] and "verdicts" not in o["record"]
    page, _ = build(s)
    assert "{{" not in page and "Skills and evidence" not in page and "Breadth:" in page
    assert check(s) == []
    assert check(dict(s, feedback_lines={"Leslie": {"landed": "x", "work_on": "Strong yes from me"}})) != []
    cv = dict(s, mode="cv", answers=[{"key": "coding", "level": "St"}, {"key": "depth", "level": "S", "topic": "x"},
                                     {"key": "depth", "level": "I", "topic": "x"}])
    o = score(cv)
    assert o["levels"]["depth"] == "I" and o["levels"]["coding"] == "St"
    assert o["feedback"]["Leslie"]["landed"] == "coding"
    assert o["feedback"]["Dennis"]["landed"] == "depth"  # only observed key skill: both slots fall back to it
    assert o["feedback"]["Freda"] == dict(o["feedback"]["Freda"], landed="communication", work_on="depth")
    page, _ = build(cv)
    assert "Topics and evidence" not in page
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
