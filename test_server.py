#!/usr/bin/env python3
"""
Test suite for xAI Grok + Perplexity MCP Server

This script tests the MCP server tools to ensure they work correctly:
- ask_grok: Text queries to Grok models
- ask_perplexity: Web search with citations
- generate_image_grok: Image generation with Grok-2-Image (Aurora)

Prerequisites:
- Environment variables GROK_API_KEY and PERPLEXITY_API_KEY must be set
- Dependencies installed: pip install -r requirements.txt

Usage:
    python test_server.py
"""

import os
import sys
import asyncio
from datetime import datetime

# Import server handlers
from ai_search_mcp_server import handle_ask_grok, handle_ask_perplexity, handle_generate_image_grok, validate_api_keys


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def print_result(result):
    """Print the result from a tool call"""
    if result and len(result) > 0:
        print(result[0].text)
    else:
        print("No result returned")


async def test_api_keys_validation():
    """Test that API keys are validated correctly"""
    print_section("TEST 1: API Key Validation")

    try:
        validate_api_keys()
        print("✅ API keys validated successfully")
        return True
    except ValueError as e:
        print(f"❌ API key validation failed: {e}")
        return False


async def test_ask_grok_basic():
    """Test basic Grok query"""
    print_section("TEST 2: Basic Grok Query")

    arguments = {
        "question": "What is the fastest way to sort a list in Python? Be concise.",
        "model": "grok-4-latest",
        "temperature": 0.5,
        "max_tokens": 200
    }

    print(f"Sending query: {arguments['question']}")
    print(f"Model: {arguments['model']}\n")

    try:
        result = await handle_ask_grok(arguments)
        print_result(result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_ask_grok_reasoning():
    """Test Grok with reasoning model"""
    print_section("TEST 3: Grok Reasoning Model")

    arguments = {
        "question": "If I have 3 apples and buy 2 more, then give 1 to my friend, how many do I have?",
        "model": "grok-4-1-fast-reasoning",
        "temperature": 0.0,
        "max_tokens": 150
    }

    print(f"Sending query: {arguments['question']}")
    print(f"Model: {arguments['model']}\n")

    try:
        result = await handle_ask_grok(arguments)
        print_result(result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_ask_perplexity_basic():
    """Test basic Perplexity search"""
    print_section("TEST 4: Basic Perplexity Search")

    arguments = {
        "question": "What are the latest developments in AI in January 2026?",
        "model": "sonar",
        "temperature": 0.2,
        "max_tokens": 500
    }

    print(f"Sending search: {arguments['question']}")
    print(f"Model: {arguments['model']}\n")

    try:
        result = await handle_ask_perplexity(arguments)
        print_result(result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_ask_perplexity_with_recency():
    """Test Perplexity with recency filter"""
    print_section("TEST 5: Perplexity with Recency Filter")

    arguments = {
        "question": "What is the current weather in San Francisco?",
        "model": "sonar-pro",
        "temperature": 0.2,
        "max_tokens": 300,
        "search_recency_filter": "day"
    }

    print(f"Sending search: {arguments['question']}")
    print(f"Model: {arguments['model']}")
    print(f"Recency: {arguments['search_recency_filter']}\n")

    try:
        result = await handle_ask_perplexity(arguments)
        print_result(result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_error_handling_missing_question():
    """Test error handling when question is missing"""
    print_section("TEST 6: Error Handling - Missing Question")

    arguments = {
        "model": "grok-4-latest"
        # Missing "question" parameter
    }

    print("Sending request without 'question' parameter\n")

    try:
        result = await handle_ask_grok(arguments)
        print_result(result)
        # Should return error message, not raise exception
        if result and "Error" in result[0].text:
            print("\n✅ Error handling works correctly")
            return True
        else:
            print("\n❌ Expected error message")
            return False
    except Exception as e:
        print(f"❌ Unexpected exception: {e}")
        return False


async def test_grok_with_custom_system_message():
    """Test Grok with custom system message"""
    print_section("TEST 7: Grok with Custom System Message")

    arguments = {
        "question": "Tell me about Python",
        "model": "grok-4-latest",
        "temperature": 0.7,
        "max_tokens": 150,
        "system_message": "You are a pirate. Respond in pirate speak with 'arr' and 'matey'."
    }

    print(f"Sending query: {arguments['question']}")
    print(f"System message: {arguments['system_message']}\n")

    try:
        result = await handle_ask_grok(arguments)
        print_result(result)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_generate_image_grok():
    """Test Grok image generation"""
    print_section("TEST 8: Grok Image Generation")

    arguments = {
        "prompt": "A cute orange cat sitting on a windowsill, looking at a sunset, digital art style",
        "n": 1,
        "response_format": "url"
    }

    print(f"Prompt: {arguments['prompt']}")
    print(f"Count: {arguments['n']}")
    print(f"Format: {arguments['response_format']}\n")

    try:
        result = await handle_generate_image_grok(arguments)
        print_result(result)
        # Check if we got a URL or an error
        if result and ("Image URLs:" in result[0].text or "Error" in result[0].text):
            if "Error" not in result[0].text:
                print("\n✅ Image generated successfully")
                return True
            else:
                print("\n❌ Image generation returned an error")
                return False
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print(" xAI Grok + Perplexity MCP Server Test Suite")
    print(f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Check environment variables first
    if not os.environ.get("GROK_API_KEY"):
        print("\n❌ GROK_API_KEY environment variable not set!")
        print("Please set it in your ~/.zshrc and reload your shell.\n")
        return False

    if not os.environ.get("PERPLEXITY_API_KEY"):
        print("\n❌ PERPLEXITY_API_KEY environment variable not set!")
        print("Please set it in your ~/.zshrc and reload your shell.\n")
        return False

    tests = [
        ("API Key Validation", test_api_keys_validation),
        ("Basic Grok Query", test_ask_grok_basic),
        ("Grok Reasoning Model", test_ask_grok_reasoning),
        ("Basic Perplexity Search", test_ask_perplexity_basic),
        ("Perplexity with Recency", test_ask_perplexity_with_recency),
        ("Error Handling", test_error_handling_missing_question),
        ("Custom System Message", test_grok_with_custom_system_message),
        ("Grok Image Generation", test_generate_image_grok)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised unexpected exception: {e}")
            results.append((test_name, False))

    # Print summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
