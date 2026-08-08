#!/usr/bin/env python3
"""
MCP Server for xAI Grok and Perplexity AI Search

This server provides tools to:
- xAI Grok (ask_grok): LLM inference with 2M token context and reasoning capabilities
- xAI Grok Image (generate_image_grok): Text-to-image generation with Aurora model
- xAI X Search (search_x): Search X (Twitter) posts via xAI's server-side X Search
- Perplexity AI (ask_perplexity): Real-time web search with citations

Environment Variables Required:
- GROK_API_KEY: xAI API key (xai-...) — used for ask_grok, generate_image_grok, and search_x
- PERPLEXITY_API_KEY: Perplexity API key (pplx-...)
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult, ListToolsResult
from openai import OpenAI
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai-search-mcp")

# Environment variables
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")


def validate_api_keys():
    """Validate that required API keys are set in environment variables"""
    errors = []

    if not GROK_API_KEY:
        errors.append("GROK_API_KEY environment variable not set")

    if not PERPLEXITY_API_KEY:
        errors.append("PERPLEXITY_API_KEY environment variable not set")

    if errors:
        error_msg = "Missing required API keys:\n" + "\n".join(f"  - {e}" for e in errors)
        error_msg += "\n\nPlease set these in your ~/.zshrc file and reload your shell."
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info("✅ API keys validated successfully")


async def handle_ask_grok(arguments: dict) -> Sequence[TextContent]:
    """
    Handle xAI Grok queries

    Args:
        arguments: Dictionary containing:
            - question (str): The question to ask
            - model (str): Grok model to use (default: grok-4-latest)
            - temperature (float): Sampling temperature 0.0-2.0 (default: 0.7)
            - max_tokens (int): Maximum tokens to generate (default: 1024)
            - system_message (str): Optional system message

    Returns:
        List of TextContent with formatted response
    """
    question = arguments.get("question")
    if not question:
        return [TextContent(type="text", text="Error: 'question' parameter is required")]

    model = arguments.get("model", "grok-4-latest")
    temperature = arguments.get("temperature", 0.7)
    max_tokens = arguments.get("max_tokens", 1024)
    system_message = arguments.get("system_message", "You are a helpful assistant.")

    logger.info(f"🤖 Grok query: model={model}, question={question[:50]}...")

    try:
        # xAI uses OpenAI-compatible API
        client = OpenAI(
            api_key=GROK_API_KEY,
            base_url="https://api.x.ai/v1"
        )

        start_time = time.time()

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question}
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        response_time = int((time.time() - start_time) * 1000)
        answer = chat_completion.choices[0].message.content
        tokens = chat_completion.usage.completion_tokens
        model_used = chat_completion.model

        result = f"""Question: {question}
Model: {model}
Temperature: {temperature}

Answer:
{answer}

---
Tokens: {tokens} | Time: {response_time}ms | Model: {model_used}"""

        logger.info(f"✅ Grok response: {tokens} tokens in {response_time}ms")
        return [TextContent(type="text", text=result)]

    except Exception as e:
        error_msg = f"xAI Grok API Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_ask_perplexity(arguments: dict) -> Sequence[TextContent]:
    """
    Handle Perplexity AI search queries

    Args:
        arguments: Dictionary containing:
            - question (str): The search question
            - model (str): Perplexity model (sonar or sonar-pro, default: sonar)
            - temperature (float): Sampling temperature 0.0-1.0 (default: 0.2)
            - max_tokens (int): Maximum tokens to generate (default: 4000)
            - search_recency_filter (str): Optional recency filter (month, week, day, hour)

    Returns:
        List of TextContent with formatted response including citations
    """
    question = arguments.get("question")
    if not question:
        return [TextContent(type="text", text="Error: 'question' parameter is required")]

    model = arguments.get("model", "sonar")
    temperature = arguments.get("temperature", 0.2)
    max_tokens = arguments.get("max_tokens", 4000)
    search_recency_filter = arguments.get("search_recency_filter")

    logger.info(f"🔍 Perplexity query: model={model}, question={question[:50]}...")

    try:
        url = "https://api.perplexity.ai/chat/completions"
        current_date = datetime.now().strftime("%Y-%m-%d")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": f"Be precise and concise. Include relevant citations. Today's date is {current_date}."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if search_recency_filter:
            payload["search_recency_filter"] = search_recency_filter

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        content = data['choices'][0]['message']['content']
        citations = data.get('citations', [])
        model_used = data.get('model', model)

        # Format citations
        sources_text = ""
        if citations:
            sources_text = "\n\nSources:\n"
            for idx, url in enumerate(citations, 1):
                sources_text += f"{idx}. {url}\n"

        recency_text = f" | Recency: {search_recency_filter}" if search_recency_filter else ""

        result = f"""Question: {question}
