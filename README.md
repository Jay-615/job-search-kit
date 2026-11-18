# job-search-kit

A job-search helper that runs in Claude on your Mac. It searches LinkedIn, Indeed, Dice and the career pages of companies you care about, scores each job against your resume, and writes a tailored version of your resume for the ones you want to apply to.

It doesn't apply for you. It does the searching, sorting and first drafts, so your time goes on the applications themselves.

## What you need

- A **Mac**
- The **Claude desktop app** ([download](https://claude.com/download)) with a **Pro or Max** plan. Pro is fine for a weekly search; Max gives more room.
- **Google Chrome**, with the **[Claude in Chrome](https://claude.com/claude-in-chrome)** extension (setup walks you through this)
- A **LinkedIn** account, and your current resume (Word, PDF or text)

## Get started

1. On this page, click the green **Code** button, then **Download ZIP**. Unzip it and move the `job-search-kit` folder into your Documents folder. (If the folder is called `job-search-kit-main`, that's fine, or rename it.)
2. Open the **Claude** app, go to the **Code** tab, and open the `job-search-kit` folder. If Claude asks whether you trust this folder, say yes. That lets the kit run its everyday steps without asking you each time.
3. Type: **set me up**

Claude takes it from there. It checks Chrome, asks about you and the jobs you want, and runs a first search with you. It takes about 10 minutes.

## Every week

| Say this | What happens |
|---|---|
| **find new jobs** | Searches the job sites and adds new matches to your spreadsheet |
| **score my jobs** | Ranks them against your resume |
| *(open `my-search/pipeline.csv` in Excel or Numbers and sort by score)* | You pick the ones you like |
| **tailor my resume for Acme** | Writes a tailored resume, as a Word file and editable text |
| *(type `applied` in the status column when you apply)* | Keeps track for you |

Close the spreadsheet before asking Claude to search or score, so your edits and Claude's don't collide.

Also: **change my settings** and **update the kit**. Claude checks for a newer version about once a week and tells you when there is one. There are two optional add-ons, described below.

## Your privacy

Everything about your search stays in the `my-search` folder on your Mac. Nothing is uploaded anywhere except your normal conversation with Claude, and Chrome visiting job sites as you.

## Optional add-ons

- **Network.** Scores each job by who you know at that company on LinkedIn, and maps out who could introduce you. It uses more of your Claude plan. Say **add the network add-on**.
- **Unemployment (Oregon only).** Keeps the weekly work-search record Oregon asks for, built from the applications you track here, and gets each week's claim ready to copy into Frances Online. Say **add the unemployment add-on**.

---

<sub>Prefer git? `git clone https://github.com/Jay-615/job-search-kit.git`, then open the folder in Claude the same way. Licensed MIT.</sub>
