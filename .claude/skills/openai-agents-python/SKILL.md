---
name: openai-agents-python
description: Fetch up-to-date OpenAI Agents Python SDK documentation using Context7. Use this skill when users ask about openai agents, openai agents sdk, openai agents python, building multi-agent workflows, agent handoffs, guardrails, sessions, or tracing with the OpenAI Agents framework. Triggers on keywords like "openai agents", "openai agents python", "openai agents sdk" "agents sdk", "multi-agent", "handoffs", "guardrails" in the context of OpenAI/Python development.
---

# OpenAI Agents Python

Token-efficient documentation fetcher for OpenAI Agents Python SDK.

## Quick Start

**ALWAYS use the fetch-docs.sh script:**

```bash
# By topic (recommended)
bash scripts/fetch-docs.sh --topic agents
bash scripts/fetch-docs.sh --topic handoffs --verbose

# Custom query
bash scripts/fetch-docs.sh "How to create an agent with custom tools"
```

**Result:** Returns filtered documentation with ~77% token savings.

## Workflow

For any OpenAI Agents Python question:

### Step 1: Identify Topic

Match user query to a topic:

| User Question | Topic |
|---------------|-------|
| "How do I create an agent?" | `agents` |
| "How do handoffs work?" | `handoffs` |
| "How to add safety constraints?" | `guardrails` |
| "How to debug my agent?" | `tracing` |
| "How to use tools with agents?" | `tools` |
| "Getting started" | `quickstart` |

### Step 2: Fetch Documentation

```bash
bash scripts/fetch-docs.sh --topic <topic> --verbose
```

### Step 3: Provide Answer

Use the filtered output to answer the user's question with code examples.

## Available Topics

| Topic | Description |
|-------|-------------|
| `agents` | How to create and configure agents |
| `handoffs` | How to implement handoffs between agents |
| `guardrails` | How to add guardrails and safety constraints |
| `sessions` | How to manage sessions and conversation state |
| `tracing` | How to enable and use tracing for debugging |
| `tools` | How to define and use tools with agents |
| `streaming` | How to implement streaming responses |
| `context` | How to manage context and memory |
| `quickstart` | Getting started guide |
| `examples` | Code examples |
| `runner` | How to use the Runner class |
| `lifecycle` | Agent lifecycle and execution flow |

## Parameters

```bash
bash scripts/fetch-docs.sh [OPTIONS] [QUERY]
```

**Options:**
- `--topic TOPIC` - Use predefined topic (see table above)
- `--mode code|info` - code for examples (default), info for concepts
- `--verbose, -v` - Show token statistics
- `--list-topics` - List all available topics
- `--help, -h` - Show help

## Examples

### Basic Agent Creation

```bash
bash scripts/fetch-docs.sh --topic agents --verbose
```

### Multi-Agent Handoffs

```bash
bash scripts/fetch-docs.sh --topic handoffs
```

### Custom Query

```bash
bash scripts/fetch-docs.sh "How to create a triage agent that routes to specialists"
```

### Conceptual Overview

```bash
bash scripts/fetch-docs.sh --topic lifecycle --mode info
```

## How It Works

The script automatically handles the MCP server lifecycle:
1. **Starts** Context7 MCP server via `npx -y @upstash/context7-mcp`
2. **Fetches** documentation using JSON-RPC over stdio
3. **Filters** content using shell tools (awk/grep/sed) - 0 LLM tokens for filtering!
4. **Stops** the server automatically when done

## Token Efficiency

The script achieves ~50-77% token savings by:
1. Fetching full documentation (stays in shell subprocess)
2. Filtering with awk/grep/sed (0 LLM tokens used for filtering!)
3. Returning only code examples + API signatures + key notes

**Do NOT use MCP tools directly** - always use the script for optimal token usage.

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `fetch-docs.sh` | **Main script - ALWAYS USE THIS** |
| `mcp-client.py` | Universal MCP client (used internally) |
| `extract-code-blocks.sh` | Code example filter |
| `extract-python-signatures.sh` | Python API signature filter |
| `extract-notes.sh` | Important notes filter |
