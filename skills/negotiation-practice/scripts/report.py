#!/usr/bin/env python3
"""negotiation-practice: the deterministic half of the round.

The model plays the counterpart and rates each move (judgement). This script does what is a fixed rule
in references/rubric.md: picking a scenario and its variant, assigning levels, the outcome statement,
feedback picks, radar points, filler counts, the session record, transcript checks, and the report.

Usage:
  report.py pick [--family new-job|at-work] [--id <scenario>] [--done id1,id2] [--difficulty easy|medium|hard] [--seed N]
  report.py score session.json
  report.py check session.json
  report.py build session.json -o out.html
  report.py selftest

Python 3.8+, standard library only. session.json format: references/session-schema.md.
"""
import html
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFS = HERE.parent / "references"
TEMPLATE = REFS / "report-template.html"
BANK = REFS / "scenarios.md"
CARDS = REFS / "techniques.md"

LEVELS = ["N", "D", "S", "E"]
NAMES = {"N": "Novice", "D": "Developing", "S": "Skilled", "E": "Expert"}
AXES = ["empathy", "mirroring", "questions", "numbers", "pressure", "discovery", "delivery"]
LABELS = {"empathy": "Tactical empathy", "mirroring": "Mirroring", "questions": "Calibrated questions",
          "numbers": "Numbers and anchoring", "pressure": "Handling pressure", "discovery": "Discovery",
          "delivery": "Delivery"}
RADAR_LABELS = {"empathy": "Empathy", "mirroring": "Mirroring", "questions": "Questions", "numbers": "Numbers",
                "pressure": "Pressure", "discovery": "Discovery", "delivery": "Delivery"}
RADAR = [
    ["170,140", "170,110", "170,80", "170,50"],
    ["193,151", "217,133", "240,114", "264,95"],
    ["199,177", "228,183", "258,190", "287,197"],
    ["183,197", "196,224", "209,251", "222,278"],
    ["157,197", "144,224", "131,251", "118,278"],
    ["141,177", "112,183", "82,190", "53,197"],
    ["147,151", "123,133", "100,114", "76,95"],
]
FILLERS = ["basically", "actually", "literally", "you know", "i mean", "kind of", "sort of", "um", "uh", "erm"]
TECHNIQUE_WORDS = re.compile(r"\b(tactical empathy|calibrated question|mirror(ing)?|accusation audit|ackerman|"
                             r"black swan|label(l)?ing|no-oriented|anchor(ing)?)\b", re.I)
VERDICT_WORDS = re.compile(r"\b(strong (yes|no)|you (won|lost|passed|failed)|verdict|your score|scored)\b", re.I)
SENTENCE_END = re.compile(r"(?<!\d)[.!?]+(?!\d)")
UNIT_WORDS = {"days": "day", "months": "month", "projects": "project"}
LEVEL_KEYS = set(LEVELS) | {"n/o"}


def idx(level):
    return LEVELS.index(level)


# ---------- the bank ----------

def bank():
    """Scenario JSON blocks and hidden-brief prose from references/scenarios.md, validated."""
    text = BANK.read_text()
    out = {}
    for m in re.finditer(r"^## ([a-z0-9-]+): (.+?)\nFamily: ([a-z-]+)\n(.*?)```json\n(.*?)```", text, re.M | re.S):
        sid, prose, block = m.group(1), m.group(4), m.group(5)
        sc = json.loads(block)
        assert sc["id"] == sid and sc["family"] == m.group(3), sid
        hidden = re.search(r"\*\*Hidden brief:\*\*(.*?)\n\n", prose + "\n\n", re.S)
        sc["hidden_brief"] = " ".join(hidden.group(1).split()) if hidden else ""
        validate(sc)
        out[sid] = sc
    return out


