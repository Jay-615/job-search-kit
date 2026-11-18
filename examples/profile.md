# Profile

*Example for a fictional person, Sam Chen. Setup writes your real version to `my-search/profile.md`. You can edit that file by hand at any time, or just tell Claude what to change.*

## Contact
- Name: Sam Chen
- Email: sam.chen@example.com
- Phone: (206) 555-0142
- Location: Seattle, WA
- LinkedIn URL: https://www.linkedin.com/in/example-sam-chen

## Resume
- Master resume: my-search/resume/master-resume.md
- Original file: my-search/resume/original.docx

## Scoring
- Experience match weight: 0.7
- Target company weight: 0.3
- Network proximity weight: 0
- Threshold: 70

## Sources
- linkedin: true
- indeed: true
- dice: true
- company_career_pages: true

## Career-page limits
- priority_filter: High
- max_companies_per_run: 8
- skip_if_scanned_within_days: 3

## Tools
- pandoc: pandoc

## Add-ons
- network: not installed

## Setup progress
- setup_complete: true
- completed_stages: chrome, linkedin, pandoc, contact, resume, criteria, companies, sources, addon, first-run
