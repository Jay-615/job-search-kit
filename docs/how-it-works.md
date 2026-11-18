# How it works

A one-page explanation for anyone curious what Claude is doing behind each command.

## 1. Finding jobs ("find new jobs")

Claude searches the sites you turned on, for each job title in your criteria, near your home city and (if you said so) remote across the US. It uses your own Chrome through the Claude in Chrome extension, so the sites see a normal person browsing at a normal pace, logged in as you.

Before reading any job in full, it drops the obvious misfits using only the summary card: wrong title, wrong level, wrong place, pay entirely below your floor, wrong job type. That's cheap. Reading full descriptions is the expensive part, so it only does that for the jobs that pass. If there are lots, it reads the most promising first and saves the rest for next time.

It also checks each shortlisted job is still open (about a quarter of last week's postings already aren't), and whether it's really remote. Job sites often label hybrid jobs as remote.

New jobs become rows in your spreadsheet, `my-search/pipeline.csv`, marked `new`. Each job's full description is saved in `my-search/postings/`. A job is never added twice. Possible duplicates (the same title at the same company under a different link) are added and flagged, never merged, so you decide.

## 2. Scoring ("score my jobs")

Each job gets two or three scores from 0 to 100:

- **Experience match**: Claude reads the description against your resume: level, years, industry, skills, and any required qualifications. This is the main one.
- **Target company**: High-priority companies on your list score 100, Medium 60, Low 20, and companies not on it 0. It counts for only 10%, so it nudges your favorites up without hiding good jobs elsewhere.
- **Network** (only with the add-on): who you know there, weighted by how well you know them.

They're combined with weights from your settings (90% experience and 10% target company by default, or 60% experience, 30% network and 10% target company with the network add-on). A job whose title is exactly your top-choice title gets a small bonus. The `why` column says in a few words what drove each score.

Scores are a sorting aid, not a verdict. Your own notes and status in the spreadsheet always win. Claude never changes them.

## 3. Tailoring ("tailor my resume for …")

Claude starts from your master resume (`my-search/resume/master-resume.md`), rewrites the summary for this job, puts the most relevant bullets first, tightens wording, and drops what's clearly off-topic. **It never adds experience you don't have.** Anything the job asks for that your resume doesn't show goes into `notes.md` as a gap for you to judge.

The Word version uses a clean standard layout. If you gave a Word resume and the optional converter (pandoc) is installed, it copies your own resume's styling instead.

## What it won't do

- Apply for jobs, or submit anything on a website
- Log in for you, or solve "are you human?" checks
- Invent experience
- Run on its own schedule. Nothing happens unless you ask.
