# Automation Layer (GitHub Webhooks)

Initial GitHub webhook automation is now available.

- **Endpoint:** `POST /api/automation/github-webhook/`
- **Auth:** HMAC signature via `X-Hub-Signature-256` using `GITHUB_WEBHOOK_SECRET`
- **Supported events:** `push`, `pull_request` (stateful actions only), `ping`
- **Deduplication:** Skips if a LearningEntry already contains the delivery marker `GitHub Delivery ID: <delivery-id>`
- **Heuristic mapping:** Tries to link to a roadmap item if its title appears in the commit messages (case-insensitive).

### How it works (push events)
1) Validates signature  
2) Aggregates all commits in the push into one entry  
3) Saves a public LearningEntry with commit summaries and delivery ID marker  
4) Returns counts of created/skipped entries

### How it works (pull_request events)
1) Validates signature  
2) Processes only actionable states (`opened`, `closed`, `reopened`, `ready_for_review`)  
3) Creates a LearningEntry with PR title, state, branches, URL, labels, and description  
4) Uses the delivery ID for deduplication  

### Environment
Set `GITHUB_WEBHOOK_SECRET` in the backend environment (and GitHub webhook settings) so signatures can be verified.
