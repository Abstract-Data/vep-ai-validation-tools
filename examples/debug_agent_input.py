#!/usr/bin/env python3
"""
Debug script to see what data the agents are receiving.
"""

import asyncio
import csv
from pathlib import Path

from vep_ai_validation_tools.agents import (
    parse_address_fields,
    parse_district_fields,
    parse_election_fields,
)
from vep_ai_validation_tools.renaming.renaming import FieldManager


async def debug_agent_input():
    """Debug what data the agents are receiving"""

    # Create RenameModel
    fields = FieldManager()
    RenameModel = fields.create_rename_model_safe()

    # Read one record from Texas file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
    )

    with open(texas_csv, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_record = next(reader)
        raw_record["file_origin"] = texas_csv.name

    # Transform the record
    transformed_record = RenameModel(**raw_record).model_dump()

    print("🔍 DEBUGGING AGENT INPUT")
    print("=" * 50)

    print("\n📋 RAW RECORD (first 10 fields):")
    for i, (key, value) in enumerate(raw_record.items()):
        if i >= 10:
            break
        print(f"   {key}: {value}")

    print("\n🔄 TRANSFORMED RECORD (first 10 fields):")
    for i, (key, value) in enumerate(transformed_record.items()):
        if i >= 10:
            break
        print(f"   {key}: {value}")

    # Check for address fields
    print("\n🏠 ADDRESS FIELDS FOUND:")
    address_fields = {}
    address_patterns = [
        "mail_",
        "residence_",
        "MAILING",
        "RESIDENTIAL",
        "ADDRESS",
        "MAILINGCITY",
        "MLCITY",
        "RCITY",
        "RZIP",
        "MZIP",
        "RA_",
        "MA_",
        "MLADD",
        "MADR",
        "STRNAM",
        "HOUSENUMBER",
    ]

    for field_name, value in transformed_record.items():
        if value and any(pattern in field_name.upper() for pattern in address_patterns):
            address_fields[field_name] = value

    if address_fields:
        for field_name, value in address_fields.items():
            print(f"   {field_name}: {value}")
    else:
        print("   ❌ No address fields found!")

    # Try to parse addresses
    print("\n🧪 TESTING ADDRESS PARSING:")
    try:
        address_result = await parse_address_fields(transformed_record)
        print(f"   ✅ Address parsing successful!")
        print(f"   Mailing fields: {len(address_result.mailing_fields)}")
        print(f"   Residence fields: {len(address_result.residence_fields)}")
        print(f"   Total processed: {address_result.total_fields_processed}")
    except Exception as e:
        print(f"   ❌ Address parsing failed: {e}")

    # Check for district fields
    print("\n🗺️ DISTRICT FIELDS FOUND:")
    district_fields = {}
    district_patterns = [
        "district_",
        "DISTRICT",
        "CONGRESS",
        "SENATE",
        "HOUSE",
        "WARD",
        "PRECINCT",
    ]

    for field_name, value in transformed_record.items():
        if value and any(
            pattern in field_name.upper() for pattern in district_patterns
        ):
            district_fields[field_name] = value

    if district_fields:
        for field_name, value in district_fields.items():
            print(f"   {field_name}: {value}")
    else:
        print("   ❌ No district fields found!")

    # Try to parse districts
    print("\n🧪 TESTING DISTRICT PARSING:")
    try:
        district_result = await parse_district_fields(transformed_record)
        print(f"   ✅ District parsing successful!")
        print(f"   Districts found: {len(district_result.districts)}")
    except Exception as e:
        print(f"   ❌ District parsing failed: {e}")


if __name__ == "__main__":
    asyncio.run(debug_agent_input())
