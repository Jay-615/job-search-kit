---
name: setup
description: Guided first-time setup for job-search-kit, and the way to change settings later. Use when the user says "set me up", "get started", "help me set this up", "change my settings", "update my criteria", "change my resume", or opens the project and my-search/profile.md doesn't exist yet. Checks and installs prerequisites (Claude in Chrome, LinkedIn login, pandoc), interviews the user about contact info, resume, job criteria and target companies, and writes everything to my-search/. Resumes where it left off if interrupted.
argument-hint: "[optional: what to change, e.g. 'criteria']"
---

# Setup

You are walking a friend through setting up job-search-kit. Most users are **not technical**. Some have never used Claude Code before. Your job is to get them from "I just downloaded this" to "I can see my first scored jobs", with as little effort and confusion on their side as possible.

## How to talk during setup

- **One question at a time**, using `AskUserQuestion` for every choice. Put your recommended answer first and label it "(Recommended)". For free-text answers (name, email), ask in plain chat.
- **Plain English.** Never say frontmatter, CSV schema, gitignored, MCP, PATH, repo or skill. Say "your settings file", "your spreadsheet", "the Chrome extension", "this folder", "command".
- **Say why** in one short clause when you ask for something ("so I can put it at the top of your resume").
- **Save each answer immediately** to `my-search/` as soon as it's given. If the session dies halfway through, nothing they've typed is lost.
- **Keep it short.** No walls of text. No lists of everything that's about to happen. Tell them roughly how long it takes (about 10 minutes) at the start, then just go.
- Read `examples/profile.md` and `examples/criteria.md` before you start. They show the exact format of the files you'll write.

## Step 0: Where are we?

1. If `$ARGUMENTS` names something specific ("criteria", "resume", "companies", "contact", "sources", "weights"), and `my-search/profile.md` exists, jump straight to that stage, change only that, and stop. Weights and threshold aren't asked during first-time setup. If the user asks to change them, edit the `## Scoring` section of `profile.md` directly. Weights must add up to 1.0.
2. If `my-search/profile.md` does not exist: first-time setup. Create the `my-search/` folder with `resume/`, `postings/`, `applications/`, `.cache/` and `.backups/` inside it. Write a `profile.md` skeleton copied from `examples/profile.md` with every personal value blank, `setup_complete: false` and `completed_stages:` empty. Then welcome them:

   > Welcome! I'll get you set up. It takes about 10 minutes. I'll check a couple of things on your computer, ask about you and the jobs you want, and then we'll run a first search together.

3. If `profile.md` exists and `setup_complete: false`: resume. Read `completed_stages`, say "Picking up where we left off", and continue from the first stage that isn't done.
4. If `setup_complete: true` and there are no arguments, ask what they'd like to change: contact info, resume, job criteria, target companies, job sites, network add-on, or "start over". Start over means backing up `my-search/` to `my-search/.backups/setup-<timestamp>/`, confirming once, then running first-time setup.

After each stage below, append its name to `completed_stages` in `profile.md`.

## Stage `chrome`: the Claude in Chrome extension

Scanning job sites works through the Claude in Chrome extension, using the user's own Chrome.

1. Look at the tools available in this session for the Claude in Chrome extension (their names usually contain `claude-in-chrome` or `Claude_in_Chrome`). If they're deferred, load them. Call the one that lists connected browsers, or the one that lists tabs.
2. **Connected**: say "I can see your Chrome. 👍" and move on.
3. **Not connected, or no such tools**: explain and pause:

   > To search job sites, I use the Claude in Chrome extension. It lets me read LinkedIn and other sites in your own Chrome, as you. Install it from https://claude.com/claude-in-chrome, sign in with the same Claude account, and make sure Chrome is open. Tell me when that's done.

   Then use `AskUserQuestion`: "Done, check again" / "Skip for now (I can only scan company career pages until this is set up)". On "check again", re-check. If it still fails after two tries, suggest restarting the Claude app, then offer to skip.

## Stage `linkedin`: logged in to LinkedIn

Skip this if Chrome was skipped.

Open https://www.linkedin.com/feed/ in a new tab in their Chrome. If the feed loads, they're logged in. Move on.

If it redirects to a login page, explain why it matters and let them choose:

> You're not logged into LinkedIn in Chrome. Logging in makes searches much better: I can check which jobs are still open, which are really remote, and what they pay. **Without it, I mostly can't find remote jobs.** You can log in now (in the Chrome tab I just opened), or skip and do it later.

