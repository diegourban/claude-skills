# Domain-expert lens

Persona: a senior practitioner in the post's field (JVM performance engineer,
Kubernetes SRE, database engineer…). Writes `REVIEW-<STEM>-<DOMAIN>.md`.

## Checklist (any domain)

1. **Is each technical claim true for the stated versions?** Check what changed
   in that version: JDK 25 is not JDK 21, Spring Boot 4 is not 3.
2. **Is each mechanism described correctly?** Simplified is fine; wrong is not.
   "Parsed and verified" when nothing is verified is wrong.
3. **Does each number match the raw data?** Recompute it. Quote the file and value.
4. **Are qualitative claims tested?** "Silently ignored", "won't start", "fails
   loudly": grep the folder for the log line. No evidence means Wrong: untested,
   with the exact command to test it.
5. **Do the checks and commands the post gives actually check what readers need?**
   Image vs running process, CI flags vs prod flags, env vars a `docker run` skips.
6. **Does the post explain where the problem came from?** The likely origin is
   often the first thing a reader hits after applying the fix.
7. **What will an expert in the comments correct?** Name it before they do.
8. **Is anything overclaimed?** "Free", "always", "every", "no cost".
9. **Production numbers**: flag for Comms/Legal; check for confounds the notes admit.
10. **Is every claim the author didn't measure cited?** Platform behaviour needs its
    primary source (the JEP, the official docs, the original paper for a statistical
    method), as an inline link plus an entry in the post's References. A claim with
    no primary source and no measurement is Wrong: unsourced, with the fix "cite X"
    or the command that measures it. Fetch each cited page and confirm it says what
    the post claims; a wrong or outdated citation (a JEP's release, a moved docs
    page) is also Wrong.
11. **Was the overlap check run?** If the blog has `scripts/check_posts.py`, run it
    on the draft and report its result. Any 8-word match is Wrong (rewrite, or quote
    with the citation); list the sources it couldn't fetch as "compare by hand".

## Worked domain: JVM startup, CDS and AOT (JDK 21–26)

Check these when the post is about JVM startup:

- **Default CDS archives** ship since JDK 12 (JEP 341). JDK 11 has none, but one
  can be generated with `java -Xshare:dump`.
- **Archive selection follows the memory layout, not the GC.** ZGC has no
  compressed oops and maps `classes_nocoops.jsa`; G1 with a heap above 32 GB does
  too. Compact object headers (JDK 24+) use the `*_coh.jsa` variants.
- **The archive holds archived heap objects too** (module graph, interned
  strings, Integer cache), not just classes. In JDK 25, ZGC cannot load them;
  JEP 516 (AOT object caching with any GC) targets JDK 26.
- **Boot classes are not bytecode-verified at runtime by default**
  (`BytecodeVerificationLocal=false`). Say "pre-parsed and pre-linked", not "verified".
- **Metaspace drop is mostly accounting.** Archived classes leave the Metaspace
  pool and appear as file-backed RSS. Report RssAnon (private) and RssFile
  separately; for cross-process sharing, measure PSS (`/proc/<pid>/smaps_rollup`).
- **Sharing across pods** needs the same node, the same image layer (same JDK
  build), mapping at the requested address (no ASLR relocation), and only the
  read-only regions are shared. The read-write region is copy-on-write. The
  kernel charges a shared page-cache page to the cgroup that touched it first.
- **A common origin of `-Xshare:off`**: silencing "Sharing is only supported for
  boot loader classes because bootstrap classpath has been appended", caused by
  a `-javaagent` (Datadog, OpenTelemetry) appending to the boot classpath.
- **`java -version` via `docker run --entrypoint java`** skips the Deployment's
  `JAVA_TOOL_OPTIONS`/`JDK_JAVA_OPTIONS`. Check the running pod: `kubectl debug
  --target`, then `grep jsa /proc/1/maps`, or `-Xlog:cds` in the startup log.
- **`-Xshare:on`** belongs in a CI smoke test with prod flags (GC, heap,
  compact headers), never in the prod entrypoint.
- **AppCDS / AOT cache** (`-XX:SharedArchiveFile`, `-XX:AOTCache`, JEP 483/514/515)
  must match the training JDK, the classpath JARs (AppCDS checks each JAR's size
  and mtime) and the memory layout (compressed oops, compact object headers); on
  mismatch the app still starts with only the JDK's ~1.4k classes archived and a
  few `[warning][cds]` lines that are easy to miss, so it is not "silent". Only
  `AOTMode=on` or `-Xshare:on` turn it into a startup failure. Any claim about the exact
  behaviour of `-Xshare:off` combined with `-XX:AOTCache` must be tested on the
  stated JDK build before publishing.
- **Express the default-CDS gain in milliseconds.** It is a roughly fixed JVM
  startup saving (tens of ms); as a percentage it shrinks as the app grows.

## Adding a domain

When a new field comes up, write its checklist as a new `## Worked domain:`
section here once the user has accepted the review, and log it in `memory.md`.
