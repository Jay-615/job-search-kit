---
name: tailor-resume
description: Write a tailored version of the user's resume for one job in my-search/pipeline.csv, as markdown and a Word document, plus a notes file listing what changed and any gaps. Never invents experience. Use when the user says "tailor my resume for <company>", "make a resume for this job", "customize my resume", or asks for changes to a tailored resume ("make it one page", "lead with X").
argument-hint: "<company name, job URL, or job id>"
---

# Tailor the resume for one job

You write a tailored resume for a single job, based on the user's master resume and that job's description. Output goes in `my-search/applications/<company>-<role>-<date>/`:

- `resume.md`: the tailored resume (the version you and the user edit)
- `resume.docx`: the same, as a Word document for attaching to applications
- `notes.md`: what you changed and why, gaps you refused to paper over, and suggestions

**You never invent experience.** You reorder, tighten and emphasize what's already in the master resume. If the job asks for something the resume doesn't show, it goes in `notes.md`, not in the resume. **You never submit anything.** The user applies themselves.

## Step 0: Preflight

1. Read `my-search/profile.md`: contact details, master resume path, original resume path, and the pandoc command under `## Tools`.
2. Read the master resume. If it's missing, say "I can't find your resume. Say **change my resume** to set it up again." Then stop.
3. Read `templates/resume.md` for section order and layout.
4. `today` = `YYYY-MM-DD`.

## Step 1: Find the job

`$ARGUMENTS` is a company name (usual), a job URL, or a job id. Read the spreadsheet with `python3 scripts/pipeline.py read`.

- **Company name**: match `company`, ignoring case. One match: use it. Several: list them (title, score, status) and ask which. None: say so, and list the closest company names.
- **URL or id**: exact match on `url` or `id`.
- **Nothing given**: show the top undecided rows (`status` new or interested, score at or above the threshold, highest first) with company, title, score and `why`, and ask which.

Then check:

- No `posting_file`, or the file is missing: "I don't have the job description saved for this one. Paste it here and I'll work from that." If they paste it, save it to `my-search/postings/<id>.md` (using `templates/job-posting.md`) and continue.
- `status` is `applied`: "You applied to this on <date>. Make another version anyway?"
- Not scored yet: that's fine. Carry on. The score isn't needed to tailor.

## Step 2: Read the job and the context

From the posting file: the description, key requirements, nice-to-haves, notes, and the `## Scoring` section if there is one. From the row: `why`, and **`notes`. If the user wrote a note on this row, respect it.** It's their judgment ("stretch role, don't oversell") and it changes how you pitch the resume.

## Step 3: The folder

`app_dir = my-search/applications/<company-slug>-<role-slug>-<today>/` (lowercase, hyphens, role slug cut to at most 50 characters **at a hyphen**, never mid-word).

If it already exists (they've tailored for this job today), ask: "Start fresh (Recommended)" / "Keep my edits and just remake the Word file" / "Cancel".

## Step 4: Write `resume.md`

Follow the section order of `templates/resume.md`:

- **Header**: name, city, email, phone and LinkedIn URL (if any) from `profile.md`.
- **Summary**: rewrite in 2–3 sentences to lead with what this job wants most, in the user's own voice from the master resume. No corporate filler ("results-driven", "passionate", "proven leader").
- **Experience**: same jobs, same titles, same dates. Within each job, put the most relevant bullets first. You may tighten wording (active verbs, keep numbers) and drop clearly irrelevant bullets (list them in `notes.md`). **Don't add bullets, claims, numbers or titles that aren't in the master resume.**
- **Skills**: reorder groups to lead with what the job asks for. Don't add skills.
- **Education, certifications**: copy exactly.
- **Length**: aim for what the master resume is (usually 1–2 pages). Don't pad.

Keep the register understated. Let numbers stand without adjectives. Prefer precise role wording ("owned the migration plan for a rewrite three teams delivered") to inflated verbs ("spearheaded a transformation").

## Step 5: Write `notes.md`

```markdown
# Notes: <company>, <title>

Drafted <today> · Score <score> · <url>

## What I emphasized
- <2–4 bullets: what leads the resume now, and why>

## Gaps (things the job asks for that your resume doesn't show)
- <one bullet per gap, specific: "Asks for SQL. Not on your resume. If you've used it, add a line yourself.">

## What I dropped or shortened
- <bullets removed or cut, and why>

## Suggestions
- <optional: small things only the user can supply, such as a metric, a project name, a tool they used but didn't list>

## What I did not do
- I didn't add any experience that isn't in your master resume.
- I didn't apply for you. You submit it when you're happy with it.
```

## Step 6: Make the Word document

There's always a way to make the Word file. Pick the first that applies:

1. **The original resume is a `.docx` and pandoc is available** (the command in `profile.md` under `## Tools`, `pandoc` or `tools/pandoc/bin/pandoc`). Use the friend's own resume as the style reference, so the tailored version keeps their fonts and spacing:

   ```bash
   <pandoc> "<app_dir>/resume.md" -o "<app_dir>/resume.docx" --reference-doc=my-search/resume/original.docx
   ```

2. **Anything else** (no pandoc, the original was a PDF or text, or step 1 failed): use the kit's built-in converter. It needs nothing installed and produces a clean, conventional resume layout:

   ```bash
   python3 scripts/md2docx.py "<app_dir>/resume.md" "<app_dir>/resume.docx"
   ```

Check that `resume.docx` exists and isn't empty. If step 1 failed and you fell back to step 2, mention it in one line ("I used the kit's standard layout rather than your own resume's styling"). If the friend's original was a `.docx` but pandoc isn't installed, mention once that saying **install pandoc** would let tailored resumes match their own styling. It's optional.

Record the folder in the row: `python3 scripts/pipeline.py update` with `[{"url": "<url>", "application_folder": "<app_dir>"}]`. If the spreadsheet is open, skip this and mention it. It isn't essential.

## Step 7: Report

```
Your tailored resume for <title> at <company> is ready:
  my-search/applications/<folder>/resume.docx   (to attach)
  my-search/applications/<folder>/resume.md     (the editable version)
  my-search/applications/<folder>/notes.md      (what I changed, and gaps to check)

Main points from the notes:
  • <2–4 most important bullets, gaps first>

Want changes? Just tell me, e.g. "make it one page" or "lead with the payments work".
When you apply, type "applied" in the status column for this job.
```

## Revisions

When the user asks for changes, edit `resume.md`, regenerate `resume.docx` the same way, and add a line to `notes.md` under a `## Revisions` heading. The no-invention rule still holds. If they ask you to add something that isn't in the master resume, ask them for the facts. If it's real experience, offer to add it to the master resume too, so future tailoring has it.