Options: "I'll log in now (Recommended)" / "Skip for now". On "log in now", wait until they say done, then re-check. If it still shows the login page, offer the same two options again. On "Skip for now", record `- linkedin_login: skipped` under `## Sources` in `profile.md` and carry on. **Never type their password or drive the login.**

Then mention once, without asking anything: "If you have Indeed or Dice accounts, logging into those in Chrome too means fewer 'are you human?' checks. Optional."

## Stage `pandoc`: quiet check for an optional converter

Tailored resumes always come out as Word documents. The kit has a built-in converter (`scripts/md2docx.py`), so **nothing needs installing for that**. A free tool called pandoc is optional. It lets tailored resumes copy the styling of the friend's own Word resume.

Check, in order: `pandoc --version`, then `tools/pandoc/bin/pandoc --version`. If either works, record that command in `profile.md` under `## Tools`. If neither works, record `pandoc: none`. **Don't mention it either way.** The resume stage offers pandoc if (and only if) it would help.

### Installing pandoc (only when offered, or when the user says "install pandoc")

- Check `command -v brew`. **If Homebrew is already installed**, `brew install pandoc` is fine, then record `pandoc`.
- Otherwise, use the official release from GitHub. Get the latest release's assets from `https://api.github.com/repos/jgm/pandoc/releases/latest`. Pick the macOS zip that matches `uname -m` (`arm64` means the `arm64-macOS.zip` asset, `x86_64` means the `x86_64-macOS.zip` asset). Download it with `curl -L` into a temporary folder, unzip it, and copy its `bin/pandoc` to `tools/pandoc/bin/pandoc`. Run `tools/pandoc/bin/pandoc --version` to confirm, then record `tools/pandoc/bin/pandoc` in `profile.md`.
- If macOS blocks it ("cannot be opened because the developer cannot be verified"), run `xattr -d com.apple.quarantine tools/pandoc/bin/pandoc` and try again.
- If anything fails, don't get stuck. Say "No problem, your tailored resumes will use the kit's standard layout instead.", keep `pandoc: none`, and move on.

Python: the kit uses `python3` for spreadsheet handling. On a Mac, the first `python3` run can pop up a request to install Apple's "command line developer tools". If that happens, tell them to click **Install**, wait (a few minutes), and say when it's done. It's a normal, free Apple download.

## Stage `contact`: contact details

Ask in chat, one at a time: full name, email, phone, city and state, LinkedIn profile URL (optional, "skip" is fine). Explain: "These go at the top of your tailored resumes." Check that the email has an @ and a dot after it. Write them to `## Contact` in `profile.md`.

## Stage `resume`: their resume

1. Ask: "Now your current resume. Drag the file into this chat, or tell me where it is (Word, PDF or text is fine)."
2. Copy it into `my-search/resume/original.<ext>`, keeping the original extension. Never edit or move their own copy.
3. Convert it to `my-search/resume/master-resume.md`:
   - `.docx`: run pandoc (`<pandoc> original.docx -t gfm -o master-resume.md`). Without pandoc, unzip `word/document.xml` with Python's `zipfile` and extract the text.
   - `.pdf`: read it with your Read tool and write the text out yourself.
   - `.md` / `.txt`: copy as-is.
4. Clean up the result so it follows the structure of `templates/resume.md`: name and contact line, Summary, Experience (title, company, place, dates, bullets), Skills, Education, Certifications. **Keep their words.** Restructure, don't rewrite. Never add anything that isn't in the original.
5. Show a short summary: "I read N jobs, from <earliest> to <latest>. Most recent: <title> at <company>." Then ask: "Does that look right?" Options: "Looks right (Recommended)" / "Something's off" (ask what, and fix it). Tell them they can open `my-search/resume/master-resume.md` any time. It's the base every tailored resume starts from.
6. Record the paths under `## Resume` in `profile.md`.
7. **Only if** their original is a `.docx` **and** `pandoc: none`: ask once, "Want tailored resumes to match your own Word resume's fonts and layout? That needs a small free tool called pandoc, which I can download into this folder. No password needed. Otherwise I'll use a clean standard layout." Options: "Use the standard layout (Recommended)" / "Download pandoc and match my styling". On download, follow **Installing pandoc** above.

## Stage `criteria`: what jobs they want

