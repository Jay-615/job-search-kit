---
name: score-jobs
description: Score the jobs in my-search/pipeline.csv against the user's resume, criteria and target companies, writing a score and a one-line reason into each row. Also re-scores everything after the user changes their criteria, weights or target companies. Use when the user says "score my jobs", "rank my jobs", "rescore", "score everything again", or after a scan.
argument-hint: "[all]"
---

# Score jobs

You score jobs in `my-search/pipeline.csv` and write the numbers back into each row. The spreadsheet is the user's one source of truth. They sort it, filter it and type their own notes and statuses into it.

**Two modes:**

- **Normal** (default): score rows that have no score yet.
- **Rescore**: when `$ARGUMENTS` contains `all`, or the user says "rescore" or "score everything again", or mentions changing their criteria, weights or companies. Recompute every undecided row, and report what moved.

Either way, **skip rows the user has already decided about**: `status` of `applied`, `passed` or `closed` (any capitalization). Re-scoring a decision only confuses things.

Filters were already applied during the scan. Don't filter again here. Every row gets a score.

---

## Step 0: Preflight

1. `python3 scripts/pipeline.py check-open`. If it exits 2, stop and show the message.
2. Read `my-search/profile.md`:
   - `## Scoring`: `Experience match weight` (default 0.9), `Target company weight` (default 0.1), `Network proximity weight` (default 0), `Threshold` (default 70). If the weights don't add up to about 1.0, warn but use them as written.
   - `## Add-ons`: `network`. If it says `installed`, the network add-on is present (see 1b).
   - `## Resume`: master resume path (default `my-search/resume/master-resume.md`).
3. Read `my-search/criteria.md`: roles (note the one marked `(preferred role)`), seniority (target and "scored lower"), industries (strong, partial, avoid).
4. Read `my-search/target-companies.csv`.
5. Read the master resume **once** and keep it in mind for the whole run. If it's missing: "I can't find your resume at <path>. Say **change my resume** to set it up again." Then stop.
6. Get the rows: `python3 scripts/pipeline.py read --status new,interested,"" --unscored` (normal mode) or without `--unscored` (rescore mode). The `""` includes rows with a blank status. If there are none: "Nothing new to score. Say **find new jobs** first." Then stop.
7. Tell the user one line: "Scoring 23 jobs against your resume. About <N> minutes."

## Step 1: Score each row

Read the job description from the row's `posting_file`. If it's missing, still score `tgt`, leave `exp` and `score` empty, and set `why` to "No job description saved. Can't score fit." Never guess fit from the title alone.

### 1a. Experience match `exp` (0–100)

This is the real work. Compare the description with the resume:

| Part | What to look at |
|---|---|
| Title and level | Does the level match the target in `criteria.md`? Levels listed as "scored lower" lose 15–25 points here. |
| Years | Does the resume show the years the posting asks for? |
| Industry | Strong match 100, partial 70, off-list 30–50, an "avoid" industry 10. |
| Skills and tools | How much of the must-have list does the resume show? Note conspicuous gaps. |
| Education and certifications | Only if the posting requires them. Otherwise this doesn't lower the score. |

Combine into one integer. **Never assume experience the resume doesn't show.** A gap is a gap.

### 1b. Network `net` (only with the network add-on)

If `profile.md` says `network: installed` **and** `.claude/skills/network-check/SKILL.md` exists, invoke the `network-check` skill once per company, with the company name exactly as it appears in the row. It caches per company, so repeat companies are cheap. From its result use:

- `final_score` → `net` (0–100)
- `high_bridge_names` → `high_bridges` (names, comma-separated, or empty)
- `medium_bridge_names` → `med_bridges`

If it fails for a company (Chrome off, rate limit), leave `net` **empty**, not `0`. Empty means "not measured", and 0 means "measured, nobody there". Score that row on the two-factor formula and say "network not checked this run" in `why`.

Without the add-on, leave `net`, `high_bridges` and `med_bridges` empty and use the two-factor formula.

### 1c. Target company `tgt` (0–100)

This is a nudge, not a gate. At the default 10% weight, a High-priority company adds 10 points and an unlisted one adds nothing, so a great fit anywhere can still reach the top of the list.

Look up the company in `target-companies.csv` (ignore case and extra spaces, and allow obvious variants like "Inc."): High 100, Medium 60, Low 20, not on the list 0.

### 1d. Overall `score`

With a network score: `round(we*exp + wn*net + wt*tgt)`.

Without one: `round((we*exp + wt*tgt) / (we + wt))`.

Then the **preferred-role bonus**: add 5 (cap at 100) only if the title's core matches the preferred role **exactly**. The core is the title before any comma, dash, slash or parenthesis, with "Sr."/"Sr" read as "Senior" and "PM" as "Product Manager". "Sr. Product Manager - Payments" matches "Senior Product Manager", but "Senior Product Manager, Technical" and "Senior PMT" don't. **Skip the bonus entirely** if no role is marked preferred, or if the preferred role is the only role in `criteria.md`, because then it would apply to almost everything and stop meaning anything.

### 1e. The `why` column

One line, under about 15 words, naming what drives the score. Don't repeat the numbers.

- High: `Strong checkout and payments fit. Target company, High.`
- Low: `Off-target industry. Wants 10+ yrs people management.`
- Penalties, plainly: `Director-level, above target.` / `Pay range straddles your floor.`
- Plus `+5 top title` when the bonus applies.

No semicolons (the helper replaces them anyway).

### 1f. A short note in the posting file

Append (or replace) a `## Scoring` section at the end of the posting file: 3–6 short bullets explaining `exp` (what matched, which gaps), the target-company match, and network results if any. This is what `tailor-resume` reads later, and what the user opens if they want the detail.

## Step 2: Write once

Collect every row's results, then write them in **one** call:

```bash
python3 scripts/pipeline.py update my-search/.cache/tmp/scores.json
```

Each object: `url`, `exp`, `tgt`, `net`, `score`, `why`, `high_bridges`, `med_bridges`. The helper never touches `status`, `notes`, `date_applied` or `applied_via` if they hold a value, keeps the user's own columns, keeps row order, and backs up first. **Never add a rank column, and never re-sort the file.** The user sorts it themselves.

In rescore mode, read the old `score` values before writing so you can show what moved.

## Step 3: Report

Show a table of the jobs at or above the threshold (top 15 if there are more), plus 2–3 just below it:

```markdown
| Score | Company | Title | Mode | Pay | Why |
|---|---|---|---|---|---|
```

Shorten titles to about 45 characters. Show pay as written, or `—`. Then:

```
Scored 23 jobs. 6 are at or above your threshold of 70.
Skipped 9 you've already decided on (applied, passed or closed).

Open my-search/pipeline.csv and sort by score to see them all.
To tailor your resume for one, say: "tailor my resume for <company>".
```

**Rescore mode** also lists what moved: jobs that crossed the threshold up or down, and the biggest movers, with `old → new`.

If network scoring failed for every company, lead with that: "Network scores couldn't be checked this run (Chrome wasn't connected). Say **rescore** once it is."

If nothing reached the threshold, say so, and suggest widening criteria or lowering the threshold ("change my settings").

## Rules

- Write only through `scripts/pipeline.py`.
- Never change `status`, `notes`, `date_applied` or `applied_via`. If you think a status should change, say so in the report.
- An honest gap beats a confident wrong number.
