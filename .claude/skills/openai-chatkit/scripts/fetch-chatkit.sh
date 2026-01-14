#!/bin/bash
# OpenAI ChatKit Documentation Fetcher
# Token-efficient fetcher using Context7 MCP with shell pipeline filtering
#
# Usage:
#   bash scripts/fetch-chatkit.sh --sdk js --topic "getting started"
#   bash scripts/fetch-chatkit.sh --sdk python --topic "server setup"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ChatKit Library IDs
declare -A CHATKIT_LIBS=(
  ["js"]="/openai/chatkit-js"
  ["javascript"]="/openai/chatkit-js"
  ["react"]="/openai/chatkit-js"
  ["next.js"]="/openai/chatkit-js"
  ["python"]="/openai/chatkit-python"
  ["py"]="/openai/chatkit-python"
  ["samples"]="/openai/openai-chatkit-advanced-samples"
  ["examples"]="/openai/openai-chatkit-advanced-samples"
  ["js-docs"]="/websites/openai_github_io_chatkit-js"
  ["python-docs"]="/websites/openai_github_io_chatkit-python"
)

# Defaults
SDK="js"
TOPIC=""
MODE="code"
VERBOSE=0

usage() {
  cat << USAGE
Usage: $0 [OPTIONS]

OpenAI ChatKit documentation fetcher with token-efficient filtering.

OPTIONS:
  --sdk SDK           SDK to fetch docs for: js, python, samples (default: js)
  --topic TOPIC       Topic to focus on (e.g., "theming", "tools", "streaming")
  --mode MODE         Mode: code (default) or info
  --verbose, -v       Show token statistics
  --help, -h          Show this help

AVAILABLE SDKs:
  js, javascript, react  - ChatKit JavaScript/React SDK
  python, py             - ChatKit Python SDK
  samples, examples      - Advanced full-stack samples
  js-docs                - Comprehensive JS documentation
  python-docs            - Comprehensive Python documentation

EXAMPLES:
  # Get JavaScript getting started
  $0 --sdk js --topic "getting started"

  # Get Python server setup
  $0 --sdk python --topic "server setup" --verbose

  # Get theming examples
  $0 --sdk js --topic "theming customization"

  # Get full-stack samples
  $0 --sdk samples --topic "fastapi vite"
USAGE
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --sdk)
      SDK="$2"
      shift 2
      ;;
    --topic)
      TOPIC="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      ;;
  esac
done

# Resolve library ID
LIBRARY_ID="${CHATKIT_LIBS[$SDK]:-}"
if [ -z "$LIBRARY_ID" ]; then
  echo "Error: Unknown SDK '$SDK'. Available: js, python, samples, js-docs, python-docs" >&2
  exit 1
fi

[ $VERBOSE -eq 1 ] && echo "📚 Fetching ChatKit $SDK documentation..." >&2
[ $VERBOSE -eq 1 ] && echo "   Library: $LIBRARY_ID" >&2
[ $VERBOSE -eq 1 ] && echo "   Topic: ${TOPIC:-all}" >&2

# Build query parameters
QUERY="${TOPIC:-chatkit getting started}"

# Build parameters JSON
PARAMS=$(cat <<JSON
{
  "libraryId": "$LIBRARY_ID",
  "query": "$QUERY"
}
JSON
)

# Call MCP server via mcp-client.py (response stays in subprocess!)
RAW_JSON=$(python3 "$SCRIPT_DIR/mcp-client.py" call \
  -s "npx -y @upstash/context7-mcp" \
  -t query-docs \
  -p "$PARAMS" 2>/dev/null)

# Extract text from JSON
if command -v jq &> /dev/null; then
  RAW_TEXT=$(echo "$RAW_JSON" | jq -r '.content[0].text // empty')
else
  RAW_TEXT=$(echo "$RAW_JSON" | python3 -c 'import sys, json; data=json.load(sys.stdin); print(data.get("content", [{}])[0].get("text", ""))')
fi

if [ -z "$RAW_TEXT" ]; then
  echo "Error: No documentation received from Context7" >&2
  exit 1
fi

# Calculate raw token count
if [ $VERBOSE -eq 1 ]; then
  RAW_WORDS=$(echo "$RAW_TEXT" | wc -w)
  RAW_TOKENS=$(echo "$RAW_WORDS * 1.3" | bc | cut -d. -f1)
  echo "📊 Raw response: ~$RAW_WORDS words (~$RAW_TOKENS tokens)" >&2
fi

# Filter using shell tools (0 LLM tokens!)
OUTPUT=""

if [ "$MODE" = "code" ]; then
  # Code mode: Extract code examples and API signatures
  CODE_BLOCKS=$(echo "$RAW_TEXT" | "$SCRIPT_DIR/extract-code-blocks.sh" 5)

  if [ -n "$CODE_BLOCKS" ] && [ "$CODE_BLOCKS" != "# No code blocks found" ]; then
    OUTPUT+="## Code Examples\n\n$CODE_BLOCKS\n"
  fi

  SIGNATURES=$(echo "$RAW_TEXT" | "$SCRIPT_DIR/extract-signatures.sh" 3)

  if [ -n "$SIGNATURES" ]; then
    OUTPUT+="\n## API Signatures\n\n$SIGNATURES\n"
  fi
else
  # Info mode: Extract conceptual content
  CODE_BLOCKS=$(echo "$RAW_TEXT" | "$SCRIPT_DIR/extract-code-blocks.sh" 2)

  if [ -n "$CODE_BLOCKS" ] && [ "$CODE_BLOCKS" != "# No code blocks found" ]; then
    OUTPUT+="## Examples\n\n$CODE_BLOCKS\n"
  fi

  OVERVIEW=$(echo "$RAW_TEXT" | \
    awk 'BEGIN{RS=""; FS="\n"} length($0) > 200 && !/```/{print; if(++count>=3) exit}')

  if [ -n "$OVERVIEW" ]; then
    OUTPUT+="\n## Overview\n\n$OVERVIEW\n"
  fi
fi

# Always add important notes
NOTES=$(echo "$RAW_TEXT" | "$SCRIPT_DIR/extract-notes.sh" 3)

if [ -n "$NOTES" ]; then
  OUTPUT+="\n## Important Notes\n\n$NOTES\n"
fi

# Fallback if no content extracted
if [ -z "$OUTPUT" ]; then
  OUTPUT=$(echo "$RAW_TEXT" | head -c 1000)
  OUTPUT+="\n\n[Response truncated for brevity...]"
fi

# Output filtered content
echo -e "$OUTPUT"

# Calculate savings
if [ $VERBOSE -eq 1 ]; then
  FILTERED_WORDS=$(echo -e "$OUTPUT" | wc -w)
  FILTERED_TOKENS=$(echo "$FILTERED_WORDS * 1.3" | bc | cut -d. -f1)
  SAVINGS=$(echo "scale=1; (($RAW_TOKENS - $FILTERED_TOKENS) / $RAW_TOKENS) * 100" | bc)

  echo "" >&2
  echo "✨ Filtered output: ~$FILTERED_WORDS words (~$FILTERED_TOKENS tokens)" >&2
  echo "💰 Token savings: ${SAVINGS}%" >&2
fi