Model: {model}{recency_text}

Answer:
{content}{sources_text}

---
Citations: {len(citations)} | Model: {model_used} | Timestamp: {datetime.now().isoformat()}"""

        logger.info(f"✅ Perplexity response: {len(citations)} citations")
        return [TextContent(type="text", text=result)]

    except requests.exceptions.HTTPError as e:
        error_msg = f"Perplexity API HTTP Error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"Perplexity API Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_generate_image_grok(arguments: dict) -> Sequence[TextContent]:
    """
    Handle xAI Grok image generation

    Args:
        arguments: Dictionary containing:
            - prompt (str): Text description of the image to generate
            - n (int): Number of images to generate (1-10, default: 1)
            - response_format (str): 'url' or 'b64_json' (default: 'url')

    Returns:
        List of TextContent with image URL(s) or base64 data
    """
    prompt = arguments.get("prompt")
    if not prompt:
        return [TextContent(type="text", text="Error: 'prompt' parameter is required")]

    n = arguments.get("n", 1)
    response_format = arguments.get("response_format", "url")

    # Validate parameters
    if n < 1 or n > 10:
        return [TextContent(type="text", text="Error: 'n' must be between 1 and 10")]
    if response_format not in ["url", "b64_json"]:
        return [TextContent(type="text", text="Error: 'response_format' must be 'url' or 'b64_json'")]

    logger.info(f"🎨 Grok image generation: n={n}, prompt={prompt[:50]}...")

    try:
        url = "https://api.x.ai/v1/images/generations"

        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "n": n,
            "response_format": response_format
        }

        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_time = int((time.time() - start_time) * 1000)

        data = response.json()

        # Extract image data
        images = data.get("data", [])
        revised_prompt = images[0].get("revised_prompt", "") if images else ""

        # Format response
        if response_format == "url":
            image_urls = [img.get("url", "") for img in images]
            images_text = "\n".join(f"{i+1}. {url}" for i, url in enumerate(image_urls))
            result = f"""Prompt: {prompt}
Images Generated: {len(images)}

Image URLs:
{images_text}

---
Revised Prompt: {revised_prompt}
Time: {response_time}ms | Model: grok-imagine-image"""
        else:
            # For b64_json, just indicate success and provide metadata
            result = f"""Prompt: {prompt}
Images Generated: {len(images)}
Format: base64 JSON

[Base64 image data returned - {len(images)} image(s)]

