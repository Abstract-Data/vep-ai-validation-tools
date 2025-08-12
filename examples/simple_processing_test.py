#!/usr/bin/env python3
"""
Simple processing test without pydantic_graph to verify core functionality.

This bypasses the complex graph type system and tests the actual AI processing.
"""

import asyncio
import csv
from pathlib import Path

# Import the agents directly
from vep_ai_validation_tools.agents import (
    parse_address_fields,
    parse_district_fields,
    parse_election_fields,
)
from vep_ai_validation_tools.models import CompleteVoterRecord, VoterProcessingState


async def simple_process_record(record: dict, record_id: str) -> CompleteVoterRecord:
    """Process a single record without the graph framework"""

    print(f"🚀 Processing {record_id}")

    # Initialize processing state
    state = VoterProcessingState(raw_record=record, record_id=record_id)

    errors = []
    confidence_scores = {}

    # 1. Parse addresses
    try:
        print("📍 Parsing addresses...")
        address_result = await parse_address_fields(record)

        if address_result.mailing_fields:
            print(
                f"   Found {len(address_result.mailing_fields)} mailing address fields"
            )
            confidence_scores["mailing_address"] = sum(
                f.confidence for f in address_result.mailing_fields
            ) / len(address_result.mailing_fields)

        if address_result.residence_fields:
            print(
                f"   Found {len(address_result.residence_fields)} residence address fields"
            )
            confidence_scores["residence_address"] = sum(
                f.confidence for f in address_result.residence_fields
            ) / len(address_result.residence_fields)

        if address_result.parsing_errors:
            errors.extend(address_result.parsing_errors)

    except Exception as e:
        error_msg = f"Address parsing failed: {str(e)}"
        errors.append(error_msg)
        print(f"   ❌ {error_msg}")

    # 2. Parse districts
    try:
        print("🏛️ Parsing districts...")
        district_result = await parse_district_fields(record)

        if district_result.districts:
            print(f"   Found {len(district_result.districts)} districts")
            confidence_scores["districts"] = sum(
                d.confidence for d in district_result.districts
            ) / len(district_result.districts)

        if district_result.parsing_errors:
            errors.extend(district_result.parsing_errors)

    except Exception as e:
        error_msg = f"District parsing failed: {str(e)}"
        errors.append(error_msg)
        print(f"   ❌ {error_msg}")

    # 3. Parse elections
    try:
        print("🗳️ Parsing elections...")
        election_result = await parse_election_fields(record)

        if election_result.elections:
            print(f"   Found {len(election_result.elections)} elections")
            confidence_scores["elections"] = sum(
                e.confidence for e in election_result.elections
            ) / len(election_result.elections)

        if election_result.parsing_errors:
            errors.extend(election_result.parsing_errors)

    except Exception as e:
        error_msg = f"Election parsing failed: {str(e)}"
        errors.append(error_msg)
        print(f"   ❌ {error_msg}")

    # Calculate overall confidence
    overall_confidence = (
        sum(confidence_scores.values()) / len(confidence_scores)
        if confidence_scores
        else 0.0
    )

    # Determine if needs review
    needs_review = overall_confidence < 0.7 or len(errors) > 0
    review_reasons = []
    if overall_confidence < 0.7:
        review_reasons.append(f"Low confidence: {overall_confidence:.2f}")
    if errors:
        review_reasons.append(f"Processing errors: {len(errors)}")

    # Create final record
    final_record = CompleteVoterRecord(
        record_id=record_id,
        original_record=record,
        confidence_scores=confidence_scores,
        overall_confidence=overall_confidence,
        processing_errors=errors,
        needs_review=needs_review,
        review_reasons=review_reasons,
    )

    print(
        f"✅ Completed {record_id}: confidence={overall_confidence:.2f}, needs_review={needs_review}"
    )

    return final_record


async def test_simple_processing():
    """Test simple processing without graph framework"""

    # Path to the Texas voter file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
    )

    if not texas_csv.exists():
        print(f"❌ Texas voter file not found at: {texas_csv}")
        return

    print(f"🚀 Testing simple processing with Texas voter file")

    # Read first 3 records
    records = []
    try:
        with open(texas_csv, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if i >= 3:  # Limit to first 3 records for testing
                    break
                records.append(row)

                if i == 0:
                    print(f"📋 Sample record fields: {list(row.keys())[:10]}...")

    except UnicodeDecodeError:
        print("🔄 UTF-8 failed, trying with latin-1 encoding...")
        with open(texas_csv, encoding="latin-1") as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if i >= 3:
                    break
                records.append(row)

                if i == 0:
                    print(f"📋 Sample record fields: {list(row.keys())[:10]}...")

    print(f"📝 Read {len(records)} records for testing")

    # Process each record
    results = []
    for i, record in enumerate(records):
        try:
            result = await simple_process_record(record, f"test_{i:03d}")
            results.append(result)
        except Exception as e:
            print(f"💥 Failed to process record {i}: {e}")
            import traceback

            traceback.print_exc()

    # Summary
    successful = [r for r in results if not r.needs_review]
    needs_review = [r for r in results if r.needs_review]

    print(f"\n📊 Simple Processing Results:")
    print(f"   ✅ Successful: {len(successful)}")
    print(f"   ⚠️  Need Review: {len(needs_review)}")

    for i, result in enumerate(results):
        print(f"\n   Record {i+1} ({result.record_id}):")
        print(f"      Confidence: {result.overall_confidence:.2f}")
        print(f"      Errors: {len(result.processing_errors)}")
        print(f"      Needs Review: {result.needs_review}")
        if result.processing_errors:
            print(f"      Error Details: {result.processing_errors[:2]}")


async def main():
    """Main test function"""
    print("Simple Processing Test (Without Graph Framework)")
    print("=" * 60)

    await test_simple_processing()

    print("\n🎉 Simple processing test completed!")


if __name__ == "__main__":
    asyncio.run(main())