def validate(sc):
    steps, o, t, l = sc["steps"], sc["opening"], sc["target"], sc["limit"]
    up = sc["scale"]["direction"] == "up"
    ordered = steps == sorted(steps) if up else steps == sorted(steps, reverse=True)
    problems = []
    if not ordered or len(set(steps)) != len(steps):
        problems.append("steps must move strictly toward the candidate")
    if steps[0] != o or steps[-1] != l:
        problems.append("steps must start at the opening and end at the limit")
    if not ((o <= t <= l) if up else (o >= t >= l)):
        problems.append("opening, target and limit out of order")
    if len(sc["facts"]) < 2 or not sc.get("tactics"):
        problems.append("needs at least two facts and one tactic")
    if problems:
        raise SystemExit(f"scenario {sc['id']}: " + "; ".join(problems))


def pick(family=None, done=(), difficulty="medium", seed=None, sid=None):
    b = bank()
    rng = random.Random(seed)
    if sid is None:
        pool = [k for k, v in b.items() if k not in done and (family is None or v["family"] == family)]
        pool = pool or [k for k, v in b.items() if family is None or v["family"] == family]
        if not pool:
            raise SystemExit(f"no scenario for family {family!r}")
        sid = rng.choice(sorted(pool))
    if sid not in b:
        raise SystemExit(f"unknown scenario {sid!r}")
    sc = b[sid]
    tactics = list(sc["tactics"])
    rng.shuffle(tactics)
    if difficulty not in ("easy", "medium", "hard"):
        raise SystemExit("--difficulty takes easy, medium or hard")
    tactics = tactics[:{"easy": 1, "medium": 2, "hard": len(tactics)}[difficulty]]
    return {"scenario": sid, "difficulty": difficulty,
            "variant": {"active_facts": sorted(rng.sample([f["id"] for f in sc["facts"]], 2)), "tactics": tactics}}


def scenario_of(s):
    if s["scenario"] == "custom":
        sc = dict(s["custom_scenario"], id="custom")
        validate(sc)
        return sc
    b = bank()
    if s["scenario"] not in b:
        raise SystemExit(f"unknown scenario {s['scenario']!r}")
    return b[s["scenario"]]


# ---------- scoring ----------

def effective(m):
    lvl = m["level"]
    if m.get("flag") == "damaging":
        lvl = "N"
    if m.get("flag") == "coached":
        lvl = LEVELS[max(0, idx(lvl) - 1)]
    return lvl


def assign(moves):
    if not moves:
        return "n/o"
    effs = [effective(m) for m in moves]
    best = max(range(len(effs)), key=lambda i: idx(effs[i]))
    level = effs[best]
    topic = moves[best].get("topic")
    if topic is not None:
        for m, e in zip(moves[best + 1:], effs[best + 1:]):
            if m.get("topic") == topic and idx(e) < idx(level):
                return LEVELS[max(0, idx(level) - 1)]
    return level


def fmt(sc, v):
    if v is None:
        return "no agreed value"
    kind, unit = sc["scale"]["kind"], sc["scale"]["unit"]
    num = f"{v:,.0f}" if kind == "money" else (f"{v:g}")
    if v == 1:
        unit = re.sub(r"\b(" + "|".join(UNIT_WORDS) + r")\b", lambda m: UNIT_WORDS[m.group(1)], unit, count=1)
    return f"{num} {unit}"


