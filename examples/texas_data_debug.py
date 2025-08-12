#!/usr/bin/env python3
"""
Debug test with actual Texas voter data to see what's failing.
"""

import asyncio
import csv
from pathlib import Path

from vep_ai_validation_tools.agents import parse_address_fields


async def test_with_texas_data():
    """Test agents with actual Texas voter data"""

    # Path to the Texas voter file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
    )

    if not texas_csv.exists():
        print(f"❌ Texas voter file not found")
        return

    print(f"🚀 Testing with real Texas voter data")

    # Read first record
    try:
        with open(texas_csv, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            record = next(reader)
    except UnicodeDecodeError:
        with open(texas_csv, encoding="latin-1") as csvfile:
            reader = csv.DictReader(csvfile)
            record = next(reader)

    print(f"📋 Sample record fields:")
    for key, value in list(record.items())[:15]:  # Show first 15 fields
        print(f"   {key}: {value}")
    print(f"   ... and {len(record) - 15} more fields")

    # Test address parsing with this data
    print(f"\n🏠 Testing address parsing...")

    try:
        # Enable debug output
        result = await parse_address_fields(record)

        print(f"✅ Address parsing completed!")
        print(f"   Total fields processed: {result.total_fields_processed}")
        print(f"   Successfully parsed: {result.successfully_parsed}")
        print(f"   Mailing fields found: {len(result.mailing_fields)}")
        print(f"   Residence fields found: {len(result.residence_fields)}")
        print(f"   Parsing errors: {len(result.parsing_errors)}")

        if result.parsing_errors:
            print(f"   Error details: {result.parsing_errors[:3]}")

        if result.mailing_fields:
            print(f"   Sample mailing field: {result.mailing_fields[0]}")

        if result.residence_fields:
            print(f"   Sample residence field: {result.residence_fields[0]}")

    except Exception as e:
        print(f"❌ Address parsing failed: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Main debug function"""
    print("Texas Data Debug Test")
    print("=" * 50)

    await test_with_texas_data()

    print("\n🎉 Texas data debug completed!")


if __name__ == "__main__":
    asyncio.run(main())
