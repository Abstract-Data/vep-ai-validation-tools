#!/usr/bin/env python3
"""
Basic usage example for the VEP AI Validation Tools.

This script demonstrates how to use the refactored modular architecture
to process voter registration data.
"""

import asyncio
import csv
from pathlib import Path

# Import the main processing functions
from vep_ai_validation_tools import (
    create_voter_processing_graph,
    process_individual_voter_record,
    process_voter_file_with_persistence,
)
from vep_ai_validation_tools.models import VoterProcessingState

# No longer need process_csv_file since we're using DictReader directly


async def example_single_record():
    """Example of processing a single voter record"""

    # Sample voter record
    sample_record = {
        "first_name": "John",
        "last_name": "Doe",
        "mail_address1": "123 Main St",
        "mail_city": "Austin",
        "mail_state": "TX",
        "mail_zip5": "78701",
        "residence_address1": "456 Oak Ave",
        "residence_city": "Austin",
        "residence_state": "TX",
        "residence_zip5": "78702",
        "district_federal_congressional": "DIST10",
        "district_state_senate": "DIST14",
        "election_2024_general": "Y",
        "election_2022_general": "Y",
    }

    print("🚀 Processing single voter record...")
    result = await process_individual_voter_record(sample_record, "sample_001")

    print(f"✅ Processing complete!")
    print(
        f"   Name: {result.name.first_name if result.name else 'N/A'} {result.name.last_name if result.name else ''}"
    )
    print(f"   Confidence: {result.overall_confidence:.2f}")
    print(f"   Needs Review: {result.needs_review}")

    return result


async def example_csv_processing():
    """Example of processing a CSV file using csv.DictReader"""

    # Use the actual Texas voter file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
    )

    if not texas_csv.exists():
        print(f"❌ Texas voter file not found at: {texas_csv}")
        print("Creating a sample CSV for demonstration...")

        # Create a sample CSV for demonstration if the real file doesn't exist
        sample_data = [
            {
                "voter_id": "001",
                "first_name": "Alice",
                "last_name": "Smith",
                "mail_address1": "789 Pine St",
                "mail_city": "Dallas",
                "mail_state": "TX",
                "mail_zip5": "75201",
            },
            {
                "voter_id": "002",
                "first_name": "Bob",
                "last_name": "Johnson",
                "residence_address1": "321 Elm St",
                "residence_city": "Houston",
                "residence_state": "TX",
                "residence_zip5": "77001",
            },
        ]

        # Save to temporary CSV
        temp_csv = Path("/tmp/sample_voters.csv")
        with open(temp_csv, "w", newline="", encoding="utf-8") as csvfile:
            if sample_data:
                fieldnames = sample_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)

        csv_file = temp_csv
    else:
        csv_file = texas_csv

    print(f"🚀 Processing CSV file: {csv_file}")

    # Read CSV using DictReader and process records
    records = []
    with open(csv_file, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        # Process first 5 records for demonstration
        for i, row in enumerate(reader):
            if i >= 5:  # Limit to first 5 records for demo
                break
            records.append(row)

    print(f"📝 Read {len(records)} records from CSV")

    # Process the records
    results = await process_voter_file_with_persistence(records)

    print(f"✅ Processed {len(results)} records")

    # Summary
    successful = [r for r in results if not r.needs_review]
    needs_review = [r for r in results if r.needs_review]

    print(
        f"   📊 Results: {len(successful)} successful, {len(needs_review)} need review"
    )

    # Show some details from first result
    if results:
        first_result = results[0]
        print(f"   📋 First record details:")
        print(f"      ID: {first_result.record_id}")
        print(f"      Confidence: {first_result.overall_confidence:.2f}")
        print(f"      Errors: {len(first_result.processing_errors)}")

    # Clean up temporary file if we created one
    if csv_file.name == "sample_voters.csv":
        csv_file.unlink()

    return results


async def example_custom_graph():
    """Example of creating and using a custom graph"""

    # Create the graph
    graph = create_voter_processing_graph()

    sample_record = {
        "first_name": "Custom",
        "last_name": "User",
        "mail_address1": "999 Custom St",
    }

    # Initialize state
    initial_state = VoterProcessingState(
        raw_record=sample_record, record_id="custom_001"
    )

    print("🚀 Running custom graph...")

    # Import the starting node
    from vep_ai_validation_tools.nodes import ParseNameNode

    # Run the graph
    result = await graph.run(ParseNameNode(), state=initial_state)

    print(f"✅ Custom graph complete!")
    print(f"   Record ID: {result.output.record_id}")
    print(f"   Overall Confidence: {result.output.overall_confidence:.2f}")

    return result.output


async def main():
    """Main example function"""

    print("VEP AI Validation Tools - Usage Examples")
    print("=" * 50)

    # Example 1: Single record
    print("\n1. Single Record Processing")
    print("-" * 30)
    await example_single_record()

    # Example 2: CSV file
    print("\n2. CSV File Processing")
    print("-" * 30)
    await example_csv_processing()

    # Example 3: Custom graph
    print("\n3. Custom Graph Usage")
    print("-" * 30)
    await example_custom_graph()

    print("\n🎉 All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
