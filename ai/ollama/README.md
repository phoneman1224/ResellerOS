# Ollama Configuration

ResellerOS expects a local Ollama service running at `http://127.0.0.1:11434` with a model like `mistral` or `llama3`. Use the following commands to prepare the environment:

```bash
ollama pull mistral
ollama serve
```

Update `AI_MODEL` in the environment if you wish to use a different model. All AI requests gracefully fall back to heuristics when the service is offline.
