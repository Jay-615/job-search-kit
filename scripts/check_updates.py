#!/usr/bin/env python3
"""Quiet weekly check for a newer version of the kit and its installed add-ons.

Run at the start of a session (from the job-search-kit folder):
  python3 scripts/check_updates.py            # checks at most once every 7 days
  python3 scripts/check_updates.py --force    # checks now (used by update-kit)

It only reads version numbers from GitHub. It never downloads or changes any
program files, and it writes one small file: my-search/.cache/update-check.json.

Output is JSON on stdout:
  {"checked": false}                                  not due yet, or no network
  {"checked": true, "updates": []}                    everything is current
  {"checked": true, "updates": [{"name": "kit", "current": "1.1.0", "latest": "1.2.0"}, ...]}

It always exits 0 and never prints errors, so a failed check never bothers the user.
Standard library only. Works with the python3 that ships with macOS.
"""
import datetime
import json
import os
import re
import subprocess
import sys

KIT_REPO = "Jay-615/job-search-kit"
# Keep in step with the table in .claude/skills/add-addon/SKILL.md.
ADDON_REPOS = {
    "network": "Jay-615/job-search-kit-network",
    "unemployment": "Jay-615/job-search-kit-unemployment",
}
CHECK_EVERY_DAYS = 7
CACHE = os.path.join("my-search", ".cache", "update-check.json")
PROFILE = os.path.join("my-search", "profile.md")


def parse_version(text):
    m = re.match(r"\s*(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(x) for x in m.groups()) if m else None


def remote_version(repo):
    url = "https://raw.githubusercontent.com/%s/main/VERSION" % repo
    try:
        out = subprocess.run(["curl", "-fsSL", "--max-time", "10", url],
                             capture_output=True, text=True, timeout=15)
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def installed_addons():
    """Return {name: version} for add-ons profile.md lists as installed."""
    try:
        with open(PROFILE, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return {}
    found = {}
    for name in ADDON_REPOS:
        if re.search(r"^\s*-?\s*%s:\s*installed\s*$" % name, text, re.M):
            m = re.search(r"^\s*-?\s*%s_version:\s*(\S+)" % name, text, re.M)
            found[name] = m.group(1) if m else "0.0.0"
    return found


def main():
    force = "--force" in sys.argv[1:]
    if not os.path.isdir("my-search"):
        print(json.dumps({"checked": False}))
        return
    today = datetime.date.today()

    if not force:
        try:
            with open(CACHE, encoding="utf-8") as f:
                last = datetime.date.fromisoformat(json.load(f)["last_checked"])
            if (today - last).days < CHECK_EVERY_DAYS:
                print(json.dumps({"checked": False}))
                return
        except Exception:
            pass  # no cache or unreadable: check now

    try:
        with open("VERSION", encoding="utf-8") as f:
            local_kit = f.read().strip()
    except OSError:
        local_kit = "0.0.0"

    checks = [("kit", local_kit, KIT_REPO)]
    for name, ver in installed_addons().items():
        checks.append((name, ver, ADDON_REPOS[name]))

    updates = []
    reached = False
    for name, current, repo in checks:
        latest = remote_version(repo)
        if latest is None:
            continue
        reached = True
        if (parse_version(latest) or (0,)) > (parse_version(current) or (0,)):
            updates.append({"name": name, "current": current, "latest": latest})

    if not reached:
        # Offline: don't record a check, so it tries again next session.
        print(json.dumps({"checked": False}))
        return

    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump({"last_checked": today.isoformat(), "updates": updates}, f)
    except OSError:
        pass
    print(json.dumps({"checked": True, "updates": updates}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(json.dumps({"checked": False}))
