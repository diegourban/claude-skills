# Worked example: the default-CDS LinkedIn post (2026-10-14/15)

Draft: `~/aot-exploration/linkedin-cds/POST-1-DEFAULT-CDS-EN.md`
(2,623 of 3,000 characters). Folder had `DADOS-POST.md` (author notes),
`POST-1-FIRST-COMMENT-EN.md`, `POST-2-APPCDS-EN.md`, `bench*.py`,
`results*.json`, `run*.log`.

Output files: `REVIEW-POST-1-JVM.md`, `REVIEW-POST-1-EDITORIAL.md`,
`REVIEW-POST-1-STATISTICS.md` in that folder. Read them for full wording.

## Domain (JVM) findings that mattered

- Wrong: closing "10 MB back per JVM" vs measured 2–7 MB RssAnon; metaspace
  drop is accounting (RssFile +3 MB).
- Wrong: "JVM won't even start" with `-Xshare:off` + `-XX:AOTCache`; no file in
  the folder mentions AOTCache. Fix: test command or drop.
- Wrong: "the memory is free"; sharing needs same node and layer, no ASLR
  relocation, read-only regions only.
- Needs explanation: gain in ms (20–70) not "noise"; archived heap objects and
  ZGC in JDK 25 (JEP 516 in 26); the Datadog-agent warning as the flag's origin;
  checks look at the image not the running pod; CI `-Xshare:on` must use prod flags.

## Editorial findings that mattered

- Wrong: backticks render literally on LinkedIn; ending contradicts body;
  teaser for post 2 undercuts post 1; "free" ambiguous; three bullet styles;
  "several services" should be "9".
- Needs explanation: method paragraph too dense; jargon table (metaspace,
  compressed oops, page cache); lesson never stated in one sentence; JDK 11
  readers left out; no discovery moment; generic CTA; no chart.

## Statistics findings that mattered

- Design: `random.shuffle(order)` inside the round loop, so paired by round.
- Wrong: "noise". Pooled −2.1% [−3.2%, −1.5%], 39/50; Serial 10/10 p=0.002,
  G1 9/10 p=0.006.
- Wrong: "+2%" on the heavy app came from unpaired medians; paired −0.2%.
- Wrong: "no effect" from n=10 with MDE 2.2–4.0% (13% on the noisy run).
- Wrong: net RSS only −1.4 to −4.1 MB (+1.1 on Postgres); sharing never measured (needs PSS).
- Needs explanation: CPU sampled ~1–2 s after ready; Postgres-run drift r=0.57;
  ~42 tests, no primary endpoint; untested mechanism; one Mac VM; production
  −14% CPU shares the warm-restart confound the notes used to discard time.

## Commands used

```bash
wc -m POST-1-DEFAULT-CDS-EN.md
grep -rn -i "AOTCache\|AOTMode" . | grep -v '\.json:'
python3 ${CLAUDE_SKILL_DIR}/scripts/paired_stats.py \
  --file results_gc.json --block-size 12 \
  --pair zgc_xshare_off:zgc_cds_default --pair g1_xshare_off:g1_cds_default \
  --pair parallel_xshare_off:parallel_cds_default --pair serial_xshare_off:serial_cds_default \
  --metrics process,cpu_s,rss_anon,rss_file,metaspace
python3 ${CLAUDE_SKILL_DIR}/scripts/paired_stats.py \
  --file results_pg.json --block-size 3 --pair pg_xshare_off:pg_cds_default --metrics process,rss_anon
```
