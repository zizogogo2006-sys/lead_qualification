# AI Lead Qualification System

Enterprise-grade microservice for evaluating incoming B2B leads. Uses an LLM (GPT-4o) to infer intent, budget, and route leads appropriately.

## Architecture
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-4o
- **CRM Integration**: HubSpot API
- **Automation**: Make.com Webhooks

## Infrastructure
This service is fully containerized and includes a CI/CD pipeline.

### Running Locally with Docker
```bash
docker-compose up --build
```

### Running Tests
We use Pytest for continuous integration.
```bash
pytest tests/
```
