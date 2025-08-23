#!/usr/bin/env python3
"""
Test script to verify the renaming agent is working properly.
"""

import asyncio
from pathlib import Path

from vep_ai_validation_tools.renaming.renaming import FieldReferenceInfo, rename_agent


async def test_renaming_agent():
    """Test the renaming agent with a few sample fields"""

    print("🧪 Testing Renaming Agent")
    print("=" * 50)

    test_cases = [
        ("person_name_first", ["FIRST_NAME", "FSTNAM", "FIRSTNAME", "FNAME"]),
        ("voter_vuid", ["VUIDNO", "VUID", "VOTER REG NUMBER", "SOS_VOTERID", "VTRID"]),
        (
            "district_federal_congressional",
            ["NEWCD", "DIST01", "CONGRESSIONAL", "CONGRESSIONAL_DISTRICT"],
        ),
    ]

    for field_name, values in test_cases:
        print(f"\n📋 Testing field: {field_name}")
        print(f"   Values: {values}")

        try:
            result = await rename_agent.run(f"Key: {field_name}, Values: {values}")

            if hasattr(result.output, "field_description"):
                print(f"✅ Success! Description: {result.output.field_description}")
                print(f"   Field name: {result.output.field_name}")
                print(f"   Possible values: {result.output.field_possible_values}")
            else:
                print(f"⚠️  Unexpected output type: {type(result.output)}")
                print(f"   Output: {result.output}")

        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback

            traceback.print_exc()


async def main():
    """Main test function"""
    await test_renaming_agent()
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
