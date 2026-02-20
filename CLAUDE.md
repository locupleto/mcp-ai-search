# CLAUDE.md

This file provides guidance to Claude Code when working with the xAI Grok + Perplexity MCP Server.

## Server Overview

This MCP server provides four tools for querying external AI services:

1. **ask_grok**: Query xAI's Grok models (2M token context, reasoning capabilities)
2. **ask_perplexity**: Real-time web search with source citations
3. **generate_image_grok**: Text-to-image generation with Grok-2-Image (Aurora)
4. **search_x**: Search X (Twitter) posts via xAI's server-side X Search

## When to Use These Tools

### Use `ask_grok` when:
- User needs general LLM inference beyond Claude's capabilities
- Task requires very large context (>200K tokens, up to 2M)
- User explicitly requests xAI Grok
- Need alternative LLM perspective or comparison
- Code generation tasks where Grok's strengths apply

**Example user requests:**
- "Use Grok to analyze this large document..."
- "Ask Grok what it thinks about..."
- "Compare your answer with Grok's..."

### Use `ask_perplexity` when:
- User needs **current/real-time information** (news, events, weather, stock prices)
- Task requires **web search with citations**
- User explicitly requests web search or Perplexity
- Need to fact-check with recent sources
- Research tasks requiring current data

**Example user requests:**
- "What's the latest news about...?"
- "Search the web for information on..."
- "What's the current weather/stock price/..."
- "Use Perplexity to find..."

### Use `search_x` when:
- User needs **current discussions or sentiment from X/Twitter**
- Task requires monitoring **what specific people are posting** on X
- User needs **real-time social media reactions** to events
- Financial market sentiment analysis from X posts
- User explicitly requests X/Twitter search

**Example user requests:**
- "What are people saying on X about...?"
- "Search Twitter for discussions about..."
- "What has @elonmusk posted about...?"
- "What's the sentiment on X about the Fed meeting?"

**Parameters:**
```python
{
  "query": str,                 # Required: Search query
  "model": str,                 # Optional: Default "grok-4-1-fast"
                                # Options: grok-4-1-fast, grok-4-latest, grok-3-latest
  "max_tokens": int,            # Optional: 100-16000, default 4000
  "allowed_x_handles": list,    # Optional: Only these handles (max 10)
  "excluded_x_handles": list,   # Optional: Exclude these handles (max 10)
  "from_date": str,             # Optional: Start date YYYY-MM-DD
  "to_date": str                # Optional: End date YYYY-MM-DD
}
```

**Notes:**
- Uses xAI's `/v1/responses` endpoint with server-side X Search (NOT the chat completions endpoint)
- Same `GROK_API_KEY` as `ask_grok` — no separate X Developer account needed
- Returns inline citations with direct links to X posts
- `grok-4-1-fast` is the default (cheapest, optimized for tool calling)

### DO NOT use these tools when:
- Information is within Claude's knowledge cutoff (January 2025)
- User hasn't requested external AI services
- Task can be completed with available context/files
- Cost/latency considerations outweigh benefits

## Tool Parameters

### ask_grok Parameters

```python
{
  "question": str,              # Required: The question to ask
  "model": str,                 # Optional: Default "grok-4-latest"
                                # Options: grok-4-latest, grok-3-latest,
                                #          grok-4-1-fast-latest, grok-4, grok-3,
                                #          grok-4-1-fast, grok-4-1-fast-reasoning,
                                #          grok-beta
  "temperature": float,         # Optional: 0.0-2.0, default 0.7
  "max_tokens": int,            # Optional: 1-131072, default 1024
  "system_message": str         # Optional: Custom system prompt
}
```

**Model Selection:**
- `grok-4-latest` - **Recommended default** (auto-updates to newest Grok 4)
- `grok-3-latest` - Legacy model (use if user specifies)
- `grok-4-1-fast-latest` - Faster inference, slightly lower quality
- `grok-4-1-fast-reasoning` - Use for math, logic, complex reasoning
- Specific versions (`grok-4`, `grok-3`) - Only if version pinning needed

### ask_perplexity Parameters

```python
{
  "question": str,              # Required: The search question
  "model": str,                 # Optional: Default "sonar"
                                # Options: "sonar" (fast), "sonar-pro" (deep research)
  "temperature": float,         # Optional: 0.0-1.0, default 0.2 (lower=more factual)
  "max_tokens": int,            # Optional: 100-8000, default 4000
  "search_recency_filter": str  # Optional: "month", "week", "day", "hour"
}
```

**Model Selection:**
- `sonar` - **Recommended default** (fast, good for most queries)
- `sonar-pro` - Use when user needs comprehensive research with many citations

**Recency Filter:**
- Use `"day"` or `"hour"` for time-sensitive queries (news, weather, stocks)
- Use `"week"` for recent trends or developments
- Use `"month"` for broader research
- Omit for general timeless knowledge

## Best Practices

### 1. Formatting Responses

When presenting Grok responses to users:
```
**Grok's Response:**

[Grok's answer here...]

**Performance:** 342 tokens in 1.2s
```

