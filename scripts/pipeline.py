#!/usr/bin/env python3
"""Safe read/write helper for my-search/pipeline.csv (and other kit CSVs).

Every skill that touches the spreadsheet goes through this script, so the
rules below are enforced in one place instead of re-implemented each run:

  * refuse to write while the file is open in Excel or LibreOffice
  * back up before the first write (3 newest kept, in my-search/.backups/)
  * read and write by column NAME, keep unknown columns and untouched rows verbatim
  * never overwrite a non-empty cell in the user's own columns
  * never write a semicolon into a cell (some spreadsheet imports split on it)
  * url is the unique key: never two rows with the same url, never merge rows

Standard library only. Works with the python3 that ships with macOS.

Usage (run from the job-search-kit folder):
  python3 scripts/pipeline.py init
  python3 scripts/pipeline.py check-open
  python3 scripts/pipeline.py backup  <file>
  python3 scripts/pipeline.py read    [--status new,interested] [--unscored] [--fields a,b,c]
  python3 scripts/pipeline.py append  <rows.json>
  python3 scripts/pipeline.py update  <updates.json> [--force-user-columns]

rows.json    : a JSON list of objects, one per new row (url required).
updates.json : a JSON list of objects, each with "url" plus the columns to set.
Output is JSON on stdout. Exit code 2 means "file is open, ask the user to close it".
"""
import csv
import datetime
import glob
import json
import os
import shutil
import sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(KIT, "my-search")
PIPELINE = os.path.join(DATA, "pipeline.csv")
BACKUPS = os.path.join(DATA, ".backups")
KEEP = 3

COLUMNS = [
    "status", "company", "title", "score", "why", "notes", "date_applied",
    "applied_via", "location", "mode", "type", "comp_text", "easy_apply",
    "posted_date", "first_seen", "exp", "tgt", "net", "high_bridges",
    "med_bridges", "source", "url", "req_id", "id", "posting_file",
    "application_folder",
]
USER_COLUMNS = {"status", "notes", "date_applied", "applied_via"}


def out(obj, code=0):
    print(json.dumps(obj, indent=1, ensure_ascii=False))
    sys.exit(code)


def lock_files(path):
    d, f = os.path.split(path)
    return [
        os.path.join(d, "~$" + f),            # Excel
        os.path.join(d, ".~lock." + f + "#"),  # LibreOffice
    ]


def check_open(path=PIPELINE):
    found = [p for p in lock_files(path) if os.path.exists(p)]
    if found:
        out({"open": True,
             "message": "Your spreadsheet looks open in Excel or LibreOffice. "
                        "Please save and close it, then ask me again.",
             "lock_files": found}, code=2)
    return False


def backup(path):
    if not os.path.exists(path):
        return None
    rel = os.path.relpath(path, DATA)
    if rel.startswith(".."):
        rel = os.path.basename(path)
    dest_dir = os.path.join(BACKUPS, os.path.dirname(rel))
    os.makedirs(dest_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(dest_dir, os.path.basename(path) + ".bak-" + stamp)
    shutil.copy2(path, dest)
    old = sorted(glob.glob(os.path.join(dest_dir, os.path.basename(path) + ".bak-*")),
                 reverse=True)
    for f in old[KEEP:]:
        os.remove(f)
    return dest


def clean(value):
    if value is None:
        return ""
    s = str(value)
    s = s.replace(";", " -").replace("\r", " ").replace("\n", " ")
    return s.strip()


def load(path=PIPELINE):
    if not os.path.exists(path):
        return list(COLUMNS), []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header = [h for h in (reader.fieldnames or []) if h is not None]
        rows = [dict(r) for r in reader]
    for r in rows:
        r.pop(None, None)
    return header, rows


def save(header, rows, path=PIPELINE):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, quoting=csv.QUOTE_ALL,
                           extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({h: r.get(h, "") for h in header})
    os.replace(tmp, path)


def ensure_columns(header, needed):
    for c in needed:
        if c not in header:
            header.append(c)
    return header


def cmd_init():
    os.makedirs(DATA, exist_ok=True)
    if os.path.exists(PIPELINE):
        out({"created": False, "path": PIPELINE})
    save(list(COLUMNS), [])
    out({"created": True, "path": PIPELINE})


def cmd_read(args):
    status, unscored, fields = None, False, None
    i = 0
    while i < len(args):
        if args[i] == "--status":
            status = {s.strip().lower() for s in args[i + 1].split(",")}
            i += 2
        elif args[i] == "--unscored":
            unscored = True
            i += 1
        elif args[i] == "--fields":
            fields = [f.strip() for f in args[i + 1].split(",")]
            i += 2
        else:
            out({"error": "unknown option " + args[i]}, 1)
    header, rows = load()
    sel = []
    for r in rows:
        if status is not None and (r.get("status") or "").strip().lower() not in status:
            continue
        if unscored and (r.get("score") or "").strip():
            continue
        sel.append({f: r.get(f, "") for f in fields} if fields else r)
    out({"header": header, "count": len(sel), "total_rows": len(rows), "rows": sel})


def cmd_append(path):
    check_open()
    new = json.load(open(path, encoding="utf-8"))
    header, rows = load()
    header = ensure_columns(header, COLUMNS)
    known = {(r.get("url") or "").strip() for r in rows}
    added, skipped = [], []
    for n in new:
        url = clean(n.get("url"))
        if not url:
            skipped.append({"reason": "no url", "row": n})
            continue
        if url in known:
            skipped.append({"reason": "url already in pipeline", "url": url})
            continue
        row = {k: clean(v) for k, v in n.items()}
        row.setdefault("status", "new")
        header = ensure_columns(header, row.keys())
        rows.append(row)
        known.add(url)
        added.append(url)
    b = backup(PIPELINE) if added and os.path.exists(PIPELINE) else None
    if added:
        save(header, rows)
    out({"added": len(added), "skipped": skipped, "backup": b})


def cmd_update(path, force_user):
    check_open()
    ups = json.load(open(path, encoding="utf-8"))
    header, rows = load()
    by_url = {}
    for r in rows:
        by_url.setdefault((r.get("url") or "").strip(), r)
    changed, missing, protected = 0, [], []
    for u in ups:
        url = (u.get("url") or "").strip()
        r = by_url.get(url)
        if r is None:
            missing.append(url)
            continue
        for k, v in u.items():
            if k == "url":
                continue
            if k in USER_COLUMNS and (r.get(k) or "").strip() and not force_user:
                protected.append({"url": url, "column": k})
                continue
            header = ensure_columns(header, [k])
            r[k] = clean(v)
        changed += 1
    b = backup(PIPELINE) if changed else None
    if changed:
        save(header, rows)
    out({"updated_rows": changed, "not_found": missing,
         "kept_user_values": protected, "backup": b})


def main():
    a = sys.argv[1:]
    if not a:
        out({"error": __doc__}, 1)
    c = a[0]
    if c == "init":
        cmd_init()
    elif c == "check-open":
        check_open(a[1] if len(a) > 1 else PIPELINE)
        out({"open": False})
    elif c == "backup":
        out({"backup": backup(a[1])})
    elif c == "read":
        cmd_read(a[1:])
    elif c == "append":
        cmd_append(a[1])
    elif c == "update":
        cmd_update(a[1], "--force-user-columns" in a)
    else:
        out({"error": "unknown command " + c}, 1)


if __name__ == "__main__":
    main()
