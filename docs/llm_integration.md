# Local LLM Integration Guide

This guide explains how to use the local LLM (Large Language Model) integration in mdiss for generating tickets using models running locally via Ollama.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Configuration](#advanced-configuration)
- [Available Models](#available-models)
- [Troubleshooting](#troubleshooting)

## Prerequisites

1. Python 3.9 or higher
2. [Ollama](https://ollama.ai/) installed and running
3. At least one model downloaded (e.g., Mistral 7B)

## Installation

1. Install mdiss with AI support:
   ```bash
   pip install mdiss[ai] ollama
   ```

2. Pull a model (e.g., Mistral 7B):
   ```bash
   ollama pull mistral:7b
   ```

3. Start the Ollama server (if not already running):
   ```bash
   make llm-serve
   ```

## Basic Usage

### Using the AITicketGenerator

```python
from mdiss.ai.ticket_generator import AITicketGenerator

# Initialize with default model (mistral:7b)
generator = AITicketGenerator()

# Generate a ticket
ticket = generator.generate_ticket(
    title="Fix login issues",
    description="Users cannot log in on mobile devices"
)
print(ticket)
```

### Using Makefile Commands

| Command | Description |
|---------|-------------|
| `make llm-serve` | Start Ollama server if not running |
| `make llm-pull` | Download Mistral 7B model |
| `make llm-list` | List available Ollama models |
| `make llm-test` | Test LLM integration |

## Advanced Configuration

### Environment Variables

```bash
# Set Ollama base URL (default: http://localhost:11434)
export OLLAMA_BASE_URL="http://localhost:11434"

# Set default model (default: mistral:7b)
export DEFAULT_LLM_MODEL="mistral:7b"

# Set timeout for API calls in seconds (default: 300)
export OLLAMA_TIMEOUT=300
```

### Custom Model Configuration

```python
from mdiss.ai.ticket_generator import AITicketGenerator

# Initialize with custom model and parameters
generator = AITicketGenerator(
    model="llama2",
    temperature=0.7,
    max_tokens=2000,
    top_p=0.9,
    timeout=300
)
```

## Available Models

You can use any model supported by Ollama. Some recommended models:

- `mistral:7b` - Fast and capable general-purpose model (default)
- `llama2` - Meta's LLaMA 2 model
- `codellama` - Code-specific model based on LLaMA
- `mixtral` - High-quality Mixture of Experts model

List all available models:
```bash
make llm-list
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Ollama server is running: `make llm-serve`
   - Check if the port is available: `lsof -i :11434`

2. **Model Not Found**
   - Download the model first: `ollama pull <model_name>`
   - Check available models: `ollama list`

3. **Slow Performance**
   - Try a smaller model
   - Increase system resources (CPU/RAM)
   - Close other resource-intensive applications

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

If you encounter any issues, please:
1. Check the [Ollama documentation](https://github.com/ollama/ollama)
2. Open an issue on [GitHub](https://github.com/wronai/mdiss/issues)
3. Check the logs in `~/.ollama/logs/`