When presenting Perplexity responses to users:
```
**Answer:**

[Perplexity's answer here...]

**Sources:**
1. [Source 1](url1)
2. [Source 2](url2)
```

### 2. Error Handling

Both tools return error messages as text content (not exceptions):
- Check for "Error:" in response text
- Report errors clearly to user
- Suggest fixes (API key check, model name, etc.)

### 3. Cost Optimization

These are paid API services - be judicious:
- Don't use for simple questions Claude can answer
- Set appropriate `max_tokens` (don't over-request)
- Use `grok-4-1-fast-latest` for speed-critical tasks
- Use `sonar` instead of `sonar-pro` unless deep research needed

### 4. Combining Tools

Example: Research task + analysis
```
1. Use ask_perplexity to gather current information with citations
2. Use ask_grok to analyze/synthesize the findings
3. Present combined insights to user
```

## Implementation Details

### File Structure
```
/Volumes/Work/development/projects/git/mcp-ai-search/
├── ai_search_mcp_server.py    # Main server (stdio MCP protocol)
├── test_server.py             # Test suite
├── requirements.txt           # Dependencies: mcp, openai, requests
└── venv/                      # Virtual environment
```

### Environment Variables
- `GROK_API_KEY` - xAI API key (from ~/.zshrc)
- `PERPLEXITY_API_KEY` - Perplexity API key (from ~/.zshrc)

### API Implementation
- **xAI Grok**: Uses OpenAI-compatible API (`base_url="https://api.x.ai/v1"`)
- **xAI X Search**: Direct REST API (`https://api.x.ai/v1/responses`) with `x_search` tool type
- **Perplexity**: Direct REST API (`https://api.perplexity.ai/chat/completions`)

## Troubleshooting

### Server not available
1. Check `.mcp.json` in trading-lab project
2. Verify environment variables are set
3. Restart Claude Code

### API errors
- **401 Unauthorized**: API key invalid/missing
- **429 Rate Limit**: Too many requests, wait and retry
- **400 Bad Request**: Invalid parameters (check model name, max_tokens)

### Testing
Run test suite to validate:
```bash
cd /Volumes/Work/development/projects/git/mcp-ai-search
source venv/bin/activate
python test_server.py
```

## Examples

### Example 1: Current News Research
```
User: "What are the latest developments in AI regulation?"

Claude: I'll use Perplexity to search for current information.

[Calls ask_perplexity({
  "question": "Latest developments in AI regulation 2026",
  "model": "sonar-pro",
  "search_recency_filter": "week"
})]

[Presents answer with citations to user]
```

### Example 2: Large Context Analysis
```
User: "Analyze this 500-page document... [large paste]"

Claude: This document is quite large. I'll use Grok which supports up to 2M tokens.

[Calls ask_grok({
  "question": "Analyze this document and summarize key points: [document]",
  "model": "grok-4-latest",
  "max_tokens": 2000
})]

[Presents analysis to user]
```

### Example 3: Reasoning Task
```
User: "Solve this complex logic puzzle..."

Claude: This requires step-by-step reasoning. I'll use Grok's reasoning model.

[Calls ask_grok({
  "question": "Solve this logic puzzle with detailed reasoning: [puzzle]",
  "model": "grok-4-1-fast-reasoning",
  "temperature": 0.0,
  "max_tokens": 1000
})]

[Presents solution to user]
```

### Example 4: X/Twitter Search
```
User: "What are people saying on X about the latest Fed rate decision?"

Claude: I'll search X for current discussions on this topic.

[Calls search_x({
  "query": "Fed rate decision latest reaction",
  "max_tokens": 2000
})]

[Presents X posts and sentiment analysis with links to source posts]
```

### Example 5: Filtered X Search
```
User: "What has Elon Musk posted about AI this week?"

Claude: I'll search X filtered to Elon Musk's account.

[Calls search_x({
  "query": "AI artificial intelligence",
  "allowed_x_handles": ["elonmusk"],
  "from_date": "2026-02-13",
  "to_date": "2026-02-20"
})]

[Presents filtered results with links to specific posts]
```

## Maintenance

### Updating Dependencies
```bash
cd /Volumes/Work/development/projects/git/mcp-ai-search
source venv/bin/activate
pip install --upgrade mcp openai requests
```

### Adding New Models
When xAI or Perplexity release new models:
1. Update `inputSchema.properties.model.enum` in `ai_search_mcp_server.py`
2. Update documentation in `README.md`
3. Add test cases in `test_server.py`
4. Test thoroughly before deploying

### Monitoring Usage
- Check xAI Console for API usage and costs
- Check Perplexity Settings for API usage and limits
- Monitor server logs for errors or rate limits

## Security Notes

- **API Keys**: Stored in environment variables only (never in code/git)
- **User Data**: Not logged or persisted by this server
- **Rate Limiting**: Implement client-side rate limiting if needed
- **Error Messages**: Don't expose API keys in error responses

## Related Documentation

- [Main README](README.md) - Installation and usage
- [Test Suite](test_server.py) - Validation and examples
- [xAI Docs](https://docs.x.ai/api) - Official API documentation
- [Perplexity Docs](https://docs.perplexity.ai/) - Official API documentation
