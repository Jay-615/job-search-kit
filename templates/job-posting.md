---
id: {{source}}-{{yyyy-mm-dd}}-{{company-slug}}-{{role-slug}}
source: {{linkedin | indeed | dice | career-page}}
url: {{full URL to the posting}}
posted_date: {{yyyy-mm-dd, or empty if not shown}}
fetched_date: {{yyyy-mm-dd}}
company: {{Company name}}
title: {{Job title exactly as posted}}
location: {{City, State, or "Remote (US)"}}
mode: {{Remote | Hybrid | Onsite | unknown}}
type: {{full-time | contract | contract-to-hire | part-time | unknown}}
comp_disclosed: {{true | false}}
comp_text: "{{pay range exactly as shown, e.g. "$150,000 - $190,000" or "$90/hr". Empty if not shown.}}"
comp_floor_met: {{true | false | null}}
req_id: {{employer's requisition number if the posting states one, else empty}}
---

## Job Description

{{Full job description text, as posted. Keep paragraph breaks. Strip boilerplate footers (EEO, benefits legalese) only if the file runs past about 6,000 words.}}

## Key Requirements (extracted)

- {{A must-have from the posting: years of experience, domain, etc.}}
- {{A required skill or method.}}
- {{Tools or platforms named.}}
- {{Education or certification requirements, if any.}}

## Nice-to-haves (extracted)

- {{Stated "nice to have" or "bonus" qualifications.}}

## Notes

{{Observations from the scan. For example: "Pay range from the LinkedIn page, not the description." or "Card said Remote but the description says Austin hybrid." Optional.}}

<!-- score-jobs appends a "## Scoring" section below this line. -->
