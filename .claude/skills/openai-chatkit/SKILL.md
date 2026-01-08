---
name: openai-chatkit
description: Fetch OpenAI ChatKit documentation for building production-ready chat experiences. Use this skill when users ask about chatbot, chatbots, write chatbot, create chatbot, build chatbot, chatbot code, AI chat, chat application, chat interface, chat UI, conversational AI, ChatKit, ChatKit TypeScript, ChatKit javaScript, or OpenAI ChatKit. Always invoke this skill before writing any chatbot-related code.
---

# OpenAI ChatKit

OpenAI ChatKit is a framework for building high-quality, AI-powered chat experiences with deep UI customization, response streaming, tool integration, and production-ready components.

## Proactive Usage

**This skill MUST be invoked AUTOMATICALLY when the user:**
- Asks to "write a chatbot" or "create a chatbot"
- Mentions "chatbot code" or "chat application"
- Wants to build any AI-powered chat interface
- Asks about chat UI components or conversational AI

**DO NOT** write generic chatbot code without first invoking this skill to get proper ChatKit documentation.

## Quick Start

**Always use the token-efficient shell script:**

```bash
# JavaScript/React SDK
bash scripts/fetch-chatkit.sh --sdk js --topic "getting started"

# Python SDK
bash scripts/fetch-chatkit.sh --sdk python --topic "server setup"

# Full-stack examples
bash scripts/fetch-chatkit.sh --sdk samples --topic "fastapi react"
```

## Standard Workflow

1. **Identify SDK** - JavaScript/React frontend or Python backend
2. **Run fetch script** - Use `fetch-chatkit.sh` with appropriate SDK and topic
3. **Use filtered output** - Script returns token-efficient code examples

## Parameters

```bash
bash scripts/fetch-chatkit.sh [OPTIONS]
```

**Options:**
- `--sdk SDK` - SDK to fetch: js, python, samples (default: js)
- `--topic TOPIC` - Specific topic (e.g., "theming", "tools", "streaming")
- `--mode MODE` - code (default) or info for conceptual explanations
- `--verbose` - Show token savings statistics

**Available SDKs:**
| SDK | Description |
|-----|-------------|
| `js`, `javascript`, `react` | ChatKit JavaScript/React SDK |
| `python`, `py` | ChatKit Python SDK |
| `samples`, `examples` | Advanced full-stack samples |
| `js-docs` | Comprehensive JS documentation |
| `python-docs` | Comprehensive Python documentation |

## Common Queries

| User Request | Command |
|--------------|---------|
| "How to create a chatbot?" | `bash scripts/fetch-chatkit.sh --sdk js --topic "getting started"` |
| "Customize chat theme" | `bash scripts/fetch-chatkit.sh --sdk js --topic "theming customization"` |
| "Add tools to chat" | `bash scripts/fetch-chatkit.sh --sdk js --topic "tools composer"` |
| "Python chat server" | `bash scripts/fetch-chatkit.sh --sdk python --topic "server fastapi"` |
| "Streaming responses" | `bash scripts/fetch-chatkit.sh --sdk js --topic "streaming responses"` |
| "Start screen prompts" | `bash scripts/fetch-chatkit.sh --sdk js --topic "start screen prompts"` |

## Token Efficiency

The script achieves ~77% token savings:
1. Fetches full documentation (stays in shell subprocess)
2. Filters with awk/grep/sed (0 LLM tokens)
3. Returns only code examples + API signatures

**Do NOT use MCP tools directly** - always use `fetch-chatkit.sh` to save tokens.

## Scripts

| Script | Purpose |
|--------|---------|
| `fetch-chatkit.sh` | Main orchestrator - **always use this** |
| `mcp-client.py` | Universal MCP client (foundation) |
| `extract-code-blocks.sh` | Code example filter |
| `extract-signatures.sh` | API signature filter |
| `extract-notes.sh` | Important notes filter |
