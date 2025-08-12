#!/usr/bin/env python3
"""
Test to see what the AI agent is actually outputting.
"""

import asyncio
import csv
from pathlib import Path

from pydantic_ai import Agent

from vep_ai_validation_tools.agents.base import create_ollama_model
from vep_ai_validation_tools.models import AddressParsingResult
from vep_ai_validation_tools.renaming.renaming import FieldManager


async def test_agent_output():
    """Test what the AI agent is outputting"""

    # Create RenameModel
    fields = FieldManager()
    RenameModel = fields.create_rename_model_safe()

    # Read one record from Texas file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-ai-validation-tools/examples/sample_data.csv"
    )

    # Create a simple test record
    test_record = {
        "mail_address1": "129 OAKLAND",
        "mail_city": "PALESTINE",
        "mail_state": "TX",
        "mail_zip5": "75801",
    }

    print("🧪 TESTING AI AGENT OUTPUT")
    print("=" * 50)

    print(f"\n📋 TEST DATA:")
    for key, value in test_record.items():
        print(f"   {key}: {value}")

    # Create a simple agent with a basic prompt
    ollama_model = create_ollama_model()

    simple_agent = Agent(
        ollama_model,
        output_type=AddressParsingResult,
        system_prompt="""
You are an address parser. You will receive address fields and must parse them into the correct structure.

For each field, create a ParsedAddressField with:
- field_name: the original field name
- address_type: "mailing" or "residence"
- component: "address1", "city", "state", "zip5", etc.
- field_value: the actual value
- confidence: a number between 0.0 and 1.0

Return an AddressParsingResult with:
- mailing_fields: list of ParsedAddressField for mailing addresses
- residence_fields: list of ParsedAddressField for residence addresses
- parsing_errors: empty list
- total_fields_processed: number of fields processed
- successfully_parsed: number of fields successfully parsed
""",
    )

    # Test the agent
    input_text = f"""
Parse these address fields:
{test_record}
"""

    print(f"\n🤖 TESTING AGENT WITH INPUT:")
    print(input_text)

    try:
        result = await simple_agent.run(input_text)
        print(f"\n✅ AGENT SUCCESS!")
        print(f"Output: {result.output}")
        print(f"Mailing fields: {len(result.output.mailing_fields)}")
        print(f"Residence fields: {len(result.output.residence_fields)}")
    except Exception as e:
        print(f"\n❌ AGENT FAILED: {e}")
        print(f"Error type: {type(e)}")


if __name__ == "__main__":
    asyncio.run(test_agent_output())
