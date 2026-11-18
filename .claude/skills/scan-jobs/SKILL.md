---
name: scan-jobs
description: Find new job postings on LinkedIn, Indeed, Dice and the user's target companies' career pages. Applies the user's filters (title, seniority, location, pay floor, job type), skips jobs already seen, drops closed postings, adds one row per new job to my-search/pipeline.csv and saves each job description to my-search/postings/. Use when the user says "find new jobs", "search for jobs", "scan for jobs", "look for new postings", or "run a search".
argument-hint: "[small]"
---

# Scan for new jobs

You search the job sites the user turned on in `my-search/profile.md`, filter out what doesn't fit `my-search/criteria.md`, skip anything already seen, and record each new job in two places:

- **A row in `my-search/pipeline.csv`**, the user's spreadsheet and the one source of truth. Written only through `scripts/pipeline.py`.
- **A job description file at `my-search/postings/<id>.md`**, because descriptions are too long for a spreadsheet cell. The row's `posting_file` column points at it.

Scoring happens afterwards in the `score-jobs` skill.

This is the most expensive command in the kit. Respect the career-page limits in `profile.md`. When something looks wrong (a CAPTCHA, a rate limit, a page that returns nothing), **say so plainly** rather than guessing. An honest "Indeed was skipped" is fine. A silently thin result is not.

