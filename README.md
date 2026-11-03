# Code Agent Boilerplate

A small, self-hostable foundation for turning a product request into a reviewed draft pull request.

It deliberately contains no company-specific repositories, knowledge, credentials, issue-tracker conventions, or service integrations. Configure those at deployment time.

## What it provides

- FastAPI health and run-planning API
- A human-gated workflow: analyse → evaluate → implement → test → review → draft PR
- Typed repository contracts with edit-path allowlists
- Provider interfaces for an LLM agent, source control, test runner, and knowledge store
- Optional Deep Agents runtime with AWS Bedrock and isolated per-run workspaces
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

## Deep Agents with Bedrock

The starter includes an optional Deep Agents runtime. It stages only the
repository's `allowed_edit_paths` from `SANDBOX_SOURCE_ROOT/<repository-id>`
into a fresh workspace under `SANDBOX_WORK_ROOT`. Secret-like files, VCS
metadata, virtual environments, dependency folders, and build output are
excluded.

`POST /v1/deep-agent/runs` defaults to `"execute": false`, which validates the
repository contract and creates the isolated workspace without contacting AWS.
Set `"execute": true` only after configuring AWS credentials outside this
repository. The runtime uses the standard AWS credential provider chain and
the `DEEP_AGENT_MODEL_ID` / `AWS_REGION` environment variables.

Deep Agents requires approval interrupts for file writes, edits, and deletes.
Branch creation, pushing, and draft-PR creation are intentionally not exposed
as tools in this starter; add them through an approved source-control adapter.

## Integration points

Implement the protocols in `src/code_agent_boilerplate/providers.py` for your own:

- LLM/agent runtime
- GitHub, GitLab, or other source-control provider
- sandbox and test runner
- documentation or knowledge retrieval system
- Slack, Teams, web UI, or issue-tracker intake

Keep credentials in your secret manager and supply them through environment variables. Do not commit them to this repository.
