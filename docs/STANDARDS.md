# Python FastAPI + uv + Pydantic Project Scaffold (Standard)

**Purpose:**  
This standard defines a repeatable structure for new Python projects using FastAPI, uv, and Pydantic. The only allowed
differences across implementations are domain-specific logic; tooling, configuration, and structure must remain
consistent.

---

## Scaffold Checklist

### 1. Repository Structure

- Top-level: `src/`, `tests/`, `docs/`, `scripts/`, `data/` (for persistence), and optionally `mock_data/`.
- Importable code goes under `src/[package_slug]/` (organized into `api`, `services`, `db`, `config`, `cli`, etc.).
- No runtime code outside of `src/`.
- Docs:
  - `README.md` (quick start with `uv sync`, API docs at `/api/docs`, CLI/dock/test/config instructions)
  - `docs/requirements.md` when you are capturing net-new requirements; omit it for already-built reference repos if the
    README covers outcomes.
  - `docs/ARCHITECTURE.md` (can stay lightweight—one diagram/table is enough unless the system is complex) plus any
    domain-specific docs.
  - `scripts/` for DB/migrations/fixtures.

### 2. Tooling & Dependencies

- Use **uv** only (`uv sync`, `uv run`), never `pip` or `poetry`.
- Ship `pyproject.toml` & `uv.lock`. Pin Python **3.12+**.
- Required core deps: `fastapi`, `uvicorn`, `pydantic`, and `pydantic-settings`. Add domain-specific libraries only when
  the implementation actually uses them.
- Optional deps: `typer` (only if you expose a CLI), `httpx` (only when you make outbound HTTP calls), `python-dateutil`
  (only if you parse arbitrary dates). If the project does not exercise those paths, omit them from `pyproject.toml` and
  the lockfile.
- Entry points (`FastAPI`, CLI): must be importable with no side effects. When you ship a CLI, define it under
  `[project.scripts]`; if no CLI exists, skip that configuration entirely.
- Tests via `uv run python -m pytest`.

### 3. Configuration & Environment

- Use `pydantic-settings` for config; support `.env` and environment variables.
- Env vars: namespace (e.g., `PROJECT_SLUG_DATABASE_URL`) and document all in `README.md`.
- Provide `.env.example` if multiple required.
- Always set `PYTHONPATH=/app/src` for Docker/scripts.
- Helper launch scripts (`start.sh`, `start_docker.sh`) if interactive flows.
- Any AI plumbing must stay model-agnostic: prefer `pydantic-ai`, DSPy abstractions, or Vercel AI SDK wired through
  OpenRouter(or another broker) so swapping providers never requires code edits. Capture all provider-specific options
  as env vars.

### 4. FastAPI & Optional UI Surface

- API entrypoint (when needed) lives in `src/[package_slug]/api/main.py`, routers by feature.
- Swagger at `/api/docs`, ReDoc at `/api/redoc` (enabled).
- Optional UI layers (FastUI dashboards or other views) mount under `/ui/...` only when the product actually ships that
  surface; include their build/setup docs alongside.
- Pydantic models for I/O in `src/[package_slug]/models/`.
- Validate input, ensure timezone-aware dates.
- Health check at `GET /healthz` (returns version, git SHA (if present), uv sync time).

### 5. Data Access & Services (Optional)

- Only scaffold these pieces when the project persists data or needs a shared service layer.
- When present: API/CLI share the same service abstractions, Pydantic I/O models stay separate from DB schemas, and
  migrations/bootstrap helpers live in `scripts/` with docs in `docs/DATABASE_SETUP.md`.
- Default: SQLite at `/data/[project].db` (configurable via env). Remote deployments can swap to Turso (or another
  hosted DB) by overriding the env vars; capture the decision in README.

### 6. Testing

- `tests/`: unit tests, API route tests (`TestClient`), CLI smoke tests.
- Integration tests marked with `@pytest.mark.integration` (skip with `-m "not integration"`).
- Pytest config: `[tool.pytest.ini_options]` in `pyproject.toml` (set `pythonpath = ["src"]`).
- Even when tests pass, log the key outputs (classifications, payloads, timings, etc.) via `pytest`'s `log_cli` so
  humans can review real model responses without rerunning demos.

### 7. Docs & Developer Experience

- Focused docs in `docs/`: `DATABASE_SETUP.md`, `API_REFERENCE.md`, `UI_ARCHITECTURE.md` (only include what the surface
  area needs, but always link from README). `ARCHITECTURE.md` can be a simple diagram/table unless the system truly
  requires deeper explanation.
- Keep every doc concise and easy to scan (prefer tables/diagrams over prose) so humans can ingest it quickly.
- Add sample data in `mock_data/` and instructions when fixtures matter.
- Onboard: show how to sync deps, run CLI/API, seed DB, use stubs, etc., and explicitly flag any open decisions where
  the agent must check with a human before proceeding.