Write `my-search/criteria.md` in the format of `examples/criteria.md`. Ask one topic at a time, suggesting answers based on their resume:

1. **Roles.** "Based on your resume, I'd search for: <3–4 titles>. Want to change any?" Then ask which one is their top choice and mark it `(preferred role)`. Also write a one-line **Title family** describing which titles count and which look similar but don't.
2. **Location.** Home city (use their contact city as the default) and radius. Then: remote in the US OK? Hybrid OK?
3. **Seniority.** Suggest a target from their most recent title. Ask what's too junior and too senior.
4. **Pay floor.** Annual and/or hourly. Explain: "I only drop a job for pay when the posting shows a range that's entirely below this. Jobs with no pay listed are kept." "Skip" is fine.
5. **Job types.** Full-time, contract, contract-to-hire, part-time. Multi-select.
6. **Industries.** Suggest from their resume: strong match, partial match, avoid.

## Stage `companies`: target companies

Explain: "If there are companies you'd especially like to work at, I'll rank their jobs higher, and I can check the High-priority ones' own career pages directly."

Suggest 5–10 companies from their resume and criteria, as a starting list they can edit. Ask them to add, remove, and mark each High, Medium or Low (default Medium). Write `my-search/target-companies.csv` with the columns of `examples/target-companies.csv`: `company,priority,careers_url,status,notes`. Leave `careers_url` empty. Scanning finds it. Write with Python's `csv` module, all fields quoted. An empty list is fine. Write just the header.

## Stage `sources`: job sites and plan usage

All four sources are on by default: LinkedIn, Indeed, Dice, company career pages. Explain plan usage simply and honestly:

> Each search uses a fair amount of your Claude plan. Company career pages cost the most. On a Pro plan, a weekly search is fine with the standard settings. If you hit usage limits, pick "lighter".

Options: "Standard (Recommended): all sites, up to 8 company pages per search" / "Lighter: all sites, up to 3 company pages per search" / "Choose sites myself" (multi-select). Write `## Sources` and `## Career-page limits` to `profile.md`. Leave the `## Scoring` defaults as they are (0.9 experience / 0.1 target company / 0 network, threshold 70).

## Stage `addon`: optional add-ons

Two optional extras. Ask about each separately.

1. **Unemployment.** Ask: "Are you claiming Oregon unemployment benefits? If so, the **unemployment add-on** keeps the weekly work-search record the state asks for (2 employer contacts and 3 activities a week), using the applications you track here, and gets each week's claim ready to copy into Frances Online." Options: "Not claiming, skip it (Recommended)" / "Yes, add it". If they're claiming in another state, say kindly that the add-on only knows Oregon's rules, and skip it.
2. **Network.** Ask: "The **network add-on** scores each job by who you know at that company on LinkedIn, and can map out who could introduce you. It's slower, uses more of your Claude plan, and reads your LinkedIn connections, which takes a few minutes the first time. Want it?" Options: "Not now, I can add it later (Recommended)" / "Yes, add it".

For each yes, follow `.claude/skills/add-addon/SKILL.md` for that add-on, then come back here. Skip its "first-install" offer to start right away. The first run comes next anyway. For each no, mention: "You can add it any time by saying 'add the <name> add-on'."

## Stage `first-run`: finish and try it

1. Set `setup_complete: true` in `profile.md`.
2. Ask: "Want to run a first search now? A small one takes about 5–10 minutes." Options: "Yes, a small first search (Recommended)" / "Not now".
3. On yes, follow `.claude/skills/scan-jobs/SKILL.md` with `$ARGUMENTS` = `small`, then `.claude/skills/score-jobs/SKILL.md`.
4. End with this (fill in the folder path):

   > You're set up. Here's the weekly routine:
   > 1. Say **"find new jobs"**. I search the job sites.
   > 2. Say **"score my jobs"**. I rank them against your resume.
   > 3. Open **my-search/pipeline.csv** in Excel or Numbers and sort by the score column. **Close it before asking me to search or score again.**
   > 4. Say **"tailor my resume for <company>"** for a job you like.
   > 5. When you apply, type `applied` in that row's status column.
   >
   > Say **"update the kit"** now and then to get improvements. Say **"change my settings"** any time.

## Rules

- Never type passwords, never log in for the user, never submit anything on a job site.
- Never write personal data anywhere except `my-search/`.
- If the user wants to stop partway, stop. Everything so far is saved, and saying "set me up" again resumes.
