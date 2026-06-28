# Lead Qualification

Evaluates incoming B2B leads. Uses GPT-4o to infer intent, budget, and route leads.

## Architecture
- Language: Python 3.11+
- Framework: FastAPI
- LLM: OpenAI GPT-4o
- CRM Integration: HubSpot API
- Automation: Make.com Webhooks

## Setup

Run locally with Docker:
```bash
docker-compose up --build
```

Run tests:
```bash
pytest tests/
```
