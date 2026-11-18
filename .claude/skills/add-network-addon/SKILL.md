---
name: add-network-addon
description: Install, update or remove the optional network add-on (job-search-kit-network), which scores jobs by who the user knows at each company on LinkedIn and maps warm-introduction paths. Use when the user says "add the network add-on", "install the network add-on", "update the network add-on", or "remove the network add-on".
---

# Network add-on: install, update, remove

The network add-on lives in its own GitHub repository: `https://github.com/Jay-615/job-search-kit-network`. It isn't a standalone tool. It adds a few commands to this kit. You install it so the user never touches files or folders.

## What the add-on download contains

```
job-search-kit-network-main/
  manifest.md      # every file to copy, and where it goes
  VERSION
  CHANGELOG.md
  skills/<name>/SKILL.md ...
  agents/<name>.md ...
  examples/...
```

`manifest.md` holds a table of `source` → `destination` rows. Sources are relative to the download, and destinations relative to this kit folder. Destinations are only ever under `.claude/skills/` or `.claude/agents/`.

## Install (or update)

1. **Explain and confirm** (skip if called from setup, which has already asked): "The network add-on reads your LinkedIn connections and scores each job by who you know there. It uses more of your Claude plan. Install it?" Options: "Install (Recommended)" / "Cancel".
2. **Download** to a temporary folder:

   ```bash
   T=$(mktemp -d)
   curl -fsSL -o "$T/net.zip" https://github.com/Jay-615/job-search-kit-network/archive/refs/heads/main.zip
   cd "$T" && unzip -q net.zip
   ```

   If it fails: "I couldn't download the add-on just now. Check your internet connection and try again later." Then stop.
3. **Read `manifest.md`.** Check that every destination is under `.claude/skills/` or `.claude/agents/`. If any isn't, stop and say the download looks wrong. On an update, back up the currently installed files (from `my-search/.addons/network-manifest.md`) to `my-search/.backups/network-<old-version>-<timestamp>/`.
4. **Copy** each source to its destination, creating folders as needed. Never run anything from the download.
5. **Record it.** Copy `manifest.md` to `my-search/.addons/network-manifest.md`. In `my-search/profile.md` under `## Add-ons`, set `network: installed` and `network_version: <VERSION>`. Create `my-search/network/` if missing.
6. **Delete** the temporary folder.
7. **Weights** (first install only). Ask: "Now that network scores are available, use the standard three-way weighting (experience 50%, network 30%, target company 20%)?" Options: "Yes (Recommended)" / "Keep my current weights". On yes, set `Experience match weight: 0.5`, `Network proximity weight: 0.3`, `Target company weight: 0.2` in `## Scoring`.
8. **Next step** (first install only). Tell the user: "Installed. The first step is reading your LinkedIn connections, which takes a few minutes." Then ask: "Read my connections now (Recommended)" / "Later". On yes, follow the add-on's `build-connections` skill (`.claude/skills/build-connections/SKILL.md`).
9. New commands may need a fresh conversation before they show up in the `/` menu. Plain sentences work right away.

## Remove

1. Confirm: "Remove the network add-on? Your connections spreadsheet in my-search/network/ stays, in case you add it back."
2. Delete every destination listed in `my-search/.addons/network-manifest.md`. Delete nothing else.
3. Set `network: not installed` in `profile.md`. Ask whether to switch the weights back to 0.7 experience, 0.3 target company, 0 network.
4. Leave the `net` and bridge columns in the spreadsheet as they are.

## Rules

- Copy files only. Never execute anything from the download.
- Never write outside `.claude/skills/`, `.claude/agents/` and `my-search/`.
- The user's data in `my-search/` is never deleted.
