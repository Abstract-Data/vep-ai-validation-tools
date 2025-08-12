"""
Core functionality for vep-ai-validation-tools.

This module contains the main entry points and convenience functions
for the voter validation system.
"""

import csv
from typing import Any, Dict, List

from .graph import process_voter_file_with_persistence
from .models import CompleteVoterRecord


def get_version_info() -> Dict[str, Any]:
    """
    Get version information about the package.

    Returns:
        Dictionary containing version information
    """
    from . import __author__, __email__, __version__

    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
    }


async def process_csv_file(csv_path: str) -> List[CompleteVoterRecord]:
    """
    Process a CSV file of voter records using built-in csv.DictReader.

    Args:
        csv_path: Path to the CSV file containing voter records

    Returns:
        List of processed voter records

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        UnicodeDecodeError: If the file encoding is not supported
    """
    # Read CSV using DictReader
    records = []
    with open(csv_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        records = list(reader)

    # Process with persistence
    results = await process_voter_file_with_persistence(records)

    return results


def main() -> None:
    """Main entry point for the package."""
    print("VEP AI Validation Tools")
    print(f"Version: {get_version_info()['version']}")
    print("\nUse the async functions to process voter data:")
    print("- process_csv_file(path) for CSV files")
    print("- process_individual_voter_record(record, id) for single records")


if __name__ == "__main__":
    main()