---
Revised Prompt: {revised_prompt}
Time: {response_time}ms | Model: grok-imagine-image"""

        logger.info(f"✅ Grok image generation: {len(images)} images in {response_time}ms")
        return [TextContent(type="text", text=result)]

    except requests.exceptions.HTTPError as e:
        error_msg = f"xAI Image API HTTP Error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"xAI Image API Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def handle_search_x(arguments: dict) -> Sequence[TextContent]:
    """
    Handle X (Twitter) search queries via xAI's Responses API with server-side X Search.

    Args:
        arguments: Dictionary containing:
            - query (str): What to search for on X
            - model (str): Grok model for analysis (default: grok-4-1-fast)
            - max_tokens (int): Maximum response tokens (default: 4000)
            - allowed_x_handles (list[str]): Limit to these X accounts (max 10)
            - excluded_x_handles (list[str]): Exclude these X accounts (max 10)
            - from_date (str): Start date YYYY-MM-DD
            - to_date (str): End date YYYY-MM-DD

    Returns:
        List of TextContent with formatted response including X post citations
    """
    query = arguments.get("query")
    if not query:
        return [TextContent(type="text", text="Error: 'query' parameter is required")]

    model = arguments.get("model", "grok-4-1-fast")
    max_tokens = arguments.get("max_tokens", 4000)
    allowed_x_handles = arguments.get("allowed_x_handles")
    excluded_x_handles = arguments.get("excluded_x_handles")
    from_date = arguments.get("from_date")
    to_date = arguments.get("to_date")

    logger.info(f"🐦 X Search query: model={model}, query={query[:50]}...")

    try:
        # Build x_search tool config
        x_search_tool = {"type": "x_search"}

        # Add optional filters only if provided
        if allowed_x_handles:
            x_search_tool["x_handles"] = allowed_x_handles
        if excluded_x_handles:
            x_search_tool["excluded_x_handles"] = excluded_x_handles
        if from_date:
            x_search_tool["from_date"] = from_date
        if to_date:
            x_search_tool["to_date"] = to_date

        url = "https://api.x.ai/v1/responses"
        payload = {
            "model": model,
            "input": query,
            "tools": [x_search_tool],
            "inline_citations": True,
            # xAI /v1/responses requires max_output_tokens; max_tokens is
            # chat-completions-only and is rejected (returns 0 results).
            "max_output_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        response_time = int((time.time() - start_time) * 1000)

        data = response.json()

        # Extract text content from response output items
        content_parts = []
        citations = []
        model_used = data.get("model", model)

        for item in data.get("output", []):
            if item.get("type") == "message":
                for content_block in item.get("content", []):
                    if content_block.get("type") == "output_text":
                        text = content_block.get("text", "")
                        content_parts.append(text)
                        # Extract citations from annotations
                        for annotation in content_block.get("annotations", []):
                            if annotation.get("type") == "url_citation":
                                cite_url = annotation.get("url", "")
                                cite_title = annotation.get("title", "")
                                if cite_url and cite_url not in [c["url"] for c in citations]:
                                    citations.append({"url": cite_url, "title": cite_title})

        content = "\n".join(content_parts) if content_parts else "No results returned from X Search."

        # Build filter description
        filters = []
        if allowed_x_handles:
            filters.append(f"From: @{', @'.join(allowed_x_handles)}")
        if excluded_x_handles:
            filters.append(f"Excluding: @{', @'.join(excluded_x_handles)}")
        if from_date:
            filters.append(f"From: {from_date}")
        if to_date:
            filters.append(f"To: {to_date}")
        filter_text = f" | Filters: {'; '.join(filters)}" if filters else ""

        # Format X post sources
        sources_text = ""
        if citations:
            sources_text = "\n\nX Post Sources:\n"
            for idx, cite in enumerate(citations, 1):
                title_text = f" - {cite['title']}" if cite['title'] else ""
                sources_text += f"{idx}. {cite['url']}{title_text}\n"

        result = f"""Query: {query}
Model: {model}{filter_text}

Results:
{content}{sources_text}

---
Citations: {len(citations)} | Time: {response_time}ms | Model: {model_used} | Timestamp: {datetime.now().isoformat()}"""

        logger.info(f"✅ X Search response: {len(citations)} citations in {response_time}ms")
        return [TextContent(type="text", text=result)]

    except requests.exceptions.HTTPError as e:
        error_msg = f"xAI X Search API HTTP Error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    except requests.exceptions.Timeout:
        error_msg = "xAI X Search API Error: Request timed out after 60 seconds"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"xAI X Search API Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]


async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="ask_grok",
            description="""Query xAI's Grok models with 2M token context and reasoning capabilities.

Use this tool when you need:
- General LLM inference and question answering
- Code generation or debugging
- Complex reasoning tasks
- Large context analysis (up to 2M tokens)

Available models: grok-4-latest, grok-3-latest, grok-4-1-fast-latest, grok-4, grok-3, grok-4-1-fast, grok-4-1-fast-reasoning, grok-beta