def score(s):
    sc = scenario_of(s)
    active = s.get("variant", {}).get("active_facts") or [f["id"] for f in sc["facts"]][:2]
    by_key = {}
    if s.get("delivery", "n/o") not in LEVEL_KEYS:
        raise SystemExit(f"delivery must be one of N, D, S, E or n/o, got {s['delivery']!r}")
    for m in s.get("moves", []):
        if m.get("level") not in LEVELS:
            raise SystemExit(f"move level must be one of N, D, S, E, got {m.get('level')!r}")
        if m["key"] not in AXES or m["key"] == "delivery":
            raise SystemExit(f"move key must be one of {AXES[:-1]}, got {m['key']!r}")
        if m.get("flag") not in (None, "coached", "damaging"):
            raise SystemExit(f"flag must be coached or damaging, got {m['flag']!r}")
        by_key.setdefault(m["key"], []).append(m)
    levels = {k: assign(by_key.get(k, [])) for k in AXES[:-1]}
    levels["delivery"] = s.get("delivery", "n/o")
    revealed = [t["reveals"] for t in s.get("transcript", []) if t.get("speaker") == "counterpart" and t.get("reveals")]
    found = [f for f in active if f in revealed]
    # Discovery is capped by what was found.
    if levels["discovery"] != "n/o" or s.get("transcript"):
        cap = "N" if not found else ("D" if len(found) < len(active) else "E")
        base = levels["discovery"] if levels["discovery"] != "n/o" else ("S" if found and len(found) == len(active) else "N")
        levels["discovery"] = min(base, cap, key=idx)
    shown = [k for k in AXES if levels[k] != "n/o"]
    flat = len(shown) > 1 and len({levels[k] for k in shown}) == 1
    landed = min(shown, key=lambda k: (-idx(levels[k]), AXES.index(k))) if shown else None
    rest = [k for k in shown if k != landed]
    work_on = min(rest, key=lambda k: (idx(levels[k]), AXES.index(k))) if rest else landed
    weakest_two = sorted(shown, key=lambda k: (idx(levels[k]), AXES.index(k)))[:2]

    o = s.get("outcome", {})
    value = o.get("value")
    up = sc["scale"]["direction"] == "up"
    left = None if value is None else (sc["limit"] - value if up else value - sc["limit"])
    if o.get("ended") == "deal" and value is not None:
        line = (f"You closed at {fmt(sc, value)}. Their opening was {fmt(sc, sc['opening'])}, their target "
                f"{fmt(sc, sc['target'])}, their limit {fmt(sc, sc['limit'])}. "
                + ("You reached their limit." if left == 0 else f"You left {fmt(sc, left)} on the table."))
        if o.get("terms"):
            line += " Also agreed: " + "; ".join(o["terms"]) + "."
    else:
        line = (f"No deal ({o.get('ended', 'not recorded')}). Their opening was {fmt(sc, sc['opening'])}, "
                f"their limit {fmt(sc, sc['limit'])}.")
    out = {
        "scenario": sc["id"], "levels": levels, "flat": flat,
        "strongest": None if flat else landed, "weakest": None if flat else work_on,
        "feedback": {"landed": landed, "work_on": work_on}, "weakest_two": weakest_two,
        "facts_found": {"found": found, "active": active},
        "outcome_line": line, "left_on_table": left,
        "coach": sum(1 for t in s.get("transcript", []) if t.get("speaker") == "coach"),
        "candidate_points": " ".join(RADAR[i][idx(levels[k])] for i, k in enumerate(AXES) if levels[k] != "n/o"),
        "not_shown": [k for k in AXES if levels[k] == "n/o"],
        "fillers": fillers(s),
    }
    out["record"] = record(s, sc, out)
    return out


def fillers(s):
    text = " ".join(t["text"] for t in s.get("transcript", []) if t.get("speaker") == "candidate").lower()
    text = re.sub(r"\bwhat kind of\b", "", text)  # a real question, not a filler
    counts = {f: len(re.findall(r"\b" + re.escape(f) + r"\b", text)) for f in FILLERS}
    return {f: c for f, c in sorted(counts.items(), key=lambda x: -x[1]) if c >= 3}


def record(s, sc, out):
    o = s.get("outcome", {})
    focus = " ".join(f"{i}) {f}" for i, f in enumerate(s.get("focus", []), 1))
    f = out["facts_found"]
    # No figures in the record: they may be someone's real compensation in a custom scenario.
    return "\n".join([
        "negotiation-practice record v1",
        f"date: {s['date']} | scenario: {sc['id']} ({sc.get('family', 'custom')}, {s.get('difficulty', 'medium')}) | "
        f"ended: {o.get('ended', '-')} | at or past their target: {'yes' if reached_target(sc, o.get('value')) else 'no'} | "
        f"facts: {len(f['found'])}/{len(f['active'])} | relationship: {o.get('relationship', '-')}",
        "levels: " + " ".join(f"{k}={out['levels'][k]}" for k in AXES),
        f"coach: {out['coach']}",
        f"focus: {focus}",
    ])


def reached_target(sc, value):
    if value is None:
        return False
    return value >= sc["target"] if sc["scale"]["direction"] == "up" else value <= sc["target"]


