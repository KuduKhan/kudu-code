# KUDU CODE API (v1.0 preview)

Control API (all endpoints except health require `Authorization: Bearer <KUDU_CONTROL_TOKEN>` when deployed remotely). Local loopback may omit the token. All operations under `/api` return JSON.

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness, public |
| GET | `/api/overview` | Real project/task counts |
| GET, POST | `/api/projects` | List and register projects |
| GET | `/api/projects/{id}` | Project metadata |
| POST | `/api/projects/{id}/clone` | Clone public GitHub repository into scope |
| GET | `/api/projects/{id}/repository` | Read checkout state |
| GET, POST | `/api/tasks` | List and plan tasks |
| GET | `/api/tasks/{id}` | Task details and stages |
| POST | `/api/tasks/{id}/propose` | AI file proposal; configured API credentials required |
| POST | `/api/tasks/{id}/apply` | Explicit approval `{ "confirm": true }` and local feature commit |
| POST | `/api/tasks/{id}/verify` | Docker language parser verification with `{ "command": "python-syntax" }` or `javascript-syntax` |
| POST | `/api/tasks/{id}/push` | Explicitly approved task-branch push `{ "confirm": true }` |
| POST | `/api/tasks/{id}/pull-request` | Explicit GitHub PR creation `{ "confirm": true }` |
| POST | `/api/tasks/{id}/cancel` | Cancel eligible tasks |
| GET | `/api/agents` | Available task roles |
| GET | `/api/toolchains` | Supported sandbox verification profiles |
| GET | `/api/integrations` | Configured providers, without credentials |
| GET | `/api/integrations/{provider}/check` | External read-only authentication check |
| GET | `/api/events` | Recorded application events |

## Task state machine

`planned → awaiting_approval → implemented → verified → completed`. Failed syntax verification sets `verification_failed`; retry is supported. `planned`, `awaiting_approval`, and `failed` states may be cancelled. Provider errors never imply a successful operation.

`completed` in this preview means a **verified task branch was pushed**, not that a pull request was merged, production is deployed, or feature behavior has been comprehensively tested.

## API security

No remote API access is permitted without a configured server-side token. Deploy only behind TLS, identity-aware routing and rate limits. Prevent broad public access to your Docker daemon. Do not place provider tokens in frontend JavaScript.
