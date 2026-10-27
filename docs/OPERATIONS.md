# Operator's guide

## Supported developer setup

1. Install Python 3.12+ and Git. Docker is optional for project/task planning but required for isolated code verification.
2. Create a virtual environment and install requirements: `python -m pip install -r requirements-dev.txt`.
3. Duplicate `.env.example` as `.env`. Set `KUDU_CONTROL_TOKEN` to a strong, randomly generated secret for any shared/remote environment.
4. Set `OPENAI_API_KEY` and `KUDU_MODEL` only if you intend to call the external model. Use a currently supported Responses API model available to your account.
5. In loopback-only development enable `KUDU_DEV_MODE=1`, then run `uvicorn app.main:app --host 127.0.0.1 --port 8000` and open http://127.0.0.1:8000.
6. Register a GitHub repository via the Projects page and use Clone (public repos, or preconfigured Git credentials for private repos).
7. Create a task. Choose Generate AI Proposal after inspecting the plan. Review proposed **complete file contents** before applying.
8. Verify using the appropriate Docker profile. The included profiles currently verify only Python and JavaScript syntax.
9. Approve push to GitHub. Optionally create a pull request using `GITHUB_TOKEN` with suitable repo permissions.
10. Independently run the project's own test suite, code review, security scans and CI before merging or deploying.

## Environment configuration

| Variable | Purpose |
|---|---|
| `KUDU_CONTROL_TOKEN` | Protect remote control API |
| `KUDU_DEV_MODE` | Explicit local-only no-token preview, forbidden behind a proxy |
| `KUDU_DATABASE_PATH` | SQLite state database path |
| `KUDU_WORKSPACE_ROOT` | Root directory containing authorized workspaces |
| `OPENAI_API_KEY` | Optional model credential (server only) |
| `KUDU_MODEL` | Model ID supporting Responses API |
| `GITHUB_TOKEN` | Authenticated branch pushes and PR creation |
| `VERCEL_TOKEN` | Read-only credential check in this milestone |
| `SUPABASE_ACCESS_TOKEN` | Read-only credential check in this milestone |

## Connecting to GitHub

The current server requires an existing GitHub repository. It cannot automatically create one via the application UI. For private repositories, secure clone authentication may require a preconfigured credential helper. The secure token-based push helper only executes on explicit approval.

## Versioned distribution

The Git bundle archive preserves the local sequential Git commit history and annotated milestone tags. A verified empty GitHub repository can receive the history by cloning the bundle and pushing `main` and tags; the supplied publishing script performs milestone pushes if explicitly run.

## Deployment warning

The included Dockerfile packages the **control API/UI only**. Running Docker verification from inside an ordinary control-plane container requires a separately designed job executor; do not mount an unrestricted host Docker socket into a publicly reachable API container.

## Windows PowerShell quick start

On a Windows machine, open PowerShell in the extracted project folder and run:

```powershell
.\scripts\start.ps1
```

For the **Git history bundle** (which includes all sequential commits), run:

```powershell
git clone .\kudu-code-history.bundle kudu-code
cd kudu-code
.\scripts\publish_to_github.ps1
```

This assumes you saved the downloaded `.bundle` file next to the folder in which you are running the clone command. Create an empty `KuduKhan/kudu-code` repository first, without adding a README or license. Git must be configured with GitHub authentication appropriate to your account.