The -latest aliases automatically use the newest version of each model.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or prompt to send to xAI Grok"
                    },
                    "model": {
                        "type": "string",
                        "default": "grok-4-latest",
                        "enum": [
                            "grok-4-latest",
                            "grok-3-latest",
                            "grok-4-1-fast-latest",
                            "grok-4",
                            "grok-3",
                            "grok-4-1-fast",
                            "grok-4-1-fast-reasoning",
                            "grok-beta"
                        ],
                        "description": "xAI Grok model to use (-latest aliases auto-update)"
                    },
                    "temperature": {
                        "type": "number",
                        "default": 0.7,
                        "minimum": 0.0,
                        "maximum": 2.0,
                        "description": "Sampling temperature (0=deterministic, 2=creative)"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 1024,
                        "minimum": 1,
                        "maximum": 131072,
                        "description": "Maximum tokens to generate (Grok supports up to 131K)"
                    },
                    "system_message": {
                        "type": "string",
                        "description": "Optional system message to set context"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="ask_perplexity",
            description="""Query Perplexity's real-time web search with citations.

Use this tool when you need:
- Up-to-date information from the web
- Current news and events
- Research with source citations
- Fact-checking with references

Available models:
- sonar: Fast search with Llama 3.3 70B backend
- sonar-pro: Deep research with 2x more citations

Optional recency filters: month, week, day, hour""",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The search question to send to Perplexity"
                    },
                    "model": {
                        "type": "string",
                        "default": "sonar",
                        "enum": ["sonar", "sonar-pro"],
                        "description": "Perplexity model: 'sonar' (fast) or 'sonar-pro' (deep research, 2x citations)"
                    },
                    "temperature": {
                        "type": "number",
                        "default": 0.2,
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Sampling temperature (lower=more factual)"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 4000,
                        "minimum": 100,
                        "maximum": 8000,
                        "description": "Maximum tokens to generate"
                    },
                    "search_recency_filter": {
                        "type": "string",
                        "enum": ["month", "week", "day", "hour"],
                        "description": "Optional: Filter search results by recency"
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="generate_image_grok",
            description="""Generate images using xAI's Grok Imagine model (Aurora).

Use this tool when you need:
- Text-to-image generation
- Photorealistic images from text descriptions
- Images with accurate text rendering, logos, or portraits
- Creative visual content generation

The model excels at:
- Photorealistic rendering
- Precise text instructions
- Real-world entities, logos, text in images
- Human portraits

Pricing: ~$0.02/image""",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate"
                    },
                    "n": {
                        "type": "integer",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Number of images to generate (1-10)"
                    },
                    "response_format": {
                        "type": "string",
                        "default": "url",
                        "enum": ["url", "b64_json"],
                        "description": "Output format: 'url' for hosted URL, 'b64_json' for base64 data"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="search_x",
            description="""Search X (Twitter) for real-time posts, discussions, and trends.

Use this tool when you need:
- Current discussions and opinions on X/Twitter
- Real-time social media sentiment on topics
- What specific X users are posting about
- Breaking news and trending discussions on X
- Financial market sentiment from X posts

Uses xAI's server-side X Search — searches actual X posts and returns
results with direct links to source posts.

Note: Uses the same xAI API key as ask_grok.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to search for on X (Twitter)"
                    },
                    "model": {
                        "type": "string",
                        "default": "grok-4-1-fast",
                        "enum": [
                            "grok-4-1-fast",
                            "grok-4-latest",
                            "grok-3-latest"
                        ],
                        "description": "Grok model for analyzing X search results (default: grok-4-1-fast, cheapest and optimized for tool calling)"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 4000,
                        "minimum": 100,
                        "maximum": 16000,
                        "description": "Maximum tokens to generate in the response"
                    },
                    "allowed_x_handles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 10,
                        "description": "Only search posts from these X handles (max 10, without @ prefix)"
                    },
                    "excluded_x_handles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 10,
                        "description": "Exclude posts from these X handles (max 10, without @ prefix)"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date for search range (YYYY-MM-DD format)"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date for search range (YYYY-MM-DD format)"
                    }
                },
                "required": ["query"]
            }
        )
    ]


async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls"""
    if name == "ask_grok":
        return await handle_ask_grok(arguments)
    elif name == "ask_perplexity":
        return await handle_ask_perplexity(arguments)
    elif name == "generate_image_grok":
        return await handle_generate_image_grok(arguments)
    elif name == "search_x":
        return await handle_search_x(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# --- MCP SDK 2.x adapters ----------------------------------------------------
# list_tools()/call_tool() above keep their v1 signatures so tests and scripts
# can import and call them directly. These thin adapters bridge them to the
# SDK 2.x handler contract (ctx/params in, *Result models out) and restore v1
# error semantics: any exception from the legacy handler becomes
# CallToolResult(is_error=True, text=str(e)) — readable by the model — instead
# of an opaque JSON-RPC internal error.

async def _on_list_tools(ctx, params) -> ListToolsResult:
    return ListToolsResult(tools=await list_tools())


async def _on_call_tool(ctx, params) -> CallToolResult:
    try:
        content = await call_tool(params.name, params.arguments or {})
        return CallToolResult(content=list(content), is_error=False)
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=str(e))],
            is_error=True,
        )


server = Server(
    "ai-search",
    version="1.0.0",
    on_list_tools=_on_list_tools,
    on_call_tool=_on_call_tool,
)


async def main():
    """Main entry point for the MCP server"""
    logger.info("🚀 Starting xAI Grok + Perplexity MCP Server...")

    try:
        # Validate API keys before starting
        validate_api_keys()

        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✅ MCP Server ready and listening on stdio")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