### 8. Docker & Railway Deployment (Updated)

- Provide a multi-stage Dockerfile:
  - **Builder**: `FROM python:3.12-slim`, copy `pyproject.toml`+`uv.lock`, install `uv` from
    `ghcr.io/astral-sh/uv:latest`, `uv sync --frozen --no-dev`, copy `src/` & `scripts/`.
  - **Runtime**: `FROM python:3.12-slim`, install OS deps as needed, set `ENV PYTHONUNBUFFERED=1`,
    `ENV PATH="/app/.venv/bin:${PATH}"`, `ENV PYTHONPATH="/app/src"`, copy `.venv` from builder, expose `8080` (or
    `$PORT` for Railway), default CMD `uvicorn [package_slug].api.main:app --host 0.0.0.0 --port ${PORT:-8080}`.
- Always read/write persistent data from `/data` (mount to `data/` locally).
- Document build/run/volume/env instructions in README.
- Railway: Dockerfile must be simple, no custom build args; ensure `PORT` env works; consult latest
  [Railway FastAPI guide](https://docs.railway.app/deploy/fastapi) for best practices.

### 9. Delivery Quality Gates

- `uv sync` must succeed clean.
- All local tests pass (`uv run python -m pytest`); document skipped tests if any.
- FastAPI runs on `0.0.0.0:8080`+ docs endpoints.
- Docker image builds; container serves FastAPI as above.
- README covers all major workflows, with copy-paste commands.
- Add "Next Steps" or "Operational Notes" for future devs.

### 10. Agent Metadata

- Create `AGENT.md` summarizing these standards, boilerplate prompt, and update instructions for future agent usage.

### 11. IDE Settings: Auto-Scaffold & Best Practices

- **VSCode**

  - **Pre-scaffolded:**

    - Add `.vscode/settings.json` with at least these defaults (pre-created in every scaffold):

      ```json
      {
        "files.exclude": {
          "**/.venv": true,
          "**/__pycache__": true
        },
        "search.exclude": {
          "**/.venv": true,
          "**/__pycache__": true
        },
        "peacock.color": "#832561",
        "workbench.colorCustomizations": {
          "activityBar.background": "#ab307e",
          "activityBar.foreground": "#e7e7e7",
          "statusBar.background": "#832561",
          "titleBar.activeBackground": "#832561"
        },
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.formatOnSave": true,
          "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
          }
        },
        "ruff.enable": true,
        "ruff.lineLength": 120,
        "ruff.fixAll": true,
        "ruff.organizeImports": true,
        "editor.rulers": [120],
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.autoImportCompletions": true
      }
      ```

    - Add `.vscode/extensions.json` with recommended extensions:

      ```json
      {
        "recommendations": ["ms-python.python", "charliermarsh.ruff", "johnpapa.vscode-peacock"]
      }
      ```

    - This ensures `.venv` and `__pycache__` are hidden in file explorer and searches, workspace color is set via
      [Peacock](https://marketplace.visualstudio.com/items?itemName=johnpapa.vscode-peacock), and Python
      formatting/linting is configured with Ruff (line length 120, format on save enabled).

  - **Recommended Extensions:**
    - **Python** (`ms-python.python`): Core Python language support, IntelliSense, debugging
    - **Ruff** (`charliermarsh.ruff`): Fast Python linter and formatter (replaces Black, isort, flake8, etc.) - handles
      both formatting and linting
    - **Peacock** (`johnpapa.vscode-peacock`): Workspace color customization for easy context-switching
  - **Manual steps:**
    - VSCode will prompt to install recommended extensions when opening the workspace.
    - Ruff should be included in `pyproject.toml` dependencies (not dev dependencies) so `uv run ruff` works.
    - Configure Ruff in `pyproject.toml` under `[tool.ruff]` with `line-length = 120`.
    - Note: Ruff's formatter preserves triple-quoted strings as-is by design; long strings in data files may need manual
      wrapping if desired.

- **PyCharm**

  - **Pre-scaffolded:**
    - Include a pre-built `.idea/.gitignore` to ensure IDE files are NOT committed.
  - **Manual steps:**
    - Right-click `.venv` and `__pycache__` in the file tree → "Mark Directory as → Excluded".
    - Recommend setting a project color via:  
      `File → Settings → Appearance & Behavior → Project View → Project Colors` for easy context-switching.

- **Zed**

  - **Pre-scaffolded:**

    - If Zed supports project/workspace settings file (e.g. `.zed/settings.json`), add it with:

      ```json
      {
        "file_exclude_patterns": ["**/.venv/**", "**/__pycache__/**"]
      }
      ```

      _(If not, document in README how to configure this manually in workspace settings)_

  - **Manual steps:**
    - Document updating/excluding patterns via workspace UI.
    - Advise users to set a workspace accent color if available.

> **Scaffolding Principle:**
>
> - Provide these settings files _by default_ so every new project hides virtualenvs, caches, and has fast context cues
>   (colors).
> - Where only manual steps are possible (e.g. exclusion in PyCharm, workspace color in Zed), explain clearly in
>   onboarding docs.

- **Always:**
  - Pre-create and commit VSCode and IDE ignore files in the template (not user secrets).
  - Add quick-reference setup steps to the project README (“First steps in your IDE”).

### 12. Add and Pre-Approve Chrome Dev Tools MCP(s)

- **Purpose**: Ensure browser debugging tools are available by default for local development, and _pre-approve_
  automation commands where possible for both Claude and Codex agents.

#### Steps

- **Add the Chrome Dev Tools MCP**  
  Register the Chrome Dev Tools Multi-Command Package by running:

  ```bash
  claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
  codex mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
  ```

- **Pre-Approval: Claude**  
  In `.claude/settings.json`, pre-approve _all_ CLI commands required by the project **including**
  `npx chrome-devtools-mcp@latest`:

  ```jsonc
  {
    // ...existing config...
    "permissions": {
      "allow": [
        "Bash(uv venv:*)",
        "Bash(source .venv/bin/activate)",
        "Bash(uv pip install:*)",
        "Bash(python:*)",
        "Bash(wait)",
        "Bash(git add:*)",
        "Bash(git commit:*)",
        "mcp__chrome-devtools__list_console_messages",
        "mcp__chrome-devtools__click",
        "mcp__chrome-devtools__fill",
        "mcp__chrome-devtools__fill_form",
        "mcp__chrome-devtools__get_network_request",
        "mcp__chrome-devtools__list_network_requests",
        "mcp__chrome-devtools__close_page",
        "mcp__chrome-devtools__handle_dialog",
        "mcp__chrome-devtools__list_pages",
        "mcp__chrome-devtools__navigate_page",
        "mcp__chrome-devtools__new_page",
        "mcp__chrome-devtools__resize_page",
        "mcp__chrome-devtools__select_page",
        "mcp__chrome-devtools__performance_stop_trace",
        "mcp__chrome-devtools__take_screenshot",
        "mcp__chrome-devtools__evaluate_script",
        "mcp__chrome-devtools__take_snapshot",
        "mcp__chrome-devtools__wait_for",
        "mcp__chrome-devtools__performance_start_trace",
        "mcp__chrome-devtools__performance_analyze_insight",
        "mcp__chrome-devtools__get_console_message",
        "mcp__chrome-devtools__drag",
        "mcp__chrome-devtools__emulate",
        "mcp__chrome-devtools__hover",
        "mcp__chrome-devtools__navigate_page_history",
        "mcp__chrome-devtools__press_key",
        "mcp__chrome-devtools__upload_file"
        // Add more MCPs/commands as needed for your project
      ],
      "deny": [],
      "ask": []
    }
  }
  ```

  - **Tip:** Any additional MCPs you install should also have their primary commands pre-approved in this list for a
    smoother developer experience (no permission prompts).

- **Pre-Approval: Codex**

  - _Codex does **not** currently support a centralized "pre-approve" commands setting like Claude does_.
  - Instead, use Codex agent's available mechanisms (e.g. `codex settings` or agent UI) to manually allow trusted
    commands if prompted. _Document any manual steps for Codex users in your project README as needed_.

- **Principle**:

  - **By default**, all routine dev automation commands and installed MCPs should be included in the predefined "allow"
    list for Claude.
  - New MCPs = update `allow` list accordingly. Ensure this standard is reflected in your project template.

- **Summary**:
  - Register `chrome-devtools` MCP (and any others your workflow needs).
  - Update `.claude/settings.json` to pre-approve their execution commands.
  - For Codex, document any steps to avoid repeated permission prompts.

### 13. Human Decision Prompts

- Agents must pause and ask the human owner for decisions that affect contracts, data retention, external integrations,
  UI scope, or deployment targets. Log approvals (who/when/what) in README or ARCHITECTURE.md (brief notes alongside
  diagram).
- When specs are ambiguous, capture the open question inline (e.g., `TODO(HUMAN_DECISION): ...`) and block delivery
  until resolved.
- Keep decision logs concise—one sentence per decision is enough for traceability.

---

---

## How to Use This Standard

1. Replace all `[PROJECT_NAME]`, `[package_slug]`, and placeholders as appropriate for your app.
2. Share this entire checklist with any agent tasked with scaffolding a new project; no extra commentary required unless
   project constraints demand it.
3. Review all deliverables for compliance with each checklist item; require justification for any deviations.
