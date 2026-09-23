# Open-source Reference Review

Reviewed on 2026-09-24 using repository metadata and README files through the GitHub API. No repository was cloned and no third-party source code was copied.

| Repository | License | Useful reference | Adopted here | Intentionally not adopted |
|---|---|---|---|---|
| [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops) | MIT | Local-first positioning, explicit limits, and evidence-led project presentation | Honest implemented-versus-planned language and a visible user-controlled workflow | Automated job searching, CV tailoring, scoring, and agent workflows are beyond Phase 2 |
| [Gsync/jobsync](https://github.com/Gsync/jobsync) | MIT | Application tracking, dashboard summaries, and confirmation before a pasted posting is stored | Paste → extract → editable preview → explicit save; status summary cards | Its broader resume, contact, task, discovery, MCP, and deployment stack would obscure this backend-focused MVP |
| [DanielPan12/JobHuntBot](https://github.com/DanielPan12/JobHuntBot) | MIT | Small local dashboard, clear privacy boundaries, and synthetic/empty starter data | Framework-light demo UI and deliberate separation of demo data from private job-search data | Browser-driven application submission and CSV workflow automation are outside the product boundary |
| [offercontext/offerPilot](https://github.com/offercontext/offerPilot) | AGPL-3.0 | Local-first job lifecycle presentation and real-interface documentation | Six explicit Job states and screenshots tied to actual running behavior | Its multi-domain product scope and AGPL implementation were not reused; this project remains an independent MIT implementation |

## Decisions

- Keep the data model to one real entity until the Job lifecycle is stable.
- Make offline behavior useful: rule-based extraction works without an external key.
- Require explicit user confirmation between extraction and persistence.
- Prefer a small FastAPI-hosted demo over a separate frontend toolchain.
- Show real tests, screenshots, and database constraints rather than future feature mockups.

Repository names, descriptions, and license identifiers were verified from GitHub on the review date. Ideas were reimplemented against this project's own API and constraints.
