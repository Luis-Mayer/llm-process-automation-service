# Runbook

This runbook provides operational guidance for running and maintaining the LLM Process Automation Service.

## Starting the Service

1. Ensure dependencies are installed:
   ```
   uv sync
   ```

2. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o-mini
   LOG_LEVEL=INFO
   ```

3. Start the service:
   ```
   uv run uvicorn app.main:app --reload
   ```

### Docker mode (optional)

- Build the Docker image:
  ```
  docker build -t llm-process-automation-service .
  ```
- Run containerized app (use .env for secrets):
  ```
  docker run --rm -p 8000:8000 --env-file .env llm-process-automation-service
  ```

4. Verify it's running:
   - API: http://127.0.0.1:8000
   - Health check: http://127.0.0.1:8000/health
   - Docs: http://127.0.0.1:8000/docs

## Testing

Run tests with:
```
uv run pytest
```

## Common Issues

- **Missing OpenAI API Key**: Ensure `OPENAI_API_KEY` is set in `.env`.
- **Model not found**: Check `OPENAI_MODEL` is a valid model (e.g., gpt-4o-mini).
- **Port already in use**: Change the port with `--port 8001` in uvicorn command.
- **Import errors**: Run `uv sync` to install missing packages.

## Finding Logs

- Application logs: `logs/app.log`
- Console output: Check terminal where uvicorn is running
- Artifacts: `artifacts/` directory for request/response pairs