# ---------- checks ----------

def money_forms(v):
    k = v / 1000
    forms = {f"{v:,.0f}", f"{v:.0f}", f"{k:g}k", f"{k:g} thousand", f"{k:g},000"}
    return {f for f in forms if len(f) >= 3}


def limit_strings(sc):
    """Ways the limit could be said out loud. Bare small counts are too common to check."""
    v, kind = sc["limit"], sc["scale"]["kind"]
    if kind == "money":
        return money_forms(v)
    word = {"days": ["days", "working days"], "months": ["months"], "percent": ["%", " percent", "percent"]}.get(kind, [])
    return {f"{v:g}{w}" if w.startswith(("%", " ")) else f"{v:g} {w}" for w in word}


def check(s):
    fails = []
    try:
        sc = scenario_of(s)
        out = score(s)
    except SystemExit as err:
        return [f"score: {err}"]
    active = set(out["facts_found"]["active"])
    unlocked, offers, asked_coach = set(), [], False
    limit_forms = limit_strings(sc)
    for n, t in enumerate(s.get("transcript", []), 1):
        sp, text = t.get("speaker"), t.get("text", "")
        if sp == "candidate":
            asked_coach = bool(re.match(r"\W*coach\b", text.strip(), re.I)) or asked_coach
            if t.get("unlocks"):
                unlocked.add(t["unlocks"])
            continue
        if sp == "coach":
            if not asked_coach:
                fails.append(f"turn {n}: coaching without the candidate saying 'coach'")
            asked_coach = False
            continue
        if sp != "counterpart":
            fails.append(f"turn {n}: unknown speaker {sp!r}")
            continue
        if len([x for x in SENTENCE_END.split(text) if x.strip()]) > 3:
            fails.append(f"turn {n}: counterpart speaks more than three sentences")
        if TECHNIQUE_WORDS.search(text):
            fails.append(f"turn {n}: counterpart names a technique: {TECHNIQUE_WORDS.search(text).group(0)!r}")
        trust = t.get("trust")
        if trust not in ("low", "medium", "high"):
            fails.append(f"turn {n}: counterpart turn needs trust: low, medium or high")
        if "offer" in t:
            offers.append((n, t["offer"]))
            if trust == "low" and len(offers) > 1 and t["offer"] != offers[-2][1]:
                fails.append(f"turn {n}: a step at low trust")
        reached = sc["limit"] in [v for _, v in offers]
        if not reached and any(re.search(r"(?<![\d,.])" + re.escape(f) + r"(?!\d|[,.]\d)", text) for f in limit_forms):
            fails.append(f"turn {n}: counterpart states its limit before reaching it")
        if t.get("reveals") and trust == "low":
            fails.append(f"turn {n}: a hidden fact revealed at low trust")
        if t.get("reveals"):
            if t["reveals"] not in active:
                fails.append(f"turn {n}: reveals {t['reveals']!r}, which is not active this session")
            elif t["reveals"] not in unlocked:
                fails.append(f"turn {n}: reveals {t['reveals']!r} before a candidate move unlocked it")
    steps = sc["steps"]
    pos = 0
    for n, v in offers:
        if v not in steps:
            fails.append(f"turn {n}: offer {v} is not one of the scenario's steps")
            continue
        i = steps.index(v)
        if i > pos + 1:
            fails.append(f"turn {n}: offer jumps more than one step")
        if i < pos:
            fails.append(f"turn {n}: offer moves backwards")
        pos = max(pos, i)
    o = s.get("outcome", {})
    up = sc["scale"]["direction"] == "up"
    if o.get("ended") == "deal":
        if o.get("value") is None:
            fails.append("outcome: a deal needs a value")
        elif o["value"] > sc["limit"] if sc["scale"]["direction"] == "up" else o["value"] < sc["limit"]:
            fails.append("outcome: the counterpart conceded past its limit")
        elif offers:
            # The counterpart may accept the candidate's own figure up to the next allowed step.
            last = offers[-1][1]
            nxt = steps[min(steps.index(last) + 1, len(steps) - 1)] if last in steps else last
            lo, hi = (last, nxt) if up else (nxt, last)
            if not lo <= o["value"] <= hi:
                fails.append("outcome: the deal must sit between the last offer and the next step")
    setup = s.get("setup", "")
    if not setup:
        fails.append("setup: the setup line is not recorded")
    elif sc.get("title", "custom").lower() not in setup.lower() and sc["id"] != "custom":
        fails.append("setup: must name the scenario")
    summary = s.get("summary", "")
    if s.get("transcript") and not summary:
        fails.append("summary: the spoken summary is not recorded")
    elif VERDICT_WORDS.search(summary):
        fails.append("summary: carries a verdict or score")
    said = re.sub(r"\s+", " ", " ".join(t["text"] for t in s.get("transcript", []) if t.get("speaker") == "candidate")).lower()
    for k in AXES:
        if out["levels"][k] != "n/o":
            q = re.sub(r"\s+", " ", s.get("prose", {}).get(k, {}).get("quote", "")).strip().lower().strip("\"'.")
            if not q:
                fails.append(f"prose {k}: a rated axis needs a verbatim quote")
            elif s.get("transcript") and q not in said:
                fails.append(f"prose {k}: quote is not verbatim from the candidate's turns")
    for slot in ("landed", "work_on"):
        txt = s.get("feedback_lines", {}).get(slot, "")
        if not txt:
            fails.append(f"feedback {slot}: missing")
        elif VERDICT_WORDS.search(txt):
            fails.append(f"feedback {slot}: verdict language")
    if not 2 <= len(s.get("replays", [])) <= 3:
        fails.append("replays: expected two or three")
    if len(s.get("focus", [])) != 3:
        fails.append(f"focus: expected 3 items, got {len(s.get('focus', []))}")
    return fails


