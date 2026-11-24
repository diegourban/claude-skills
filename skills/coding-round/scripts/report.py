#!/usr/bin/env python3
"""coding-round: the deterministic half of the round.

The model rates each answer (judgement) and writes the prose. This script does what is a fixed rule
in references/rubric.md: picking a problem, assigning levels, the feedback picks, radar points,
filler counts, the session record, transcript checks, and filling the HTML template.

Usage:
  report.py pick [--done id1,id2] [--category <category>] [--seed N]   # print one problem id
  report.py score session.json                                         # computed results as JSON
  report.py check session.json                                         # mechanical transcript checks
  report.py build session.json -o out.html                             # render report, print record
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
TEMPLATE = HERE.parent / "references" / "report-template.html"
BANK = HERE.parent / "references" / "problems.md"

LEVELS = ["J", "I", "S", "St"]
NAMES = {"J": "Junior", "I": "Intermediate", "S": "Senior", "St": "Staff"}
AXES = ["clarifying", "approach", "complexity", "correctness", "edges", "communication"]
LABELS = {"clarifying": "Clarifying", "approach": "Approach", "complexity": "Complexity",
          "correctness": "Correctness", "edges": "Edge cases", "communication": "Communication"}
RADAR = [
    ["170,140", "170,110", "170,80", "170,50"],
    ["196,155", "222,140", "248,125", "274,110"],
    ["196,185", "222,200", "248,215", "274,230"],
    ["170,200", "170,230", "170,260", "170,290"],
    ["144,185", "118,200", "92,215", "66,230"],
    ["144,155", "118,140", "92,125", "66,110"],
]
FILLERS = ["basically", "actually", "literally", "you know", "i mean", "kind of", "sort of", "um", "uh", "erm"]
NO_QUESTION_OK = {"hint", "code", "answer"}
PRAISE = re.compile(r"\b(great|excellent|good point|well done|nice one|perfect|spot on)\b|(?:^|[.!?]\s+)exactly[.!]", re.I)
VERDICT_WORDS = re.compile(r"\b(strong (yes|no)|no hire|would hire|would not hire|wouldn't hire|hiring decision|verdicts?)\b", re.I)
MD = re.compile(r"^\s*([-*] |#{1,6} |\d{1,2}\. |\|)", re.M)
SUMMARY_FORBIDDEN = re.compile(r"\b(hire|hiring|ready|pass(ed)?|fail(ed)?|junior|intermediate|senior|staff|verdict|work on)\b", re.I)
ASKED_HINT = re.compile(r"\bhint\b", re.I)
DECLINED_HINT = re.compile(r"\b(no|don't|do not|without)( need)?( a| any)? hints?\b", re.I)
# Words a user says -> bank category ids.
CATEGORY_WORDS = {
    "counting": "counting", "grouping": "counting", "hashmap": "counting", "hash map": "counting",
    "frequency": "counting", "anagram": "counting",
    "window": "window", "sliding window": "window", "two pointers": "window", "pointers": "window",
    "intervals": "intervals-heap", "interval": "intervals-heap", "heap": "intervals-heap",
    "top-k": "intervals-heap", "top k": "intervals-heap", "intervals-heap": "intervals-heap",
    "design": "design", "lru": "design", "cache": "design", "rate limiter": "design", "limiter": "design",
    "logs": "logs", "log": "logs", "parsing": "logs", "log parsing": "logs",
}
FOOTNOTE = "Your interviewer's name nods to Leslie Lamport (logical clocks, Paxos)."


def idx(level):
    return LEVELS.index(level)


def bank():
    """Problem ids and categories from references/problems.md."""
    text = BANK.read_text()
    out = {}
    for m in re.finditer(r"^## ([a-z0-9-]+): (.+)\nCategory: ([a-z-]+)", text, re.M):
        out[m.group(1)] = {"title": m.group(2).strip(), "category": m.group(3)}
    return out


def pick(done=(), category=None, seed=None):
    problems = bank()
    if category is not None:
        category = CATEGORY_WORDS.get(category.strip().lower(), category)
    pool = [p for p, v in problems.items() if p not in done and (category is None or v["category"] == category)]
    if not pool:  # everything done: allow repeats rather than fail
        pool = [p for p, v in problems.items() if category is None or v["category"] == category]
    if not pool:
        raise SystemExit(f"no problem in category {category!r}; categories: "
                         f"{sorted({v['category'] for v in problems.values()})}")
    return random.Random(seed).choice(sorted(pool))


def effective(a):
    lvl = a["level"]
    if a.get("flag") == "wrong":
        lvl = "J"
    if a.get("flag") == "hinted":
        lvl = LEVELS[max(0, idx(lvl) - 1)]
    return lvl


def assign(answers):
    """Rubric: the highest level demonstrated, lowered by one for a later weaker answer on the same point."""
    if not answers:
        return "n/o"
    effs = [effective(a) for a in answers]
    best = max(range(len(effs)), key=lambda i: idx(effs[i]))
    level = effs[best]
    hinted = [e for a, e in zip(answers, effs) if a.get("flag") == "hinted"]
    if hinted:  # an axis that needed a hint caps at its best hinted answer
        level = min(level, max(hinted, key=idx), key=idx)
    topic = answers[best].get("topic")
    if topic is not None:
        for a, e in zip(answers[best + 1:], effs[best + 1:]):
            if a.get("topic") == topic and idx(e) < idx(level):
                return LEVELS[max(0, idx(level) - 1)]
    return level


def score(s):
    target = s.get("target", "S")
    if s["problem"]["id"] not in bank():
        raise SystemExit(f"unknown problem id {s['problem']['id']!r}")
    by_key = {}
    for a in s.get("answers", []):
        if a["key"] not in AXES or a["key"] == "communication":
            raise SystemExit(f"answer key must be one of {AXES[:-1]}, got {a['key']!r}")
        if a.get("flag") not in (None, "hinted", "wrong"):
            raise SystemExit(f"flag must be hinted or wrong, got {a['flag']!r}")
        by_key.setdefault(a["key"], []).append(a)
    levels = {k: assign(by_key.get(k, [])) for k in AXES[:-1]}
    levels["communication"] = s.get("communication", "n/o")
    probed = [k for k in AXES if levels[k] != "n/o"]

    # Ties go by radar order; the spoken weakest is the report's work on, so the two always agree.
    landed = min(probed, key=lambda k: (-idx(levels[k]), AXES.index(k))) if probed else None
    gaps = [k for k in probed if k != landed]
    work_on = (min(gaps, key=lambda k: (-(idx(target) - idx(levels[k])), idx(levels[k]), AXES.index(k)))
               if gaps else landed)
    out = {
        "target": target, "levels": levels,
        "strongest": landed, "weakest": work_on,
        "feedback": {"landed": landed, "work_on": work_on,
                     "work_on_gap": max(0, idx(target) - idx(levels[work_on])) if work_on else 0},
        "hints": (sum(1 for t in s.get("transcript", []) if t.get("kind") == "hint") if s.get("transcript")
                  else sum(1 for a in s.get("answers", []) if a.get("flag") == "hinted")),
        "candidate_points": " ".join(RADAR[i][idx(levels[k])] for i, k in enumerate(AXES) if levels[k] != "n/o"),
        "target_points": " ".join(RADAR[i][idx(target)] for i in range(len(AXES))),
        "not_probed": [k for k in AXES if levels[k] == "n/o"],
        "fillers": fillers(s),
    }
    out["record"] = record(s, out)
    return out


def fillers(s):
    text = " ".join(t["text"] for t in s.get("transcript", []) if t.get("speaker") == "candidate").lower()
    counts = {f: len(re.findall(r"\b" + re.escape(f) + r"\b", text)) for f in FILLERS}
    return {f: c for f, c in sorted(counts.items(), key=lambda x: -x[1]) if c >= 3}


def record(s, out):
    p = s["problem"]
    focus = " ".join(f"{i}) {f}" for i, f in enumerate(s.get("focus", []), 1))
    return "\n".join([
        "coding-round record v1",
        f"date: {s['date']} | problem: {p['id']} ({p['category']}) | language: {s.get('language', 'Java')} | "
        f"target: {s.get('target_label', NAMES[out['target']])}",
        "levels: " + " ".join(f"{k}={out['levels'][k]}" for k in AXES),
        f"hints: {out['hints']}",
        f"focus: {focus}",
    ])


def check(s):
    """The mechanical evals: turn shape, the trace, hints only on request, setup and summary."""
    fails = []
    turns = s.get("transcript", [])
    first = True
    asked_hint = False
    for n, t in enumerate(turns, 1):
        sp, text, kind = t.get("speaker"), t.get("text", ""), t.get("kind", "question")
        if sp == "candidate":
            asked_hint = asked_hint or bool(ASKED_HINT.search(text) and not DECLINED_HINT.search(text))
            continue
        if sp != "Leslie":
            fails.append(f"turn {n}: speaker {sp!r}; the round has one interviewer, Leslie")
            continue
        if first and not re.match(r"Leslie here, [^.?]{3,40}\.", text):
            fails.append(f"turn {n}: Leslie's first turn needs a role tag ('Leslie here, staff engineer.')")
        elif not first and not text.startswith("Leslie here."):
            fails.append(f"turn {n}: does not start with 'Leslie here.'")
        first = False
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        q = prose.count("?")
        if q != 1 and not (q == 0 and kind in NO_QUESTION_OK):
            fails.append(f"turn {n}: {q} question marks (kind={kind})")
        if MD.search(prose):
            fails.append(f"turn {n}: markdown in a spoken turn")
        for block in re.findall(r"```[^\n]*\n(.*?)```", text, flags=re.S):
            if len(block.strip().splitlines()) > 15:
                fails.append(f"turn {n}: code block over 15 lines")
        if kind == "code" and "```" not in text:
            fails.append(f"turn {n}: a code turn must show the write-up as a code block")
        if PRAISE.search(prose):
            fails.append(f"turn {n}: possible praise or judgement: {PRAISE.search(prose).group(0)!r}")
        if kind == "hint":
            if not asked_hint:
                fails.append(f"turn {n}: hint given without the candidate asking for one")
            asked_hint = False
    if turns and not any(t.get("kind") == "trace" for t in turns):
        fails.append("no trace turn: the round must end its coding with a trace of a hidden test")
    setup = s.get("setup", "").lower()
    if not setup:
        fails.append("setup: the setup line is not recorded")
    elif not re.search(r"\b" + re.escape(s.get("language", "java").lower()) + r"\b(?![-+#])", setup) or "target" not in setup:
        fails.append("setup: must state the language and the target level")
    summary = s.get("summary", "")
    if turns and not summary:
        fails.append("summary: the spoken summary is not recorded")
    elif VERDICT_WORDS.search(summary) or SUMMARY_FORBIDDEN.search(summary.replace("Strongest", "").replace("Weakest", "")):
        fails.append("summary: carries a verdict, a level or feedback; it gives strongest, weakest and the report prompt")
    said = re.sub(r"\s+", " ", " ".join(t["text"] for t in turns if t.get("speaker") == "candidate")).lower()
    for k, p in s.get("prose", {}).items():
        q = re.sub(r"\s+", " ", p.get("quote", "")).strip().lower().strip("\"'.")
        if q and turns and q not in said:
            fails.append(f"prose {k}: quote is not verbatim from the candidate's turns")
    try:
        levels = score(s)["levels"]
    except SystemExit as err:
        return fails + [f"score: {err}"]
    for k in AXES:
        if levels[k] != "n/o" and not s.get("prose", {}).get(k, {}).get("quote"):
            fails.append(f"prose {k}: a probed axis needs a verbatim quote")
    for slot in ("landed", "work_on"):
        txt = s.get("feedback_lines", {}).get(slot, "")
        if not txt:
            fails.append(f"feedback {slot}: missing")
        elif VERDICT_WORDS.search(txt):
            fails.append(f"feedback {slot}: verdict language")
    if len(s.get("focus", [])) != 3:
        fails.append(f"focus: expected 3 items, got {len(s.get('focus', []))}")
    return fails


# ---------- rendering ----------

def e(x):
    return html.escape(str(x), quote=True)


def build(s):
    out = score(s)
    lv = out["levels"]
    t = re.sub(r"<!--.*?-->\n?", "", TEMPLATE.read_text(), flags=re.S)
    rows = ""
    for k in AXES:
        if lv[k] == "n/o":
            rows += f"<tr><td>{LABELS[k]}</td><td>not probed</td><td>-</td><td>-</td></tr>\n"
            continue
        p = s.get("prose", {}).get(k, {})
        quote = f'<blockquote>"{e(p["quote"])}"</blockquote>' if p.get("quote") else ""
        rows += (f"<tr><td>{LABELS[k]}</td><td>{NAMES[lv[k]]}</td><td>{quote}{e(p.get('why', ''))}</td>"
                 f"<td>{e(p.get('next', ''))}</td></tr>\n")
    fb = s.get("feedback_lines", {})
    for slot in ("landed", "work_on"):
        if VERDICT_WORDS.search(fb.get(slot, "")):
            raise SystemExit(f"verdict language in Leslie's {slot} feedback")
    m = s.get("model_solution", {})
    c = s.get("coaching", {})
    tl = NAMES[out["target"]]
    subs = {
        "DATE": s["date"], "PROBLEM_TITLE": e(s["problem"].get("title", s["problem"]["id"])),
        "CATEGORY": e(s["problem"]["category"]), "LANGUAGE": e(s.get("language", "Java")),
        "TARGET": e(s.get("target_label", tl)), "TARGET_LEVEL": tl, "HINTS": out["hints"],
        "TARGET_POINTS": out["target_points"], "CANDIDATE_POINTS": out["candidate_points"],
        "STRONGEST": LABELS.get(out["strongest"], "-"), "WEAKEST": LABELS.get(out["weakest"], "-"),
        "NOT_PROBED": ", ".join(LABELS[k] for k in out["not_probed"]) or "none",
        "ROWS": rows,
        "LANDED_AXIS": LABELS.get(out["feedback"]["landed"], "-"), "LANDED": e(fb.get("landed", "")),
        "WORK_ON_AXIS": LABELS.get(out["feedback"]["work_on"], "-"), "WORK_ON": e(fb.get("work_on", "")),
        "MODEL_APPROACH": e(m.get("approach", "")), "MODEL_COMPLEXITY": e(m.get("complexity", "")),
        "MISSED": e(", ".join(m.get("missed", [])) or "none"), "MODEL_CODE": e(m.get("code", "")),
        "FILLERS_WITH_COUNTS": ", ".join(f'"{f}" x{n}' for f, n in out["fillers"].items())
                               or "none used three or more times",
        "STRONGER_ANSWERS": "".join(f"<p><i>{e(a['question'])}</i><br>{e(a['answer'])}</p>\n"
                                    for a in c.get("stronger", [])) or "<p>none noted</p>",
        "SESSION_RECORD": e(out["record"]), "FOOTNOTE": FOOTNOTE,
    }
    for i, k in enumerate(AXES, 1):
        subs[f"AXIS_{i}"] = LABELS[k] + (" (n/o)" if lv[k] == "n/o" else "")
    for k, v in subs.items():
        t = t.replace("{{" + k + "}}", str(v))
    left = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", t)))
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    return t, out


# ---------- self-test ----------

def selftest():
    b = bank()
    assert len(b) == 10, len(b)
    cats = sorted({v["category"] for v in b.values()})
    assert cats == ["counting", "design", "intervals-heap", "logs", "window"], cats
    assert all(sum(1 for v in b.values() if v["category"] == c) == 2 for c in cats)
    assert pick(done=["lru-cache"], category="design") == "fixed-window-limiter"
    assert pick(done=list(b), category="logs") in ("slowest-endpoints", "sessions-per-user")  # all done: repeat
    s = {
        "date": "2026-11-24", "target": "S", "language": "Java", "communication": "S",
        "problem": {"id": "merge-maintenance-windows", "category": "intervals-heap", "title": "Merge maintenance windows"},
        "setup": "Coding round ready: one problem, about 15 minutes, in Java, target Senior. Keywords: hint, repeat, time out, wrap up.",
        "summary": "Strongest: approach. Weakest: edge cases. Type report when you're out of voice mode.",
        "answers": [
            {"key": "clarifying", "level": "I"},
            {"key": "approach", "level": "S"},
            {"key": "complexity", "level": "S"},
            {"key": "edges", "level": "S", "flag": "hinted"},
            {"key": "correctness", "level": "S", "topic": "trace"},
            {"key": "correctness", "level": "I", "topic": "trace"},
        ],
        "prose": {k: {"quote": "sort by start basically", "why": "w", "next": "n"} for k in AXES},
        "feedback_lines": {"landed": "You sorted first.", "work_on": "Ask about touching windows before coding."},
        "model_solution": {"approach": "sort, merge", "complexity": "O(n log n)", "code": "x < y", "missed": ["touching"]},
        "focus": ["edges: touching", "clarifying: order", "correctness: trace"],
        "transcript": [
            {"speaker": "Leslie", "text": "Leslie here, staff engineer. Teams book windows; what would you ask first?"},
            {"speaker": "candidate", "text": "I'd sort by start basically, basically, basically. Can I get a hint?"},
            {"speaker": "Leslie", "text": "Leslie here. Sort by start.", "kind": "hint"},
            {"speaker": "Leslie", "text": "Leslie here. I've put what I heard on screen.\n```java\nsort(w);\n```", "kind": "code"},
            {"speaker": "Leslie", "text": "Leslie here. Trace it for two windows that only touch?", "kind": "trace"},
        ],
    }
    o = score(s)
    lv = o["levels"]
    assert [lv[k] for k in AXES] == ["I", "S", "S", "I", "I", "S"], lv  # hinted -1; later weaker trace -1
    capped = score(dict(s, answers=s["answers"] + [{"key": "edges", "level": "St"}]))
    assert capped["levels"]["edges"] == "I"  # a later unhinted answer can't lift an axis that needed a hint
    assert pick(category="intervals", seed=1) in ("merge-maintenance-windows", "top-k-campaigns")
    assert pick(category="LRU", done=["lru-cache"]) == "fixed-window-limiter"
    assert o["hints"] == 1 and o["strongest"] == "approach" and o["weakest"] == "clarifying", o
    assert o["weakest"] == o["feedback"]["work_on"]
    assert o["feedback"] == {"landed": "approach", "work_on": "clarifying", "work_on_gap": 1}, o["feedback"]
    assert o["candidate_points"] == "170,110 248,125 248,215 170,230 118,200 92,125", o["candidate_points"]
    assert o["target_points"] == "170,80 248,125 248,215 170,260 92,215 92,125"
    assert o["fillers"] == {"basically": 3}
    assert "coding-round record v1" in o["record"] and "problem: merge-maintenance-windows (intervals-heap)" in o["record"]
    assert check(s) == [], check(s)
    bad = dict(s, transcript=[{"speaker": "Leslie", "text": "Leslie here. Great. Sort it?"},
                              {"speaker": "Leslie", "text": "Leslie here. Try a map.", "kind": "hint"}],
               summary="Strong yes from me.")
    f = " | ".join(check(bad))
    for expected in ("role tag", "praise", "without the candidate asking", "no trace turn", "summary"):
        assert expected in f, (expected, f)
    assert any("summary" in x for x in check(dict(s, summary="Strongest: approach. You're ready for Senior.")))
    assert any("needs a verbatim quote" in x for x in check(dict(s, prose={})))
    assert any("feedback work_on: missing" in x for x in check(dict(s, feedback_lines={"landed": "x"})))
    reveal = dict(s, transcript=s["transcript"][:1] + [{"speaker": "Leslie", "text": "Leslie here. A gap of exactly 1800 continues it. What next?"}] + s["transcript"][1:])
    assert not any("praise" in x for x in check(reveal))
    assert any("language" in x for x in check(dict(s, setup=s["setup"].replace("Java", "JavaScript"))))
    page, _ = build(s)
    assert "{{" not in page and "Merge maintenance windows" in page and "x &lt; y" in page
    nop = score(dict(s, answers=[{"key": "approach", "level": "S"}], communication="I"))
    assert nop["not_probed"] == ["clarifying", "complexity", "correctness", "edges"]
    assert len(nop["candidate_points"].split()) == 2
    for broken in ({"key": "communication", "level": "S"}, {"key": "speed", "level": "S"},
                   {"key": "approach", "level": "S", "flag": "skipped"}):
        try:
            score(dict(s, answers=[broken]))
            raise AssertionError(f"must reject {broken}")
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
        def opt(name):
            return argv[argv.index(name) + 1] if name in argv else None
        done = [d for d in (opt("--done") or "").split(",") if d]
        seed = opt("--seed")
        if seed is not None and not seed.lstrip("-").isdigit():
            raise SystemExit("--seed takes an integer")
        print(pick(done, opt("--category"), int(seed) if seed else None))
        return 0
    s = json.loads(Path(argv[2]).read_text())
    if argv[1] == "score":
        print(json.dumps(score(s), indent=2))
    elif argv[1] == "check":
        fails = check(s)
        print("\n".join(fails) or "all mechanical checks pass")
        return 1 if fails else 0
    else:
        dest = Path(argv[argv.index("-o") + 1]) if "-o" in argv else Path(f"coding-round-{s['date']}.html")
        page, out = build(s)
        dest.write_text(page)
        print(f"wrote {dest}\n\n{out['record']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
