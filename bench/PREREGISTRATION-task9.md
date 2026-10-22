# Pre-registration: prospective run (Task 9)

Written before any prospective data exists. sitemend 1.9.0 gates real pull requests on
sites it was never tuned on, as they are opened. Every value below is fixed before the
window opens, and the decision rules in section 6 are applied to the results **exactly as
written**. A change after data exists is a dated, signed addendum at the end of this
file, and the report states it.

Fields marked `____` are for B to fill in. Where Claude proposed a value, it is shown
next to the field as "suggested", for reference only; the accepted value is the one that
counts.

**Status:** draft, written by Claude on 2026-10-22 from `bench/PREREGISTRATION.md`
(sections 1 to 6, Addenda 1 to 10) and `docs/benchmark-1.9.0-replay.md`. Not signed. No
part of Task 9 runs on a real repository until this file is merged.

**Why this run.** The replay result on 1.9.0 (precision 82 of 86, frequency 21 of 556,
seeded recall 66 of 67) was measured on the sample every 1.8.0 and 1.9.0 fix came from,
so it is optimistic (Addendum 10, part 6). As pre-registered, it makes Task 9 eligible;
it does not reopen outreach. This run is the evidence for sites sitemend has never seen,
and for the two regression types replay under-counts (section 7).

## 1. Frozen version

- Package: `sitemend==1.9.0`
- Tag: `v1.9.0`
- Commit: `507367ca62f341e0925dd82b2674d17731d93158`

The harness pins it the way `FROZEN` in `bench/replay/replay.py` does. No rule,
threshold or severity changes until this run's report is published. A bug found during
the window is logged in the ledger and gets an issue, and is not fixed. If B lifts the
freeze, that is an addendum, and every pull request checked after it is reported apart.

## 2. Sites

### 2.1 Exclusions

A repository is excluded if it is any of:

- the 15 benchmark repositories in `bench/replay/repos.json`, the sample every 1.8.0 and
  1.9.0 fix came from;
- every repository built or audited by the robustness sweep (`bench/sweep/sweep.csv`),
  since its findings were logged as issues against these rules;
- every repository Addendum 5 lists as excluded: the source repositories of the 23
  tuning sites, any repository whose GitHub homepage is on one of those hosts, and the 20
  repositories this plan used before Addendum 5;
- a repository owned by, or with a maintainer who is, B.

### 2.2 Frame and draw

- **Frame:** Addendum 5's saved frame, `bench/sample/frame-<stack>.json`, with no new
  search: ____ (suggested: reuse it, so the draw needs no new judgement).
- **Order:** each stack's saved draw order, `bench/sample/order-<stack>.json`, continued
  after the last repository the sample and the sweep looked at. Same seed (`20261017`),
  so nothing is shuffled again.