# ---------- rendering ----------

def e(x):
    return html.escape(str(x), quote=True)


def card_html(key):
    text = CARDS.read_text()
    m = re.search(r"^## " + re.escape(key) + r": (.+?)\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return ""
    paras = [p.strip() for p in m.group(2).strip().split("\n\n") if p.strip()]
    body = "".join(f"<p>{e(' '.join(p.split()))}</p>" for p in paras)
    body = re.sub(r"\*\*(.+?):\*\*", r"<b>\1:</b>", body).replace("`", "")
    return f"<h3>{e(m.group(1))}</h3>{body}"


def build(s):
    out = score(s)
    sc = scenario_of(s)
    lv = out["levels"]
    t = re.sub(r"<!--.*?-->\n?", "", TEMPLATE.read_text(), flags=re.S)
    rows = ""
    for k in AXES:
        if lv[k] == "n/o":
            rows += f"<tr><td>{LABELS[k]}</td><td>not shown</td><td>-</td><td>-</td></tr>\n"
            continue
        p = s.get("prose", {}).get(k, {})
        quote = f'<blockquote>"{e(p["quote"])}"</blockquote>' if p.get("quote") else ""
        rows += (f"<tr><td>{LABELS[k]}</td><td>{NAMES[lv[k]]}</td><td>{quote}{e(p.get('why', ''))}</td>"
                 f"<td>{e(p.get('next', ''))}</td></tr>\n")
    fb = s.get("feedback_lines", {})
    for slot in ("landed", "work_on"):
        if VERDICT_WORDS.search(fb.get(slot, "")):
            raise SystemExit(f"verdict language in the {slot} feedback")
    replays = "".join(f"<p><i>{e(r.get('moment', ''))}</i><br>You said: \"{e(r.get('said', ''))}\"<br>"
                      f"Stronger ({e(LABELS.get(r.get('technique'), r.get('technique', '')))}): \"{e(r.get('stronger', ''))}\"</p>\n"
                      for r in s.get("replays", [])) or "<p>none</p>"
    f = out["facts_found"]
    facts_by_id = {x["id"]: x["fact"] for x in sc["facts"]}
    found_txt = f"{len(f['found'])} of {len(f['active'])}" + (
        " (" + "; ".join(facts_by_id[x] + (" — found" if x in f["found"] else " — missed") for x in f["active"]) + ")")
    subs = {
        "DATE": s["date"], "TITLE": e(sc.get("title", "Your situation")), "FAMILY": e(sc.get("family", "custom")),
        "DIFFICULTY": e(s.get("difficulty", "medium")), "COACH": out["coach"],
        "OUTCOME_LINE": e(out["outcome_line"]), "FACTS_FOUND": e(found_txt),
        "RELATIONSHIP": e({"up": "goodwill up", "neutral": "neutral", "strained": "strained"}.get(
            s.get("outcome", {}).get("relationship"), "not recorded")),
        "CANDIDATE_POINTS": out["candidate_points"],
        "STRONGEST": ("even profile" if out["flat"] else LABELS.get(out["strongest"], "-")),
        "WEAKEST": ("none stands out" if out["flat"] else LABELS.get(out["weakest"], "-")),
        "NOT_SHOWN": ", ".join(LABELS[k] for k in out["not_shown"]) or "none",
        "ROWS": rows,
        "LANDED_AXIS": LABELS.get(out["feedback"]["landed"], "-"), "LANDED": e(fb.get("landed", "")),
        "WORK_ON_AXIS": LABELS.get(out["feedback"]["work_on"], "-"), "WORK_ON": e(fb.get("work_on", "")),
        "REPLAYS": replays, "HIDDEN_BRIEF": e(sc.get("hidden_brief", "")),
        "CARDS": "".join(card_html(k) for k in out["weakest_two"]),
        "FILLERS_WITH_COUNTS": ", ".join(f'"{w}" x{n}' for w, n in out["fillers"].items()) or "none used three or more times",
        "FOCUS": "".join(f"<p>{i}. {e(x)}</p>" for i, x in enumerate(s.get("focus", []), 1)) or "<p>none</p>",
        "SESSION_RECORD": e(out["record"]),
    }
    for i, k in enumerate(AXES, 1):
        subs[f"AXIS_{i}"] = RADAR_LABELS[k] + (" (n/o)" if lv[k] == "n/o" else "")
    for k, v in subs.items():
        t = t.replace("{{" + k + "}}", str(v))
    left = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", t)))
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    return t, out


# ---------- self-test ----------

def selftest():
    b = bank()
    assert len(b) == 10 and sum(v["family"] == "new-job" for v in b.values()) == 5, sorted(b)
    for sc in b.values():
        cards = CARDS.read_text()
        assert all(f"## {k}:" in cards for k in AXES)
        assert sc["hidden_brief"], sc["id"]
    p = pick(family="at-work", done=["aw-raise"], seed=3)
    assert b[p["scenario"]]["family"] == "at-work" and p["scenario"] != "aw-raise"
    assert len(p["variant"]["active_facts"]) == 2 and len(pick(sid="aw-raise", difficulty="easy")["variant"]["tactics"]) == 1
    assert len({json.dumps(pick(sid="aw-raise", seed=n)["variant"]) for n in range(6)}) > 1  # variants differ
    s = {
        "date": "2026-11-27", "scenario": "nj-lowball-offer", "difficulty": "medium",
        "variant": {"active_facts": ["bonus", "finance"], "tactics": ["cites internal parity"]},
        "setup": "Negotiation ready: A low first offer, medium. Keywords: coach, repeat, time out, wrap up.",
        "summary": "You closed with a signing bonus. Strongest: questions. Weakest: numbers. Type report for the debrief.",
        "delivery": "S",
        "moves": [
            {"key": "questions", "level": "S"}, {"key": "empathy", "level": "S", "flag": "coached"},
            {"key": "numbers", "level": "S", "topic": "counter"}, {"key": "numbers", "level": "D", "topic": "counter"},
            {"key": "discovery", "level": "E"}, {"key": "pressure", "level": "D"},
        ],
        "outcome": {"ended": "deal", "value": 80500, "terms": ["signing bonus 5,000"], "relationship": "up"},
        "prose": {k: {"quote": "how was the 72 decided basically", "why": "w", "next": "n"} for k in AXES},
        "feedback_lines": {"landed": "Your how-question opened finance.", "work_on": "Concede in shrinking steps."},
        "replays": [{"moment": "a", "said": "b", "stronger": "c", "technique": "numbers"},
                    {"moment": "d", "said": "e", "stronger": "f", "technique": "pressure"}],
        "focus": ["numbers: shrink steps", "pressure: hold on parity", "mirroring: try one"],
        "transcript": [
            {"speaker": "counterpart", "text": "We'd like to offer 72,000. It's in line with internal parity.", "offer": 72000, "trust": "medium"},
            {"speaker": "candidate", "text": "How was the 72 decided basically? Basically curious, basically.", "unlocks": "finance"},
            {"speaker": "counterpart", "text": "Finance set a ceiling, and I can go higher with a justification.", "reveals": "finance", "trust": "medium"},
            {"speaker": "candidate", "text": "coach"},
            {"speaker": "coach", "text": "A label on his worry could help here."},
            {"speaker": "counterpart", "text": "I could do 75,000.", "offer": 75000, "trust": "medium"},
            {"speaker": "candidate", "text": "Is there anything one-off we could add?", "unlocks": "bonus"},
            {"speaker": "counterpart", "text": "There's a signing bonus pool. Let's say 78,000 plus that.", "reveals": "bonus", "offer": 78000, "trust": "high"},
            {"speaker": "counterpart", "text": "Final: 80,500.", "offer": 80500, "trust": "high"},
        ],
    }
    o = score(s)
    lv = o["levels"]
    assert [lv[k] for k in AXES] == ["D", "n/o", "S", "D", "D", "E", "S"], lv  # coached -1; later weaker -1; discovery all found
    assert o["facts_found"]["found"] == ["bonus", "finance"] and o["coach"] == 1
    assert o["feedback"] == {"landed": "discovery", "work_on": "empathy"} and o["weakest_two"] == ["empathy", "numbers"]
    assert "You left 3,500 EUR per year on the table" in o["outcome_line"], o["outcome_line"]
    assert o["fillers"] == {"basically": 3}
    assert "80,500" not in o["record"] and "at or past their target: yes" in o["record"] and "facts: 2/2" in o["record"]
    assert check(s) == [], check(s)
    half = dict(s, transcript=[t for t in s["transcript"] if t.get("reveals") != "bonus"])
    assert score(half)["levels"]["discovery"] == "D"  # one of two found caps discovery
    bad_t = [
        {"speaker": "counterpart", "text": "Our limit is 84,000 but I'll start at 72,000.", "offer": 72000},
        {"speaker": "counterpart", "text": "Finance pre-approved more.", "reveals": "finance"},
        {"speaker": "coach", "text": "Use a label."},
        {"speaker": "counterpart", "text": "Nice mirroring. Okay, 80,500. One. Two. Three.", "offer": 80500},
    ]
    f = " | ".join(check(dict(s, transcript=bad_t)))
    for expected in ("before a candidate move unlocked", "coaching without", "names a technique", "more than three sentences", "jumps more than one step"):
        assert expected in f, (expected, f)
    assert any("limit before" in x for x in check(dict(s, transcript=[{"speaker": "counterpart", "text": "We can't pass 84k."}])))
    assert any("past its limit" in x for x in check(dict(s, outcome=dict(s["outcome"], value=90000))))
    # Fixes from the dry run.
    dec = dict(s, transcript=s["transcript"] + [{"speaker": "counterpart", "text": "I can do 6.5% now.", "trust": "high"}])
    assert not any("three sentences" in x for x in check(dec))
    assert any("limit before" in x for x in check(dict(s, transcript=[
        {"speaker": "counterpart", "text": "Our ceiling is 84,000, but I start at 72,000.", "offer": 72000, "trust": "medium"}])))
    ex = dict(s, scenario="nj-exploding-offer", setup="The offer expires Friday", variant={"active_facts": ["own-report", "weaker"]},
              outcome={"ended": "deal", "value": 5, "relationship": "up"},
              transcript=[{"speaker": "counterpart", "text": "Friday stands.", "offer": 0, "trust": "medium"},
                          {"speaker": "counterpart", "text": "Two days, then.", "offer": 2, "trust": "medium"},
                          {"speaker": "counterpart", "text": "I could never do 10 days.", "trust": "medium"}])
    fx = " | ".join(check(ex))
    assert "limit before" in fx and "between the last offer" in fx, fx  # 5 is past the next step (4)
    assert not any("between the last offer" in x for x in check(dict(ex, outcome={"ended": "deal", "value": 3, "relationship": "up"})))
    assert fmt(b["nj-exploding-offer"], 1) == "1 working day of extension", fmt(b["nj-exploding-offer"], 1)
    assert fmt(b["aw-extra-scope"], 1) == "1 project taken off your plate" and fmt(b["aw-extra-scope"], 2).startswith("2 projects")
    coach_please = dict(s, transcript=[{"speaker": "candidate", "text": "Coach, please."}, {"speaker": "coach", "text": "x"}])
    assert not any("coaching without" in x for x in check(coach_please))
    assert score(dict(s, moves=[m for m in s["moves"] if m["key"] != "discovery"]))["levels"]["discovery"] == "S"
    later = score(dict(s, moves=[{"key": "empathy", "level": "S", "flag": "coached"}, {"key": "empathy", "level": "E"}]))
    assert later["levels"]["empathy"] == "E"  # an uncoached later move counts in full
    for bad in ({"delivery": "Skilled"}, {"moves": [{"key": "empathy", "level": "Skilled"}]}):
        try:
            score(dict(s, **bad))
            raise AssertionError(f"must reject {bad}")
        except SystemExit:
            pass
    assert not any("verdict" in x for x in check(dict(s, summary="Strongest: questions. You let the Friday date pass. Type report.")))
    assert any("low trust" in x for x in check(dict(s, transcript=[
        {"speaker": "counterpart", "text": "72,000.", "offer": 72000, "trust": "medium"},
        {"speaker": "counterpart", "text": "75,000.", "offer": 75000, "trust": "low"}])))
    page, _ = build(s)
    assert "`" not in page
    assert "{{" not in page and "Finance pre-approved" in page and "Tactical empathy" in page and "<h3>" in page
    custom = dict(s, scenario="custom", custom_scenario=dict(b["aw-raise"], id="custom", title="Your situation"),
                  outcome={"ended": "deal", "value": 6.5, "relationship": "up"},
                  variant={"active_facts": ["slot", "hr-case"]}, transcript=[], moves=[{"key": "questions", "level": "S"}])
    assert "6.5" not in score(custom)["record"]
    try:
        validate(dict(b["aw-raise"], steps=[3, 9, 5]))
        raise AssertionError("unordered steps must fail")
    except SystemExit:
        pass
    rows = re.findall(r"^\s*\|\s*\d\s*\|\s*\w+\s*\|((?:\s*\d+,\d+\s*\|){4})", TEMPLATE.read_text(), re.M)
    assert [[c.strip() for c in r.split("|") if c.strip()] for r in rows] == RADAR, "template radar table drifted"
    print("selftest ok")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("pick", "score", "check", "build", "selftest"):
        print(__doc__)
        return 2
    if argv[1] == "selftest":
        selftest()
        return 0
    if argv[1] == "pick":
        def opt(name, default=None):
            return argv[argv.index(name) + 1] if name in argv else default
        seed = opt("--seed")
        if seed is not None and not seed.isdigit():
            raise SystemExit("--seed takes a non-negative integer")
        done = [d for d in (opt("--done") or "").split(",") if d]
        print(json.dumps(pick(opt("--family"), done, opt("--difficulty", "medium"),
                              int(seed) if seed else None, opt("--id")), indent=2))
        return 0
    s = json.loads(Path(argv[2]).read_text())
    if argv[1] == "score":
        print(json.dumps(score(s), indent=2))
    elif argv[1] == "check":
        fails = check(s)
        print("\n".join(fails) or "all mechanical checks pass")
        return 1 if fails else 0
    else:
        dest = Path(argv[argv.index("-o") + 1]) if "-o" in argv else Path(f"negotiation-{s['date']}.html")
        page, out = build(s)
        dest.write_text(page)
        print(f"wrote {dest}\n\n{out['record']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
