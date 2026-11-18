# job-search-kit

You're running inside job-search-kit, a job-search helper. The user downloaded it from GitHub, and most users aren't technical. It finds job postings on LinkedIn, Indeed, Dice and company career pages, scores them against the user's resume and preferences, and writes tailored resumes. It never applies for jobs. The user does that themselves.

## First thing to check

If `my-search/profile.md` doesn't exist, or it says `setup_complete: false`, the user isn't set up yet. Greet them and offer to start: "Looks like you're new here. Want me to set you up? It takes about 10 minutes." Then follow the `setup` skill.

## What the user can ask for

| They say | Skill |
|---|---|
| "set me up", "change my settings" | `setup` |
| "find new jobs" | `scan-jobs` |
| "score my jobs", "rescore" | `score-jobs` |
| "tailor my resume for <company>" | `tailor-resume` |
| "update the kit" | `update-kit` |
| "add the network add-on", "add the unemployment add-on" | `add-addon` |

Add-ons add their own skills when installed (listed under `## Add-ons` in `profile.md`). The **network** add-on adds `build-connections`, `rate-connections`, `network-check`, `map-company-connections` and `add-work-context`. The **unemployment** add-on adds `log-work-search`.

If the unemployment add-on is installed, mention once per session, after a scan, a scoring run or a tailored resume, and only if the user hasn't logged this week yet: "When you're ready, say **log my work search** to add this week's activity to your unemployment record." Never log anything without the user confirming it.

## Where things live

```
job-search-kit/
├── .claude/skills/        the commands above
├── scripts/pipeline.py    the only code that writes the spreadsheet
├── templates/             resume and job-posting layouts
├── examples/              a fictional person's settings (Sam Chen), for reference
├── docs/how-it-works.md   plain-language explanation
└── my-search/             EVERYTHING PERSONAL. Never committed, never touched by updates.
    ├── profile.md           contact info and settings
    ├── criteria.md          what jobs they want
    ├── target-companies.csv
    ├── resume/              original.<ext> (theirs, untouched) + master-resume.md
    ├── pipeline.csv         THE SPREADSHEET: one row per job
    ├── postings/            one .md per job description
    ├── applications/        one folder per tailored resume
    ├── network/             network add-on data, if installed
    ├── work-search/         unemployment add-on records, if installed
    ├── .cache/              seen.json, career-page-cache.json, network cache
    ├── .backups/            automatic backups, 3 newest per file
    └── .addons/             record of installed add-on files
```

## Rules for the spreadsheet (`my-search/pipeline.csv`)

The user opens this in Excel or Numbers, sorts it, and types their own notes and statuses into it. Treat it with care:

- **Write it only through `scripts/pipeline.py`** (`append`, `update`). The script refuses to write while the file is open, backs it up first, keeps the user's own columns and row order, never overwrites their `status`, `notes`, `date_applied` or `applied_via`, and strips semicolons.
- If the script says the file is open, ask the user to close it. Numbers doesn't leave a lock file, so before writing, remind Numbers users once per session to close the file.
- `url` is the unique key. Never merge two rows, never delete rows. Flag possible duplicates and let the user decide.
- No rank column, and don't re-sort. The user sorts.
- Status values are the user's. Common ones: `new`, `interested`, `applied`, `passed`, `closed`. Rows marked `applied`, `passed` or `closed` aren't re-scored.

## Other conventions

- Personal data goes only in `my-search/`. Never write the user's details anywhere else in this folder.
- Before overwriting any file in `my-search/`, back it up with `python3 scripts/pipeline.py backup <file>`.
- Temporary work files go in `my-search/.cache/tmp/`. When a command finishes, delete them with exactly `rm -rf my-search/.cache/tmp`. That exact command is pre-approved, so the user isn't asked.
- Never invent experience in a resume. Gaps go in the notes file.
- Never type passwords, log in for the user, solve CAPTCHAs, or submit applications.
- The user is on a Mac. Prefer Python (`python3`) over shell tricks that differ between Mac and Linux (`sed -i`, `date -d`, `stat`). Don't assume Homebrew.
- Talk plainly. Avoid developer terms (repository, CSV schema, frontmatter, MCP) unless the user uses them first.