**Small mode.** If `$ARGUMENTS` contains `small` (setup's first run uses this): LinkedIn plus one other enabled board, the first two roles only, at most 2 career pages, and read full descriptions for at most **10 LinkedIn jobs plus 5 from the other sources combined** (15 in total). Say at the start that this is a small first search.

## How to talk to the user

The user is probably not technical. Before starting, say one line: "Searching <sites> for <roles>. This takes about <5–15> minutes." Then work quietly. Don't narrate every page. Only stop to ask when you need them (a CAPTCHA, a login). Finish with the summary in Step 8.

---

## Step 0: Preflight

1. Read `my-search/profile.md`, `my-search/criteria.md` and `my-search/target-companies.csv`. If profile or criteria is missing, stop: "You're not set up yet. Say **set me up** and I'll walk you through it." A missing or empty target-companies file is fine. Skip career pages.
2. From `profile.md`: `## Sources` (linkedin, indeed, dice, company_career_pages, each true/false, default true) and `## Career-page limits` (`priority_filter` default High, `max_companies_per_run` default 8, `skip_if_scanned_within_days` default 3).
3. From `criteria.md`: Roles, Title family, Locations (home base city and radius, remote yes/no, hybrid yes/no), Seniority, Pay floor, Job types.
4. Run `python3 scripts/pipeline.py check-open`. If it exits 2, stop and show its message. Run `python3 scripts/pipeline.py init` (creates the spreadsheet if missing). Load existing rows with `python3 scripts/pipeline.py read --fields url,company,title,status,req_id,date_applied` for duplicate checks.
5. Load (or create as `{}`) `my-search/.cache/seen.json` and `my-search/.cache/career-page-cache.json`. Back up `seen.json` once this run with `python3 scripts/pipeline.py backup my-search/.cache/seen.json`.
6. If LinkedIn, Indeed or Dice is on, run the **Browser check** below. If Chrome isn't available, turn those sources off for this run, say so in the summary, and continue. Career pages on Lever, Greenhouse and Workday don't need Chrome.
7. `today` = today's date as `YYYY-MM-DD`.

Work files (downloaded HTML, JSON) go in `my-search/.cache/tmp/`. Delete that folder at the end of the run.

## Browser check

1. Use the Claude in Chrome tools available in this session (names usually contain `claude-in-chrome`). Load them if they're deferred. If no browser is connected: skip LinkedIn, Indeed and Dice and tell the user "Chrome isn't connected. Open Chrome, and check the Claude extension is signed in, then ask me again."
2. Get or create one working tab and reuse it for the whole run.
3. **LinkedIn login**: open `https://www.linkedin.com/feed/`. If it redirects to a login page, carry on in **logged-out mode** (Step 1-guest) and tell the user once: "You're not logged into LinkedIn in Chrome, so I can find jobs but can't confirm they're still open or truly remote. Log in and I'll check them." Never log in for them.
4. Pace: wait 2–3 seconds after each page load. No more than one browser action per second when paging.

---

## Step 1: LinkedIn

### 1a. Searches

For each role × each location mode the user accepts:

- **Near home:** `https://www.linkedin.com/jobs/search/?keywords=<role>&location=<home city, state, United States>&distance=<radius>&f_TPR=r604800`
- **US remote** (if remote is OK): `https://www.linkedin.com/jobs/search/?keywords=<role>&location=United%20States&f_WT=2&f_TPR=r604800`

`f_TPR=r604800` is "past week". Hybrid jobs near home come back from the near-home search. **`f_WT=2` is a hint, not a fact.** It returns plenty of non-remote jobs, so never mark a job Remote because of the search that found it (see 1d).

### 1b. Read the result cards

Results are `li[data-occludable-job-id]` elements. LinkedIn only fills in the text of cards near the screen, so **read what's filled, then paginate**. Don't scroll card by card (it hangs the page).

```javascript
const noise = /^(promoted|easy apply|viewed|be an early applicant|actively reviewing applicants|no longer accepting applications|medical|vision|dental|401\(k\)|·\s*\d+|\d+\s*applicants?|new|company logo|\d+ (school|company) alumni work here|see how you compare|your profile matches|reposted?)$/i;
const out = [];
for (const li of document.querySelectorAll('li[data-occludable-job-id]')) {
  const raw = li.innerText || '';
  let L = raw.split('\n').map(s => s.trim()).filter(Boolean)
    .filter(l => !noise.test(l) && !/\bwith verification$/i.test(l))
    .filter((l, i, a) => i === 0 || l !== a[i - 1]);
  if (L.length < 2) continue;  // not hydrated yet
  out.push({ id: li.getAttribute('data-occludable-job-id'), t: L[0], c: L[1], l: L[2] || '',
             ea: /\beasy apply\b/i.test(raw), pr: /\bpromoted\b/i.test(raw) });
}
```

- Read `easy_apply` and `promoted` from the raw text **before** filtering lines. Those words have to be filtered out or the company lands in the title slot.
- **The tool return is cut off at about 1,000 characters** and anything URL-shaped gets redacted. Save results into `localStorage` on the linkedin.com page (it survives navigation) and return only a count. Read them out in small chunks at the end. Build URLs yourself as `https://www.linkedin.com/jobs/view/<id>`.
- Paginate with `&start=25`, then `&start=50`. Stop after page 3 or when a page adds nothing new.
- Card text sometimes includes "N connections work here" and a pay range. Keep both. They're free.

### 1-guest. Logged-out mode

Without a login, use the public search endpoint (works with `curl`, no browser):

```
https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<q>&location=<loc>&distance=<mi>&f_TPR=r604800&start=<n>
```

- 10 results per page. Step `start` by 10, stop when a page returns fewer than 10.
- Parse with **regex**, not an HTML parser (parsers silently drop everything). Split on `data-entity-urn="urn:li:jobPosting:(\d+)"`. Pull `base-search-card__title`, `base-search-card__subtitle`, `job-search-card__location`, `time[datetime]`, `job-search-card__salary-info`.
- `keywords`, `location`, `distance`, `f_TPR` and `f_AL=true` (Easy Apply) work. `f_WT` (remote) does **not**.
- Rate limit: roughly 30 requests, then HTTP 429. Pace about 1 second apart, accept a partial result, and say which search was cut short.
- Logged out, you **can't** confirm a job is still open, truly Easy Apply, or truly remote. Mark these jobs "unverified" in the summary.
- **Remote jobs are mostly out of reach logged out.** The US-wide search returns a city for nearly every job, and the remote flag isn't readable, so the location filter drops almost everything outside the home area. If the user accepts remote work, say so plainly in the summary (see Step 8).

### 1c. Cheap filters, then a shortlist

Apply the Step 5 filters using only the card (title, company, location, pay if shown). Drop anything already in `seen.json` or already a `url` in the spreadsheet.

If more than about 40 survive (10 in small mode), **shortlist** before fetching descriptions. Rank by title fit to the preferred role, target-company priority, and pay if shown. Fetch descriptions for the top slice only. Tell the user honestly how many were set aside, and **don't** add those to `seen.json`, so they come back next time.

### 1d. Check the shortlist on the logged-in page: open? remote? pay?

About a quarter of "past week" postings are already closed. Before fetching descriptions, open each shortlisted job's logged-in page (`/jobs/view/<id>`) in batches and read three things in one short script:

```javascript
(function(){
  const T = (document.querySelector('main') || document.body).innerText.replace(/\s+/g, ' ');
  const closed = /no longer accepting applications/i.test(T);
  const mode = (T.match(/(Remote|Hybrid|On-site)\s+(Full-time|Part-time|Contract|Temporary)/i) || [])[0] || 'unknown';
  const pay = (T.match(/\$[\d,]+(?:\.\d+)?(?:\/(?:hr|yr))?\s*(?:-|–|to)\s*\$[\d,]+(?:\.\d+)?(?:\/(?:hr|yr))?/) || [])[0] || '';
  const btn = Array.from(document.querySelectorAll('button, a')).find(e => /easy apply/i.test((e.getAttribute('aria-label') || '') + ' ' + e.innerText));
  return location.pathname.split('/')[3] + '|' + (closed ? 'CLOSED' : 'open') + '|' + mode + '|' + pay + '|' + (btn ? 'EA' : '');
})()
```

- **Closed**: record in `seen.json` with status `closed`, and count it for the summary. Don't add a row.
- **Mode**: write what the page says to `mode`. If `unknown`, keep the job and record `unknown`.
- **Pay**: the page often shows a pay range that isn't in the description at all. Use it as `comp_text`. Prefer it over the description's number.
- **Easy Apply**: match "Easy Apply" in the button's label **or** text, so a renamed label doesn't silently fail. If every job comes back "not Easy Apply" on an Easy Apply search, assume the detector broke, not that there are none.

Skip this step in logged-out mode.

### 1e. Fetch descriptions with `curl`, not the browser

The public endpoint `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<id>` returns the full description, even for "Promoted by hirer" jobs whose logged-in page hides it. Fetch with `curl` into files:

```bash
mkdir -p my-search/.cache/tmp/jd
for id in $IDS; do
  curl -s -o "my-search/.cache/tmp/jd/$id.html" -w "%{http_code} $id\n" \
    -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
    "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/$id"
  sleep 1.2
done
```

Parse with Python:

- Description: regex `show-more-less-html__markup[^>]*>([\s\S]*?)</section>`. Anchoring on `description__text` captures nothing, and that reads as "no description" instead of an error.
- Title `.topcard__title`, company `.topcard__org-name-link`, location `.topcard__flavor--bullet`, posted `.posted-time-ago__text`.
- Criteria items (`.description__job-criteria-item`): Seniority level, Employment type, Job function, Industries. Use them in the filters.
- HTTP 429: wait 20 seconds and retry the failed ids. Never fetch `/jobs/view/<id>` with curl (it returns HTTP 999).
- This endpoint is cached and shows closed jobs as open. That's why 1d comes first.

### 1f. Re-check against the description

- **Location**: cards can say "United States (Remote)" when the description says another city or country. Re-apply the location filter using the description.
- **Pay**: collect every `$` amount and look for the actual salary sentence. Watch for numbers that aren't pay ("leading $35M+ programs", "projects over $50M"). A bare `$NN` with no range, no `/hr` and no `,000` needs its sentence read before it decides anything.
- **Requisition id**: if the description states the employer's req number, keep it as `req_id`.

---

## Step 2: Indeed

Searches, for each role:

- Near home: `https://www.indeed.com/jobs?q=<role>&l=<City, ST>&radius=<mi>&fromage=7`
- Remote: `https://www.indeed.com/jobs?q=<role>&l=Remote&fromage=7`

For each: open the page, wait about 3 seconds, check for a CAPTCHA (see **CAPTCHAs**), then read the cards:

```javascript
(function(){
  // Badge and metadata lines that sit between the title and the company on Indeed cards.
  const noise = /^(new|easily apply|urgently hiring|hiring multiple candidates|responsive employer|active \d+ days? ago|posted .*ago|just posted|employer active.*|view similar jobs.*|\d+(\.\d+)?|\d+(\.\d+)?\s*out of 5.*|.*reviews?|typically responds.*|responds within.*|often replies.*|replies within.*|usually responds.*|full-time|part-time|contract|temporary|.*\$[\d,].*|up to \$.*|from \$.*|.*an hour|.*a year|.*per (hour|year).*|.*benefits.*|.*shift.*|.*schedule.*|show more.*|·)$/i;
  const out = [], seen = new Set();
  for (const a of document.querySelectorAll('a[id^="job_"], a[data-jk]')) {
    const jk = a.getAttribute('data-jk') || (a.id || '').replace(/^job_/, '');
    if (!jk || seen.has(jk)) continue; seen.add(jk);
    const root = a.closest('li') || a.closest('div');
    const raw = (root ? root.innerText : '');
    const L = raw.split('\n').map(s => s.trim()).filter(Boolean).filter(l => !noise.test(l));
    // Title from the link itself when it has text. It's more reliable than line order.
    const t = (a.innerText || '').trim() || L[0] || '';
    const rest = L.filter(l => l !== t);
    out.push({ jk, t, c: rest[0] || '', l: rest[1] || '', ea: /easily apply/i.test(raw),
               pay: (raw.match(/\$[\d,.]+(?:K)?\s*(?:-|–|to)\s*\$[\d,.]+(?:K)?\s*(?:an hour|a year|per hour|per year)?/i) || [''])[0] });
  }
  localStorage.setItem('jsk_indeed', JSON.stringify(out));
  return out.length + ' cards';
})()
```

Read them back from `localStorage` in small chunks. **Sanity-check the result:** if more than a few cards have a company that looks like a badge, a date or a pay figure, the card layout has changed. Read those jobs' company from the detail page instead, and say so in the summary. `ea` is Indeed's "Easily apply" flag, so write it to `easy_apply`. The job URL is `https://www.indeed.com/viewjob?jk=<jk>`. Cheap-filter the cards, then open the detail pages for new survivors only and read the description from the page text. On the first page, if the top of the page shows "Sign in" and no "My jobs", add a note to the summary: "Indeed: searched without logging in. Logging in reduces CAPTCHAs." Don't stop.

## Step 3: Dice

Search: `https://www.dice.com/jobs?q=<role>&location=<City, ST>&radius=<mi>&radiusUnit=mi&pageSize=20&filters.postedDate=SEVEN`. For remote, add `&workplaceTypes=Remote` and drop the location.

Cards: links matching `a[href*="/job-detail/"]`. Strip the `?` query and dedupe. Title, company and location are the first lines of the card's container. Same pattern as Indeed: CAPTCHA check, cheap filter, open details for new survivors only. Don't use Dice's old RSS address (it returns the whole page).

## Step 4: Company career pages

Only if `company_career_pages` is on and `target-companies.csv` has rows.

### 4a. Pick companies

1. Keep companies at or above `priority_filter` (High = High only, Medium = High + Medium, Low = all).
2. Drop any scanned within `skip_if_scanned_within_days` (check `career-page-cache.json`).
3. Cap at `max_companies_per_run` (2 in small mode), longest-since-scanned first.

### 4b. Find each company's job board, cheapest first

Stop at the first that works. If the company's `careers_url` is filled in, start from it. If `career-page-cache.json` already knows the board type and address, use that.

1. **Lever:** `curl -s https://api.lever.co/v0/postings/<slug>?mode=json`. Try a couple of slug variants (lowercase, hyphens, no "inc"). A non-empty JSON list means you've found it. Use `descriptionPlain`, not `description`.
2. **Greenhouse:** `curl -s https://boards-api.greenhouse.io/v1/boards/<token>/jobs`. Filter titles and locations first, then fetch details only for survivors: `.../jobs/<id>?questions=false`. **Never** add `?content=true` to the list (it can be megabytes). Many companies don't publish pay through Greenhouse at all, even when their LinkedIn listing shows it. Leave `comp_text` empty rather than guessing. If the same job also came in from LinkedIn this run, use that row's pay range.
3. **Workday** (`<tenant>.wd<N>.myworkdayjobs.com/<site>`): POST `https://<tenant>.wd<N>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs` with `{"appliedFacets":{},"limit":20,"offset":0,"searchText":"<role>"}`, headers `Content-Type: application/json` and a `Referer` of the site URL. Notes:
   - `limit` max is 20 (50 gives HTTP 400). Page with `offset`. `total` only appears on the first page.
   - Detail URLs (`.../job/<externalPath>`) return 403 unless you reuse the cookies from a search POST (`curl -c jar -b jar` on both calls).
   - Work mode isn't in the list results. Read the `remoteType` facet values from a response, then re-query per facet to label jobs.
   - The `endDate` field is the deadline **plus one day**. Read the deadline from the description instead.
   - Public-sector boards often state pay **per month**. Multiply by 12 before applying the pay floor.
4. **Anything else:** open the careers page in Chrome. If it links to a known board (Lever, Greenhouse, Workday, Ashby, SmartRecruiters, iCIMS, Workable, BambooHR), follow that. Otherwise read the page text and collect job links. Open details for title-and-location survivors only.

After each company, update `career-page-cache.json`:

```json
{ "<Company>": { "last_scanned": "<today>", "url": "<what worked>", "ats": "lever|greenhouse|workday|custom", "jobs_seen": 12 } }
```

If a site blocks you, record the cache entry anyway so it isn't retried for a few days.

---

## Step 5: Filters

A job that fails any filter is **dropped**. Count each drop by reason for the summary.

1. **Title**: must fit the user's Roles and Title family in `criteria.md`. Use judgment, not exact matching.
2. **Seniority**: drop what `criteria.md` rejects. Levels listed as "also OK, scored lower" stay in.
3. **Location**: keep only jobs within the home-base radius, remote in the US (if accepted; not "Remote, Canada only"), or hybrid with an office in range (if accepted). If unclear, read the description before deciding.
4. **Pay**: drop only when a range is shown **and the whole range** is below the floor. A range that straddles the floor stays, with a note. No pay shown means keep.
5. **Job type**: drop types the user didn't pick. Unknown means keep.

Read every threshold from `criteria.md`. Never hard-code a number.

## Step 6: Already seen? Possible duplicate?

**6a. Same posting (exact).** `url` is the key. If the url is in `seen.json` or the spreadsheet, skip it. Record a job in `seen.json` only once you've **decided** about it: `"inbox"` (added), `"closed"` or `"filtered"` (with the reason). Jobs set aside by the shortlist stay out of `seen.json`. Save `seen.json` after each source.

**6b. Same job, different posting (judgment).** Compare company + normalized title (lowercase, no punctuation) with existing rows. If they match, **flag it in the summary and add the row anyway. Never merge or skip.** Only a matching `req_id`, or one of the two being closed, is real evidence they're the same job. Flag loudest when the existing row's `status` is `applied`: "Possible repeat: <title> at <company> looks like one you applied to on <date>. Worth a look before applying again."

## Step 7: Save each new job

**7a. Id.** `<source>-<today>-<company-slug>-<role-slug>`: lowercase ASCII, hyphens, punctuation dropped, role slug cut to at most 60 characters **at a hyphen** (never mid-word), `-2`/`-3` on a collision.

**7b. Description file** `my-search/postings/<id>.md`, using `templates/job-posting.md`. Fill in the frontmatter and the description, key requirements and nice-to-haves sections. Put scan observations under `## Notes` ("pay from the LinkedIn page", "card said Remote, description says Austin hybrid"). No scores in this file. `score-jobs` adds those.

**7c. Spreadsheet rows.** Write all new rows **once, at the end**, with:

```bash
python3 scripts/pipeline.py append my-search/.cache/tmp/new-rows.json
```

Each object has: `status` (`new`), `company`, `title`, `location`, `mode`, `type`, `comp_text`, `easy_apply` (`true`/`false`/empty), `posted_date` (only a real date, never one guessed from "3 days ago"), `first_seen` (today), `source`, `url`, `req_id`, `id`, `posting_file` (`my-search/postings/<id>.md`). Leave score columns empty. The helper keeps the user's columns and edits, makes a backup, and refuses to write if the file is open.

## Step 8: Summary

Keep it short and readable:

```
Done. Searched LinkedIn, Indeed, Dice and 4 company career pages.

  New jobs added: 23  (they're in my-search/pipeline.csv, marked "new")
  Already closed: 7  ·  Already seen before: 12
  Filtered out: 41  (18 wrong location, 9 too senior, 8 wrong title, 6 pay too low)
  Set aside for next time: 30  (I only read the 40 most promising this time)

  ⚠ Possible repeat: "Senior PM, Checkout" at Lumora Commerce looks like
    one you applied to on 2026-10-02. Different posting. Worth a look.

  Indeed: searched without logging in. Logging in reduces CAPTCHAs.

Next: say "score my jobs".
```

If LinkedIn ran logged out and the user accepts remote work, add this line near the top: "⚠ You're not logged into LinkedIn, so I could barely search remote jobs. Log into LinkedIn in Chrome and ask me again for a much better remote search."

Always include: closed count, set-aside count (and that they'll come back), every duplicate flag (and that nothing was merged), and any skipped or degraded source with the reason.

---

## CAPTCHAs (Indeed, Dice, sometimes LinkedIn)

Detect: page text matches `/verify you are (human|a human)|cloudflare|press and hold|are you a robot/i`, or a results page is empty when it shouldn't be.

1. Leave the page where it is, so the user sees the same thing in Chrome.
2. Ask with `AskUserQuestion`: "<Site> is asking to check you're human. What would you like to do?" Options: "I'll clear it in Chrome (Recommended): switch to Chrome, complete the check (and log in while you're there), then come back and say done." / "Skip <site> this time" / "Stop the search and save what we have".
3. **Clear it**: when they say done, reload once. If it's clear, carry on. If not, skip the site for this run without asking again.
4. **Stop**: save everything found so far (rows, description files, caches), print the partial summary, and stop.

Ask at most once per site per run. Never try to solve a CAPTCHA yourself.

## When things go wrong

- **LinkedIn "searching too fast"**: stop LinkedIn for this run and suggest waiting an hour.
- **A page's structure changed** (selectors return nothing on a page that clearly has jobs): stop that source and say which page and what you tried. Don't guess.
- **Description under about 300 characters**: try the guest endpoint (1e). If that fails too, keep the job and note "description not available" in its file.

## Known site quirks (checked late 2026; sites change)

- LinkedIn only fills in about 7–10 of 25 cards on load. Paginating is more reliable than scrolling.
- LinkedIn's `f_WT=2` (remote) search returns many hybrid and on-site jobs. About half of one sample wasn't remote.
- LinkedIn's guest description endpoint works with plain `curl`. The logged-in page is the only reliable source for open/closed, work mode and the page's pay range.
- "Promoted" and "Easy Apply" can appear together. Promoted jobs more often send you to an outside application site.
- Easy Apply at senior levels is mostly staffing agencies. Judge by the job description, not the company name.
