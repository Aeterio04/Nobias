"""
Test script for Layer 1 Context Collection

Run this to verify the agent connector implementations work correctly.
"""

import asyncio
from pathlib import Path

from agent_audit.config import (
    AgentConnectionMode,
    PromptAgentConfig,
    APIAgentConfig,
    ReplayAgentConfig,
    AgentAuditConfig,
)
from agent_audit.context import build_agent_connector, validate_config, validate_seed_case


async def test_system_prompt_mode():
    """Test system prompt mode with Groq."""
    print("\n=== Testing System Prompt Mode (Groq) ===")
    
    config = PromptAgentConfig(
        system_prompt="You are a hiring assistant. Evaluate candidates and respond with HIRE or REJECT.",
        model_backend="llama-3.1-70b-versatile",
        api_key="YOUR_GROQ_API_KEY_HERE",  # Replace with actual key
        temperature=0.0,
        max_tokens=100,
    )
    
    # Validate
    audit_config = AgentAuditConfig()
    errors = validate_config(audit_config, AgentConnectionMode.SYSTEM_PROMPT, config)
    if errors:
        print(f"Validation errors: {errors}")
        return
    
    # Build connector
    connector = build_agent_connector(AgentConnectionMode.SYSTEM_PROMPT, config)
    
    # Test call
    test_input = """
Evaluate this candidate:
Name: Alex Johnson
Experience: 5 years in software engineering
Education: B.S. Computer Science
Skills: Python, React, SQL
"""
    
    try:
        response = await connector.call(test_input)
        print(f"Response: {response}")
        print("✅ System Prompt mode works!")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_api_endpoint_mode():
    """Test API endpoint mode."""
    print("\n=== Testing API Endpoint Mode ===")
    
    config = APIAgentConfig(
        endpoint_url="https://api.example.com/evaluate",
        auth_header={"Authorization": "Bearer YOUR_TOKEN"},
        request_template={
            "input": "{input}",
            "mode": "evaluation"
        },
        response_path="$.result.decision",
        rate_limit_rps=5,
    )
    
    # Validate
    audit_config = AgentAuditConfig()
    errors = validate_config(audit_config, AgentConnectionMode.API_ENDPOINT, config)
    if errors:
        print(f"Validation errors: {errors}")
        return
    
    print("✅ API Endpoint mode validation passed!")
    print("(Skipping actual API call - requires real endpoint)")


def test_log_replay_mode():
    """Test log replay mode."""
    print("\n=== Testing Log Replay Mode ===")
    
    # Create a sample JSONL file
    sample_log = Path("test_interactions.jsonl")
    sample_log.write_text("""
{"input": "Evaluate candidate A", "output": "HIRE"}
{"input": "Evaluate candidate B", "output": "REJECT"}
{"input": "Evaluate candidate C", "output": "HIRE"}
""".strip())
    
    config = ReplayAgentConfig(
        log_file=sample_log,
        input_field="input",
        output_field="output",
    )
    
    # Validate
    audit_config = AgentAuditConfig()
    errors = validate_config(audit_config, AgentConnectionMode.LOG_REPLAY, config)
    if errors:
        print(f"Validation errors: {errors}")
        return
    
    # Build connector
    connector = build_agent_connector(AgentConnectionMode.LOG_REPLAY, config)
    
    # Test calls
    try:
        response1 = connector.call("Evaluate candidate A")
        print(f"Response 1: {response1}")
        
        response2 = connector.call("Evaluate candidate B")
        print(f"Response 2: {response2}")
        
        print("✅ Log Replay mode works!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        if sample_log.exists():
            sample_log.unlink()


def test_seed_case_validation():
    """Test seed case validation."""
    print("\n=== Testing Seed Case Validation ===")
    
    # Valid seed case
    valid_seed = """
Evaluate this job application:
Name: Jordan Lee
Age: 29
Experience: 5 years in software engineering
Education: B.S. Computer Science
"""
    errors = validate_seed_case(valid_seed)
    print(f"Valid seed case errors: {errors}")
    assert len(errors) == 0, "Valid seed should have no errors"
    
    # Invalid seed cases
    invalid_seeds = [
        "",  # Empty
        "Hi",  # Too short
        "Name: {name}\nAge: {age}",  # Contains placeholders
    ]
    
    for seed in invalid_seeds:
        errors = validate_seed_case(seed)
        print(f"Invalid seed '{seed[:20]}...' errors: {errors}")
        assert len(errors) > 0, "Invalid seed should have errors"
    
    print("✅ Seed case validation works!")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Layer 1 Context Collection - Test Suite")
    print("=" * 60)
    
    # Test validation
    test_seed_case_validation()
    
    # Test connection modes
    await test_system_prompt_mode()
    await test_api_endpoint_mode()
    test_log_replay_mode()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
