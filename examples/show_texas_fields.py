#!/usr/bin/env python3
"""
Script to show all fields in the Texas voter records.
"""

import asyncio
import csv
from pathlib import Path

from vep_ai_validation_tools.renaming.renaming import FieldManager


def show_texas_fields():
    """Show all fields in the Texas voter records"""

    # Create RenameModel
    fields = FieldManager()
    RenameModel = fields.create_rename_model_safe()

    # Read Texas file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
    )

    print("🔍 ANALYZING TEXAS VOTER RECORD FIELDS")
    print("=" * 60)

    # Read first few records to see all possible fields
    all_fields = set()
    sample_records = []

    with open(texas_csv, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 5:  # Look at first 5 records
                break
            all_fields.update(row.keys())
            sample_records.append(row)

    print(f"\n📋 TOTAL UNIQUE FIELDS FOUND: {len(all_fields)}")
    print("\n" + "=" * 60)

    # Show all fields alphabetically
    print("\n📝 ALL FIELDS (ALPHABETICAL):")
    for field in sorted(all_fields):
        print(f"   {field}")

    print("\n" + "=" * 60)

    # Show sample data for first record
    if sample_records:
        print(f"\n📊 SAMPLE RECORD DATA (First Record):")
        first_record = sample_records[0]
        for field in sorted(first_record.keys()):
            value = first_record[field]
            if value:  # Only show non-empty values
                print(f"   {field}: {value}")

    print("\n" + "=" * 60)

    # Show field categories
    print(f"\n🏷️  FIELD CATEGORIES:")

    # Address fields
    address_fields = [
        f
        for f in all_fields
        if any(
            pattern in f.upper()
            for pattern in ["ADDRESS", "CITY", "STATE", "ZIP", "MAIL", "RESIDENCE"]
        )
    ]
    print(f"\n🏠 ADDRESS FIELDS ({len(address_fields)}):")
    for field in sorted(address_fields):
        print(f"   {field}")

    # District fields
    district_fields = [
        f
        for f in all_fields
        if any(
            pattern in f.upper()
            for pattern in [
                "DISTRICT",
                "CONGRESS",
                "SENATE",
                "HOUSE",
                "WARD",
                "PRECINCT",
            ]
        )
    ]
    print(f"\n🗺️  DISTRICT FIELDS ({len(district_fields)}):")
    for field in sorted(district_fields):
        print(f"   {field}")

    # Name fields
    name_fields = [
        f
        for f in all_fields
        if any(
            pattern in f.upper()
            for pattern in ["NAME", "FIRST", "LAST", "MIDDLE", "FORMER"]
        )
    ]
    print(f"\n👤 NAME FIELDS ({len(name_fields)}):")
    for field in sorted(name_fields):
        print(f"   {field}")

    # Voter fields
    voter_fields = [
        f
        for f in all_fields
        if any(
            pattern in f.upper()
            for pattern in ["VOTER", "REGISTRATION", "VUID", "COUNTY", "PCT"]
        )
    ]
    print(f"\n🗳️  VOTER FIELDS ({len(voter_fields)}):")
    for field in sorted(voter_fields):
        print(f"   {field}")

    # Election fields
    election_fields = [
        f
        for f in all_fields
        if any(pattern in f.upper() for pattern in ["GEN", "PRI", "ELECTION", "VOTE"])
    ]
    print(f"\n📊 ELECTION FIELDS ({len(election_fields)}):")
    for field in sorted(election_fields):
        print(f"   {field}")

    # Other fields
    other_fields = [
        f
        for f in all_fields
        if not any(
            pattern in f.upper()
            for pattern in [
                "ADDRESS",
                "CITY",
                "STATE",
                "ZIP",
                "MAIL",
                "RESIDENCE",
                "DISTRICT",
                "CONGRESS",
                "SENATE",
                "HOUSE",
                "WARD",
                "PRECINCT",
                "NAME",
                "FIRST",
                "LAST",
                "MIDDLE",
                "FORMER",
                "VOTER",
                "REGISTRATION",
                "VUID",
                "COUNTY",
                "PCT",
                "GEN",
                "PRI",
                "ELECTION",
                "VOTE",
            ]
        )
    ]
    print(f"\n🔧 OTHER FIELDS ({len(other_fields)}):")
    for field in sorted(other_fields):
        print(f"   {field}")

    print("\n" + "=" * 60)

    # Show transformed record structure
    print(f"\n🔄 TRANSFORMED RECORD STRUCTURE:")
    if sample_records:
        first_record = sample_records[0]
        first_record["file_origin"] = texas_csv.name

        try:
            transformed = RenameModel(**first_record)
            print(f"✅ Transformation successful!")
            print(f"   Model type: {type(transformed)}")
            print(
                f"   Total fields in transformed model: {len(transformed.model_dump())}"
            )

            # Show structured fields
            print(f"\n📊 STRUCTURED FIELDS:")
            print(f"   districts: {len(transformed.districts)} items")
            print(f"   voter_registration: {len(transformed.voter_registration)} items")
            print(
                f"   person_name: {len(transformed.person_name) if transformed.person_name else 0} items"
            )
            print(
                f"   data_source: {len(transformed.data_source) if transformed.data_source else 0} items"
            )

            # Show some sample transformed fields
            print(f"\n📋 SAMPLE TRANSFORMED FIELDS (first 10):")
            transformed_dict = transformed.model_dump()
            for i, (key, value) in enumerate(transformed_dict.items()):
                if i >= 10:
                    break
                print(f"   {key}: {value}")

        except Exception as e:
            print(f"❌ Transformation failed: {e}")


if __name__ == "__main__":
    show_texas_fields()
