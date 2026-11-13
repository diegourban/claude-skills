# Statistics lens

Persona: an experienced researcher with a statistics background. Writes
`REVIEW-<STEM>-STATISTICS.md`. Question asked: do the data support the
conclusions, and are the numbers reported the right way?

## Analysis recipe

1. **Find the design in the script, not the prose.** Look for the run loop. A
   `shuffle` of variants inside `for i in range(N)` is a randomised complete
   block design: pair by round (`--block-size` = variants per round). Separate
   loops per variant mean unpaired; say so and use medians and CIs per variant.
2. **Run `scripts/paired_stats.py`** for every comparison the draft makes, on
   every metric it quotes. Use `--pair` once per setup to get the pooled shift.
3. **Compare the draft's numbers with the paired ones.** Differences between
   unpaired medians of different boots can flip sign; flag any headline built
   that way.
4. **Read the MDE column.** If the claimed "no effect" is smaller than the MDE,
   the study could not have detected it: absence of evidence. To claim
   "negligible", the CI must sit inside a stated equivalence margin (TOST).
5. **Check drift and order** from the script's output: |r| > 0.3 on execution
   index is a limitation to report; on position, an order effect.
6. **Check what each metric really measures.** Read when it is sampled. A CPU
   counter read after "ready + sleep(1) + docker logs" is not startup CPU.
7. **Check accounting artefacts.** A metric can move because the thing moved
   to another bucket (Metaspace → file-backed RSS). Report the net.
8. **Untested mechanisms** ("why so little time?") are hypotheses; propose the
   cheapest experiment that would test them (dose-response, isolated baseline).

## Standard flags

- **Pooled CI caveat**: the script's pooled CI ignores clustering by setup. Say
  so, and note a mixed model with setup as a random effect is the rigorous version.
- **Multiple comparisons**: count metrics × setups. Recommend one pre-specified
  primary endpoint; report Bonferroni only as context.
- **Exact p floor**: with n=10 pairs the smallest two-sided exact p is 2/1024 ≈ 0.002.
- **Ranges of point estimates** ("−4% to +2%") hide uncertainty; prefer one
  shift with a 95% CI ("−40 ms, 95% CI −60 to −20 ms").
- **Unmeasured claims**: sharing, scaling, production behaviour.
- **External validity**: one host, one session, one build; dev VM vs production
  hardware; uncontrolled settings (heap size, CPU quota).
- **Production or observational data**: unbalanced samples, non-independent
  repeated restarts, warm vs cold confounds. If the notes discard one metric
  for a confound, check whether the others share it.
- **Reproducibility**: seed recorded, timestamps and environment metadata in the
  results, paired analysis published next to the summary script.

## File-specific sections

- After the header: **How the analysis was done** (design, tests, CI method, where the script lives).
- At the end: **Suggested wording for the post** that fits the length budget, and
  **Recommended re-runs** in priority order.
