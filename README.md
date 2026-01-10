# xAI Grok + Perplexity MCP Server

Model Context Protocol (MCP) server providing tools to query **xAI Grok** and **Perplexity AI** services.

## Features

### 🤖 xAI Grok (`ask_grok`)
- **2M token context window** - Analyze large documents and codebases
- **Reasoning capabilities** - Advanced models with enhanced reasoning
- **Multiple models** - Choose from grok-4, grok-3, grok-4-1-fast, and more
- **Auto-updating aliases** - Use `-latest` suffixes for newest versions

### 🔍 Perplexity AI (`ask_perplexity`)
- **Real-time web search** - Get current information from the internet
- **Source citations** - Every answer includes URLs to sources
- **Recency filters** - Filter by hour, day, week, or month
- **Two models** - sonar (fast) or sonar-pro (deep research, 2x citations)

## Installation

### 1. Clone or Create Repository

```bash
cd /Volumes/Work/development/projects/git/
git clone <repo-url> mcp-ai-search
# OR if creating new:
mkdir mcp-ai-search && cd mcp-ai-search
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Add to `~/.zshrc`:

```bash
# xAI Grok API (get from https://console.x.ai/)
export GROK_API_KEY="xai-..."

# Perplexity API (get from https://www.perplexity.ai/settings/api)
export PERPLEXITY_API_KEY="pplx-..."
```

Reload your shell:

```bash
source ~/.zshrc
```

### 5. Register with Claude Code

Add to `/Volumes/Work/development/projects/git/trading-lab/.mcp.json`:

```json
{
  "mcpServers": {
    "ai-search": {
      "type": "stdio",
      "command": "/Volumes/Work/development/projects/git/mcp-ai-search/venv/bin/python3",
      "args": ["/Volumes/Work/development/projects/git/mcp-ai-search/ai_search_mcp_server.py"],
      "env": {
        "GROK_API_KEY": "${GROK_API_KEY}",
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    }
  }
}
```

Restart Claude Code to register the new MCP server.

## Usage

### Tool 1: `ask_grok`

Query xAI's Grok models for LLM inference, code generation, and reasoning tasks.

**Parameters:**
- `question` (string, required): The question or prompt to send to Grok
- `model` (string, optional): Model to use (default: `grok-4-latest`)
  - `grok-4-latest` - Latest Grok 4 (recommended)
  - `grok-3-latest` - Latest Grok 3
  - `grok-4-1-fast-latest` - Latest Grok 4.1 Fast
  - `grok-4` - Specific Grok 4 version
  - `grok-3` - Specific Grok 3 version
  - `grok-4-1-fast` - Fast inference variant
  - `grok-4-1-fast-reasoning` - Enhanced reasoning variant
  - `grok-beta` - Beta model
- `temperature` (number, optional): 0.0-2.0 (default: 0.7)
- `max_tokens` (integer, optional): 1-131072 (default: 1024)
- `system_message` (string, optional): System prompt for context

**Example (via Claude Code):**

```
User: "Use ask_grok to explain quantum computing in simple terms"

Claude calls: ask_grok({
  "question": "Explain quantum computing in simple terms",
  "model": "grok-4-latest",
  "temperature": 0.7,
  "max_tokens": 500
})
```

**Response Format:**
```
Question: Explain quantum computing in simple terms
Model: grok-4-latest
Temperature: 0.7

Answer:
[Grok's response here...]

---
Tokens: 342 | Time: 1240ms | Model: grok-4-2025-01-01
```

### Tool 2: `ask_perplexity`

Query Perplexity for real-time web search with source citations.

**Parameters:**
- `question` (string, required): The search question
- `model` (string, optional): Model to use (default: `sonar`)
  - `sonar` - Fast search with Llama 3.3 70B
  - `sonar-pro` - Deep research with 2x more citations
- `temperature` (number, optional): 0.0-1.0 (default: 0.2)
- `max_tokens` (integer, optional): 100-8000 (default: 4000)
- `search_recency_filter` (string, optional): Filter results by recency
  - `month` - Results from past month
  - `week` - Results from past week
  - `day` - Results from past day
  - `hour` - Results from past hour

**Example (via Claude Code):**

```
User: "Use ask_perplexity to find the latest news about AI regulation"

Claude calls: ask_perplexity({
  "question": "What are the latest developments in AI regulation?",
  "model": "sonar-pro",
  "search_recency_filter": "week"
})
```

**Response Format:**
```
Question: What are the latest developments in AI regulation?
Model: sonar-pro | Recency: week

Answer:
[Perplexity's answer with current information...]

Sources:
1. https://www.example.com/article1
2. https://www.example.com/article2
3. https://www.example.com/article3

---
Citations: 3 | Model: sonar-pro | Timestamp: 2026-01-02T14:30:45.123456
```

## Testing

Run the test suite to validate the MCP server:

```bash
cd /Volumes/Work/development/projects/git/mcp-ai-search
source venv/bin/activate
python test_server.py
```

The test suite includes:
- ✅ API key validation
- ✅ Basic Grok queries
- ✅ Grok reasoning models
- ✅ Basic Perplexity searches
- ✅ Perplexity with recency filters
- ✅ Error handling
- ✅ Custom system messages

## Telegram Bot Integration

The Telegram bot can use these tools via Claude Code integration:

**Example conversation:**
```
User: "What's the weather forecast for tomorrow?"

Bot (via Claude):
  1. Calls ask_perplexity({
       "question": "Weather forecast for San Francisco tomorrow",
       "search_recency_filter": "day"
     })
  2. Receives answer with source citations
  3. Responds to user with current, cited information
```

## Architecture

```
mcp-ai-search/
├── ai_search_mcp_server.py    # Main MCP server implementation
├── test_server.py             # Test suite
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── CLAUDE.md                  # Claude-specific guidance
├── .gitignore                 # Git ignore patterns
└── venv/                      # Virtual environment
```

## API Keys

### xAI Grok API Key
1. Visit [xAI Console](https://console.x.ai/)
2. Sign in or create an account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key (starts with `xai-...`)

### Perplexity API Key
1. Visit [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Sign in or create an account
3. Generate a new API key
4. Copy the key (starts with `pplx-...`)

## Troubleshooting

### "API key not set" error
- Ensure environment variables are set in `~/.zshrc`
- Reload your shell: `source ~/.zshrc`
- Verify: `echo $GROK_API_KEY && echo $PERPLEXITY_API_KEY`

### "Module not found" error
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### MCP server not appearing in Claude Code
- Check `.mcp.json` syntax (valid JSON)
- Verify file paths are absolute (not relative)
- Restart Claude Code after modifying `.mcp.json`

### Grok API errors
- Check API key is valid (not expired/revoked)
- Verify model name is correct (use `-latest` aliases)
- Check token limits (max_tokens <= 131072)

### Perplexity API errors
- Check API key is valid
- Verify model name (`sonar` or `sonar-pro`)
- Check recency filter values (month/week/day/hour)

## Performance

### xAI Grok
- **Latency**: 1-3 seconds (varies by model and max_tokens)
- **Context window**: Up to 2M tokens
- **Rate limits**: Check xAI console for current limits

### Perplexity
- **Latency**: 2-5 seconds (includes web search time)
- **sonar**: Faster responses, good for quick facts
- **sonar-pro**: Slower but more comprehensive, better citations
- **Rate limits**: Check Perplexity settings for current limits

## License

This MCP server follows the same license as the trading-lab project.

## References

- [xAI API Documentation](https://docs.x.ai/api)
- [Perplexity API Documentation](https://docs.perplexity.ai/)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Claude Code Documentation](https://claude.com/claude-code)
