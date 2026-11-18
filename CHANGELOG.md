# Changelog

## 1.1.0

New optional **unemployment add-on** for Oregon claimants: say "add the unemployment add-on". The add-on installer now handles both add-ons (the `add-network-addon` command is now `add-addon`, and "add the network add-on" still works). Also includes the fixes from the first full test: fairer scoring weights (jobs at companies not on your list can now reach the top), cleaner Indeed results, a clearer LinkedIn-login choice, Word resumes that need nothing installed, and fewer permission prompts.

**Migration**
- In `my-search/profile.md` under `## Add-ons`, add `- unemployment: not installed` if it's missing.
- If `## Scoring` still has the old defaults (experience 0.7, target company 0.3, network 0), ask: "Scoring now leans more on how well a job fits you. Switch to the new default (90% fit, 10% target company)?" On yes, write 0.9 / 0.1 / 0. If the network add-on is installed and the weights are 0.5 / 0.3 / 0.2, offer 0.6 / 0.3 / 0.1 the same way. Leave any other custom weights alone.

Each entry lists what changed and, under **Migration**, any new setting `/update-kit` should ask for or default. An entry with no Migration section needs nothing from the user.

## 1.0.0

First release. Guided setup, job scanning (LinkedIn, Indeed, Dice, company career pages), scoring, tailored resumes in markdown and Word, self-update, and an installer for the optional network add-on.
