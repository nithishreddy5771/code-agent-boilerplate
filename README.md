# Code Agent Boilerplate

A small, self-hostable foundation for turning a product request into a reviewed draft pull request.

It deliberately contains no company-specific repositories, knowledge, credentials, issue-tracker conventions, or service integrations. Configure those at deployment time.

## What it provides

- FastAPI health and run-planning API
- A human-gated workflow: analyse → evaluate → implement → test → review → draft PR
- Typed repository contracts with edit-path allowlists
- Provider interfaces for an LLM agent, source control, test runner, and knowledge store
- Container and environment templates

## Quick start

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/uvicorn code_agent_boilerplate.api:app --reload
```

Then create a planned run:

```bash
curl -X POST http://127.0.0.1:8000/v1/runs \
  -H 'content-type: application/json' \
  -d '{
    "repository": {"id": "payments-api", "url": "git@github.com:your-org/payments-api.git", "allowed_edit_paths": ["src/", "tests/"]},
    "request": "Add idempotency keys to charge creation."
  }'
```

The starter only plans the run. Connect concrete providers before allowing implementation or PR creation.

## Integration points

Implement the protocols in `src/code_agent_boilerplate/providers.py` for your own:

- LLM/agent runtime
- GitHub, GitLab, or other source-control provider
- sandbox and test runner
- documentation or knowledge retrieval system
- Slack, Teams, web UI, or issue-tracker intake

Keep credentials in your secret manager and supply them through environment variables. Do not commit them to this repository.
