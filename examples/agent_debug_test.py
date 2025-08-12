#!/usr/bin/env python3
"""
Debug test for individual agents to see what's failing.
"""

import asyncio

from pydantic_ai import Agent

from vep_ai_validation_tools.agents.base import create_ollama_model
from vep_ai_validation_tools.models import AddressParsingResult


async def test_simple_agent():
    """Test a simple agent to see if the basic setup works"""

    print("🔧 Testing basic Ollama model...")

    try:
        # Create a simple agent without complex output validation
        model = create_ollama_model()
        print("✅ Model created successfully")

        # Test with just string output first
        simple_agent = Agent(
            model, system_prompt="You are a helpful assistant. Respond briefly."
        )

        print("🚀 Testing simple agent...")
        result = await simple_agent.run("Say hello")
        print(f"✅ Simple agent result: {result.output}")

    except Exception as e:
        print(f"❌ Simple agent failed: {e}")
        import traceback

        traceback.print_exc()
        return

    print("\n🧪 Testing structured output agent...")

    try:
        # Test with structured output
        structured_agent = Agent(
            model,
            output_type=AddressParsingResult,
            system_prompt="""You are an address parser. Return a JSON object with this structure:
{
  "mailing_fields": [],
  "residence_fields": [],
  "parsing_errors": [],
  "total_fields_processed": 0,
  "successfully_parsed": 0
}""",
        )

        test_input = "Parse this address data: {'mail_address1': '123 Main St', 'mail_city': 'Austin'}"

        print(f"🚀 Testing structured agent with: {test_input}")
        result = await structured_agent.run(test_input)
        print(f"✅ Structured agent result: {result.output}")

    except Exception as e:
        print(f"❌ Structured agent failed: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Main debug function"""
    print("Agent Debug Test")
    print("=" * 40)

    await test_simple_agent()

    print("\n🎉 Debug test completed!")


if __name__ == "__main__":
    asyncio.run(main())