- **Eligibility,** checked in draw order on the draw date, every repository looked at
  recorded in `bench/task9/draw.csv` with its outcome and reason. All must hold:
  - Addendum 5, rule 4 (public, not a fork, not archived, site config present), with
    the 12-month commit window ending on the draw date instead of the cutoff;
  - at least ____ pull requests merged into the default branch in the 8 weeks before the
    draw date (suggested: 8, about one a week, so the window has PRs to gate);
  - builds by Addendum 5, rule 5 (with Addendum 6's Node rule) at the default branch's
    head on the Ubuntu runner, and the output holds HTML pages (Addendum 7).
- **Preview flag,** recorded but not required: whether a public deploy preview (Netlify,
  Vercel, Cloudflare Pages or similar) was posted, as a commit status or bot comment, on
  at least one of those merged PRs. It decides which PRs get the url-mode check (3.3).
- **Size:** the first ____ eligible repositories per stack (suggested: 6, so 30 in all).
  If fewer than ____ of the 30 have the preview flag (suggested: 10), the draw continues
  in order, taking only flagged repositories, until that many are flagged or ____
  repositories in all are taken (suggested: 40).
- **Draw date (UTC):** ____ (suggested: the day this file is merged).

The draw is run once and committed (`bench/task9/repos.json`, `draw.csv`) before the
window opens. A repository that later archives itself, goes private or stops building on
every PR stays in the sample, and its PRs count as skipped (4.3).

### 2.3 No contact during the window

This is a shadow run: sitemend runs on B's own runner against each PR's public code and
public preview. It posts no comment, opens no issue and sends no message to any drawn
repository during the window, so maintainers cannot change what they do because of it.
Whether true regressions are reported to maintainers after the report is published:
____ (suggested: yes, one issue per site, only after the report, and only for
`true_regression` findings still present on production).

## 3. Pull requests in the window

### 3.1 Window

- Opens (UTC): ____ (suggested: 00:00 on the day after the draw is committed).
- Length: ____ (suggested: 8 weeks).
- Extension: if fewer than 20 blocking findings have a verdict when the window closes,
  it is extended ____ at a time (suggested: 4 weeks), up to ____ in all (suggested: 16
  weeks). If 20 are never reached, precision counts as not met (as in section 4 of the
  main pre-registration).

### 3.2 What counts as a pull request

A pull request counts when all hold:

- it targets the repository's default branch;
- it is opened during the window (a PR opened before the window does not count, even if
  it is updated during it);
- it is not a draft when it is checked (3.3).

PRs opened by bots (Dependabot, Renovate and the like) count, and are also reported
apart. PRs from forks count. A PR that changes no file the site build reads still
counts: that is the per-PR gate a maintainer would run.

### 3.3 What is checked

Each counted PR is **one comparison**, made on its last head commit before it is merged
or closed, or at the window's close if it is still open. A PR closed less than ____
after its last push (suggested: 10 minutes) is checked on that head after closing. A PR
reopened in the window is still one comparison.

- **Folder mode, every PR:** head built with the repository's rule-5 command, compared
  with the PR's base commit built the same way, through `verify.py` as the Action does.
- **URL mode, PRs with a public preview:** the preview deploy of the head commit is
  audited as `url` and production (the repository's GitHub homepage) as `baseline-url`,
  with the Action's default `max-pages` (200) and no secret header. A preview behind
  authentication is not checked in url mode.

A finding counts as **blocking** exactly as the gate decides it: new or worsened,
critical or high, measured (high confidence), and not waived by the repository's own
`.sitemend-waivers.json` (`verify.py`, `blocks()`).

### 3.4 Skips

As in the main pre-registration, none of these count toward frequency or precision:

- `build_failed`: the head or base build fails in folder mode;
- `preview_unavailable`: the preview is missing, private or unreachable in url mode
  (the PR's folder-mode check still counts);
- tool failures (Addendum 1): sitemend crashes, or an audit does not finish within ____
  (suggested: 60 minutes). Reported per repository with the reason, as a reliability
  finding.

## 4. Verdicts

### 4.1 Ledger

One ledger, `bench/ledger-task9.csv`, with the same fields as `bench/ledger.csv`:

`repo, head_sha, rule_id, severity, url, evidence_excerpt, verdict, verified_by,
verification_method, notes`

- `notes` starts with the mode: `mode: folder`, `mode: url` or `mode: both`. A finding
  with the same ledger key (repo, head_sha, rule_id, url, evidence_excerpt) in both modes
  is one row, `mode: both`.
- `verified_by` is the person who gave the verdict.
- Earlier ledgers are not edited, and no verdict is carried over from them: every site
  here is new.

### 4.2 Verdict values

The values used in `bench/ledger.csv`:

| Verdict | Meaning | Counted as |
|---|---|---|
| `true_regression` | the PR introduced it, and it harms crawling or indexing | true |
| `false_positive` | the PR did not introduce it, or it is not a problem | false |
| `unclear` | nobody can confirm it either way | false, as in section 4 of the main pre-registration |

`true_but_preexisting` (used once in `bench/ledger-1.8.0.csv`): allowed here? ____
(suggested: yes, counted as false, since the gate blamed this PR for it). In url mode it
is the expected verdict when production lags the PR's base branch.

### 4.3 How a verdict is given

- **Evidence,** in this order, named in `verification_method`: the built HTML at the
  head and base commits (`build HTML at the commit`); the preview deploy at the head
  commit (`preview deploy at the head`); production after the PR was merged and deployed
  (`live site check`).
- **Timing:** a finding is judged within ____ of its PR being checked (suggested: 7
  days), while its preview is still up. A preview that is gone before a verdict leaves
  the built HTML as the evidence.
- **What happened next** is recorded in `notes`, not used as the verdict: merged or
  closed, and whether a later PR in the window fixed the problem.
- **Claude's readings.** Claude may draft a reading of a finding; it is marked
  `reading drafted by Claude` in `notes`, and B accepts or changes it. The report counts
  how many verdicts started as Claude's readings.
- **Second look:** ____ (suggested: B re-judges a random 20% of findings, drawn with
  `random.Random(20261017)` after the window closes, without seeing the first verdict;
  disagreements are reported, and the first verdict stands).
- No verdict changes after the window closes, except by addendum.

## 5. Thresholds

| Measure | Unit | Main pre-registration | Task 9 value |
|---|---|---|---|
| Blocking precision | per blocking finding: `true_regression` / all blocking findings with a verdict | at least 95%, with at least 20 verdicts | ____ (suggested: the same, at least 95% with at least 20, both modes pooled) |
| Frequency | per PR: PRs with at least one `true_regression` blocking finding / PRs compared | at least 1 per 100 commits | ____ (suggested: at least 1 per 100 PRs compared) |
| Tool failures | per PR: PRs with a tool failure / PRs counted | not a threshold | ____ (suggested: at most 5%) |

Reported, not thresholds:

- precision and frequency per mode (folder, url), per stack and per rule;
- bot PRs apart from the rest;
- **preview-host leaks** (`S1-HOST-MISMATCH` at critical, and the sitemap and canonical
  forms the seeded `sitemap-preview-host` mutation covers) and **soft 404s**
  (`S1-SOFT-404`): count of blocking findings, verdicts and PRs with each, in each mode.
  If a type has no `true_regression`, the report gives the rule-of-three upper bound
  (3 / PRs checked in url mode) on how often it occurs, instead of "none found";
- **misses, as a lower bound:** production of each site is audited at window open and
  window close with `fail-on: high`. A critical or high finding present at close, absent
  at open, and traced to a PR the gate passed in the window is a miss. This cannot see
  regressions fixed again before the window closes, so it is a floor, not recall.

Seeded recall is not re-run here; the 1.9.0 seeded result stands.

## 6. Decision rules

Applied to the window's results as written, with the outcome at the top of the report.

- **Precision, frequency and tool failures all met:** reopen outreach for the
  release-gate positioning (Phase 4). ____ (suggested: yes, this is the only result that
  reopens it.)
- **Precision fails:** outreach stays stopped, and the rules are fixed under the
  stability policy in `RELEASING.md`; every confirmed false positive becomes a permanent
  test. The next prospective run uses a fresh draw (the next repositories in draw order
  after this one), not this sample, for the reason in Addendum 10, part 7.
- **Precision passes, frequency fails:** re-position as a pre-launch and redesign audit,
  not a per-PR gate, as in section 5 of the main pre-registration.
- **Tool failures above the threshold:** outreach stays stopped until the failures are
  fixed and re-measured on a fresh draw, even if precision and frequency pass.
- **Preview-host leaks and soft 404s:** whatever the rest shows, no public material
  claims sitemend catches a type on real pull requests unless this run has at least ____
  `true_regression` blocking finding of that type (suggested: 1). Without one, the
  material says the type is tested by seeded mutation only.
- **Fewer than 20 verdicts after the longest extension:** precision counts as not met,
  and the first rule above applies.

## 7. Known limitations

- **What this run is for.** Replay builds each commit locally and cannot see
  environment variables, hosting or runtime behaviour, so preview-host leaks and soft
  404s were under-counted there (section 6 of the main pre-registration). URL mode on
  real preview deploys is the first measurement that can see them. It sees them only on
  sites with public previews, which are not a random part of the sample.
- **Production is not the base.** In url mode the baseline is production, which may lag
  or lead the PR's base branch. Differences that come from that gap are judged
  `true_but_preexisting` or `false_positive`, and count against precision.
- **The frame** is still GitHub code search from 2026-10-17 (capped, ranked by GitHub),
  mostly docs and project sites, and the build rule is mechanical (Addendum 5). Sites
  whose real deploy needs more than their own `build` script, and Hugo sites without an
  npm build script, are not in it.
- **URL mode crawls at most 200 pages** a side, so a regression on a larger site's deep
  pages can be missed in url mode while folder mode sees it.
- **Shadow, not installed.** Nobody acts on sitemend's result during the window, so the
  run measures what the gate would have said, not whether maintainers find it useful or
  how often they would waive a finding.
- **One judge.** B gives every verdict; Claude's readings and the second look (4.3) are
  stated, not a substitute for an independent rater.
- **Misses are a floor.** There is no seeded ground truth on live PRs, so recall here is
  only the lower bound in section 5.

## 8. Harness and data

- The harness (`bench/task9/`) is written and merged before the window opens. Before
  that, it is run only on the repository's own fixtures (`examples/demo-site`,
  `examples/demo-site-intl`), never on a drawn repository.
- Committed: `repos.json`, `draw.csv`, one results row per PR (repo, PR number, head and
  base SHA, mode, outcome, blocking count), the ledger and the report. Not committed:
  crawl output or built HTML, which hold the full text of the audited sites
  (`RELEASING.md`, step 5).
- The report gives totals and names no sites, like the replay reports.

## Sign-off

- Filled in and approved by (B): ____
- Date: ____
- Merged before the draw and before any prospective run on real data (commit SHA of the
  merge): ____
