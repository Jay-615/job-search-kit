---
name: add-addon
description: Install, update or remove one of the kit's optional add-ons. The network add-on scores jobs by who the user knows at each company on LinkedIn and maps warm introductions. The unemployment add-on keeps the weekly Oregon unemployment work-search record and prepares the claim. Use when the user says "add the network add-on", "add the unemployment add-on", "install an add-on", "what add-ons are there?", "update the add-on", or "remove the … add-on".
argument-hint: "network | unemployment"
---

# Add-ons: install, update, remove

Each add-on lives in its own GitHub repository. None of them works on its own. Each adds a few commands to this kit. You install them so the user never touches files or folders.

## The add-ons

| name | repository | what it's for | ask first |
|---|---|---|---|
| `network` | `Jay-615/job-search-kit-network` | Scores each job by who the user knows there on LinkedIn, and maps warm introductions at a company. | "It reads your LinkedIn connections and uses more of your Claude plan." |
| `unemployment` | `Jay-615/job-search-kit-unemployment` | Keeps the weekly work-search record for **Oregon** unemployment benefits, checks each week is covered, and prints a copy-paste block for Frances Online. | "It's for Oregon unemployment claims only. Other states have different rules." |

If the user doesn't name one, or asks what's available, show this list in plain words and ask which.

## What each download contains

```
<repository>-main/
  manifest.md      # every file to copy, and where it goes
  VERSION
  CHANGELOG.md
  skills/<name>/... and possibly agents/<name>.md
  examples/...
```

`manifest.md` holds a table of `source` → `destination` rows. Sources are relative to the download, and destinations relative to this kit folder. Destinations are only ever under `.claude/skills/` or `.claude/agents/`.

## Install (or update)

`<name>` below is `network` or `unemployment`.

1. **Explain and confirm** (skip if called from setup, which has already asked). One sentence on what it does, plus the "ask first" note from the table. Options: "Install (Recommended)" / "Cancel".
2. **Download** to a temporary folder:

   ```bash
   T=$(mktemp -d)
   curl -fsSL -o "$T/addon.zip" https://github.com/<repository>/archive/refs/heads/main.zip
   cd "$T" && unzip -q addon.zip
   ```

   The files land in `$T/<repository name>-main/`. If the download fails, say "I couldn't download the add-on just now. Check your internet connection and try again later." Then stop.
3. **Check `manifest.md`.** Every destination must be under `.claude/skills/` or `.claude/agents/`, and must not contain `..`. If any isn't, stop and say the download looks wrong. On an update, back up the currently installed files (listed in `my-search/.addons/<name>-manifest.md`) to `my-search/.backups/<name>-<old version>-<timestamp>/`.
4. **Copy** each source to its destination, creating folders as needed. Never run anything from the download.
5. **Record it.** Copy `manifest.md` to `my-search/.addons/<name>-manifest.md`. In `my-search/profile.md` under `## Add-ons`, set `<name>: installed` and `<name>_version: <VERSION>`, adding the lines if they're missing.
6. **Delete** the temporary folder.
7. **First-install steps**, per add-on:
   - **network**: create `my-search/network/`. Ask: "Now that network scores are available, use the standard three-way weighting (experience 60%, network 30%, target company 10%)?" Options: "Yes (Recommended)" / "Keep my current weights". On yes, set `Experience match weight: 0.6`, `Network proximity weight: 0.3`, `Target company weight: 0.1` in `## Scoring`. Then: "Installed. The first step is reading your LinkedIn connections, which takes a few minutes." Ask: "Read my connections now (Recommended)" / "Later". On yes, follow `.claude/skills/build-connections/SKILL.md`.
   - **unemployment**: create `my-search/work-search/` and `my-search/work-search/filings/`. Then: "Installed. Say **log my work search** whenever you want to update this week's record, and before you file. Applications you mark `applied` in your spreadsheet count automatically." Ask: "Set up this week's record now (Recommended)" / "Later". On yes, follow `.claude/skills/log-work-search/SKILL.md`.
8. New commands may need a fresh conversation before they show up in the `/` menu. Plain sentences work right away.

## Remove

1. Confirm: "Remove the <name> add-on? Your records in my-search/ stay, in case you add it back."
2. Delete every destination listed in `my-search/.addons/<name>-manifest.md`, and that manifest copy. Delete nothing else.
3. Set `<name>: not installed` in `profile.md`.
4. **network** only: ask whether to switch the weights back to 0.9 experience, 0.1 target company, 0 network. Leave the `net` and bridge columns in the spreadsheet as they are.

## Rules

- Copy files only. Never execute anything from a download.
- Never write outside `.claude/skills/`, `.claude/agents/` and `my-search/`.
- The user's data in `my-search/` is never deleted.
