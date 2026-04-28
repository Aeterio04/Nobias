"""
Test Google Gemini Connection
==============================

Quick test to verify Gemini API connectivity and basic functionality.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_gemini_basic():
    """Test basic Gemini API call."""
    from agent_audit.interrogation.backends.gemini import GeminiBackend
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        return
    
    print("Testing Google Gemini connection...")
    print(f"API Key: {api_key[:10]}...")
    
    # Create backend
    backend = GeminiBackend(
        api_key=api_key,
        model="gemini-1.5-pro",  # or "gemini-pro"
        temperature=0.0,
        max_tokens=100,
    )
    
    # Test call
    try:
        response = await backend.call("Say 'Hello from Gemini!' and nothing else.")
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_gemini_with_system_prompt():
    """Test Gemini with system prompt."""
    from agent_audit.interrogation.backends.gemini import GeminiBackend
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    print("\nTesting Gemini with system prompt...")
    
    backend = GeminiBackend(
        api_key=api_key,
        model="gemini-1.5-pro",
        system_prompt="You are a helpful hiring assistant. Respond in JSON format.",
        temperature=0.0,
        max_tokens=200,
    )
    
    try:
        response = await backend.call(
            'Evaluate candidate: Name: Alex, Experience: 5 years. '
            'Respond with: {"decision": "hire" or "reject", "reason": "brief reason"}'
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all tests."""
    await test_gemini_basic()
    await test_gemini_with_system_prompt()


if __name__ == "__main__":
    asyncio.run(main())
