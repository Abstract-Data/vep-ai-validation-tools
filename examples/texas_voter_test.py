#!/usr/bin/env python3
"""
Simple test script for processing Texas voter file.

This script uses csv.DictReader to read the Texas voter file and
processes a few records using the new modular architecture.
"""

import asyncio
import csv
from pathlib import Path

from tqdm import tqdm

from vep_ai_validation_tools import process_voter_file_with_persistence
from vep_ai_validation_tools.renaming.renaming import FieldManager, FieldReferenceInfo

fields = FieldManager()
RenameModel = fields.create_rename_model_safe()


def read_records(file: Path):
    with open(file, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # test_row = next(reader)
        # rest_result = test_agent.run_sync(f"Identify all address keys and values in {test_row} and ouput a dictionary of the values assigned to the correct key that is in {FIELD_DEFINITIONS_TOML}")
        # print(rest_result.output)
        for row in tqdm(reader):
            row["file_origin"] = Path(file).name
            yield row


texas_csv = Path(
    "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
)
record_generator = read_records(texas_csv)
records = []
for idx, row in enumerate(record_generator):
    if idx >= 10:
        break
    records.append(RenameModel(**row).model_dump())


async def process_records(records):
    results = await process_voter_file_with_persistence(records)
    return results


results = asyncio.run(process_records(records))
print(results[0])

# async def test_texas_voter_file():
#     """Test processing the Texas voter file"""

#     # Path to the Texas voter file
#     texas_csv = Path("/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv")


#     if not texas_csv.exists():
#         print(f"❌ Texas voter file not found at: {texas_csv}")
#         print("Please check the file path and try again.")
#         return

#     print(f"🚀 Processing Texas voter file: {texas_csv}")
#     record_generator = read_records(texas_csv)

#     # Read CSV using DictReader
#     records = []
#     try:
#         # Read first 10 records for testing
#         print("📖 Reading first 10 records...")
#         for i, row in enumerate(record_generator):
#             if i >= 10:  # Limit to first 10 records for testing
#                 break
#             records.append(row)

#             # Show first record structure
#             if i == 0:
#                 print(f"📋 First record has {len(row)} fields:")
#                 for key in list(row.keys())[:10]:  # Show first 10 field names
#                     print(f"   - {key}: {row[key]}")
#                 if len(row) > 10:
#                     print(f"   ... and {len(row) - 10} more fields")

#     except UnicodeDecodeError:
#         print("🔄 UTF-8 failed, trying with latin-1 encoding...")

#         # Read first 10 records for testing
#         for i, row in enumerate(record_generator):
#             if i >= 10:
#                 break
#             records.append(row)

#             if i == 0:
#                 print(f"📋 First record has {len(row)} fields:")
#                 for key in list(row.keys())[:10]:
#                     print(f"   - {key}: {row[key]}")
#                 if len(row) > 10:
#                     print(f"   ... and {len(row) - 10} more fields")
#     print(records[0])
#     records = [RenameModel(**row) for row in records]
#     print(records[0])
#     print(f"📝 Successfully read {len(records)} records")

#     if not records:
#         print("❌ No records found in the file")
#         return

#     # Process the records
#     print("\n🔄 Processing records through the validation pipeline...")
#     results = await process_voter_file_with_persistence(records)

#     print(f"\n✅ Processing complete! Processed {len(results)} records")

#     # Summary statistics
#     successful = [r for r in results if not r.needs_review]
#     needs_review = [r for r in results if r.needs_review]

#     print(f"\n📊 Results Summary:")
#     print(f"   ✅ Successful: {len(successful)}")
#     print(f"   ⚠️  Need Review: {len(needs_review)}")

#     # Show details of first few results
#     print(f"\n📋 Sample Results:")
#     for i, result in enumerate(results[:3]):
#         print(f"\n   Record {i+1} ({result.record_id}):")
#         print(f"      Overall Confidence: {result.overall_confidence:.2f}")
#         print(f"      Processing Errors: {len(result.processing_errors)}")
#         print(f"      Needs Review: {result.needs_review}")

#         if result.name:
#             print(f"      Parsed Name: {result.name.first_name} {result.name.last_name}")

#         if result.primary_address:
#             addr = result.primary_address.normalized_address
#             print(f"      Primary Address: {addr[:50]}{'...' if len(addr) > 50 else ''}")

#         print(f"      Districts Found: {len(result.districts)}")
#         print(f"      Elections Found: {len(result.elections)}")

#         if result.processing_errors:
#             print(f"      Errors: {result.processing_errors[:2]}")  # First 2 errors


# async def main():
#     """Main function"""
#     print("Texas Voter File Test")
#     print("=" * 50)

#     await test_texas_voter_file()

#     print("\n🎉 Test completed!")


# if __name__ == "__main__":
#     asyncio.run(main())
