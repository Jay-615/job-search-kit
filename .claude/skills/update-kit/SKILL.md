---
name: update-kit
description: Update job-search-kit (and the network add-on, if installed) to the latest version from GitHub without touching the user's own data in my-search/. Use when the user says "update the kit", "check for updates", "get the latest version", or "upgrade".
---

# Update the kit

You bring the program files up to date from GitHub. **The user's data in `my-search/` and downloaded tools in `tools/` are never touched.** Git isn't required.

Source: `https://github.com/Jay-615/job-search-kit` (branch `main`).

## Step 1: Is there a newer version?

1. Read the local `VERSION`.
2. Fetch the latest: `curl -fsSL https://raw.githubusercontent.com/Jay-615/job-search-kit/main/VERSION`.
3. If they match: "You're on the latest version (<version>)." Then go to Step 5 (the add-on check), then stop.
4. If the fetch fails, tell the two cases apart (`curl -sS -o /dev/null -w "%{http_code}"` on the same URL):
   - **No connection** (curl can't connect, status `000`): "I couldn't reach GitHub just now. Check your internet connection and try again later."
   - **404 or another HTTP error**: "I reached GitHub, but couldn't find the kit's update page. It may have moved. Ask whoever shared the kit with you for the current link." Don't mention the internet connection in this case.
   Then stop.

## Step 2: Download and compare

1. Download into a temporary folder (never inside `my-search/`):

   ```bash
   T=$(mktemp -d)
   curl -fsSL -o "$T/kit.zip" https://github.com/Jay-615/job-search-kit/archive/refs/heads/main.zip
   cd "$T" && unzip -q kit.zip
   ```

   The files land in `$T/job-search-kit-main/`.
2. Read the new `CHANGELOG.md`. Find the entries newer than the local version.
3. List which program files would change, be added or be removed. Compare these paths only: `.claude/skills/`, `.claude/settings.json`, `scripts/`, `templates/`, `docs/`, `examples/`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`, `.gitignore`. **Skills installed by add-ons are not part of the kit.** Leave every path listed in any `my-search/.addons/*-manifest.md` alone.

## Step 3: Confirm

Tell the user in plain words what's new (from the changelog, not the file list), then ask: "Update now (Recommended)" / "Not now".

## Step 4: Apply

1. Back up the current program files to `my-search/.backups/kit-<old-version>-<timestamp>/` (the same paths as Step 2.3).
2. Copy the new versions of those paths over the old ones. Delete program files that no longer exist upstream, but only inside `.claude/skills/<kit skill>/`, `scripts/`, `templates/`, `docs/` and `examples/`, and never an add-on skill.
3. Delete the temporary folder.
4. If any changelog entry has a **Migration** section (a new setting), apply it: ask for the new value, or write the stated default into `my-search/profile.md`.
5. Confirm: "Updated to <new version>. <one-line summary>." Mention that a backup of the old version is in `my-search/.backups/` in case anything looks wrong.

## Step 5: Add-ons

For each add-on that `my-search/profile.md` lists as `<name>: installed` (see the table in `.claude/skills/add-addon/SKILL.md` for each one's repository), compare its `<name>_version` with `https://raw.githubusercontent.com/<repository>/main/VERSION`. If it's newer, offer to update it. If they agree, run the install steps in `.claude/skills/add-addon/SKILL.md` in update mode.

## Rules

- Never delete or overwrite anything in `my-search/` or `tools/`.
- Never run anything from the download except copying files.
- If anything fails partway, restore from the backup made in Step 4.1 and say what happened.
