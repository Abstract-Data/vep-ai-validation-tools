#!/usr/bin/env python3
"""
Test script to see how the RenameModel is transforming the data.
"""

import asyncio
import csv
from pathlib import Path

from vep_ai_validation_tools.renaming.renaming import FieldManager


def test_rename_model():
    """Test the RenameModel data transformation"""

    # Create RenameModel
    fields = FieldManager()
    RenameModel = fields.create_rename_model_safe()

    # Read one record from Texas file
    texas_csv = Path(
        "/Users/johneakin/PyCharmProjects/vep-ai-validation-tools/examples/sample_data.csv"
    )

    # Create a sample record
    sample_record = {
        "COUNTY": "ANDERSON",
        "PCT": "0003",
        "NEWCD": "6",
        "NEWSD": "3",
        "NEWHD": "8",
        "VUID": "2215516075",
        "LNAME": "MONK",
        "FNAME": "KAMERON",
        "MNAME": "JOE",
        "FORMERNAME": "",
        "mail_address1": "129 OAKLAND",
        "mail_city": "PALESTINE",
        "mail_state": "TX",
        "mail_zip5": "75801",
        "file_origin": "texasnovember2024.csv",
    }

    print("🧪 TESTING RENAME MODEL")
    print("=" * 50)

    print(f"\n📋 SAMPLE RECORD:")
    for key, value in sample_record.items():
        print(f"   {key}: {value}")

    # Transform the record
    try:
        transformed_record = RenameModel(**sample_record)
        print(f"\n✅ TRANSFORMATION SUCCESSFUL!")

        print(f"\n🔄 TRANSFORMED RECORD:")
        print(f"   Type: {type(transformed_record)}")
        print(f"   Model fields: {list(transformed_record.model_fields.keys())}")

        # Check structured fields
        print(f"\n📊 STRUCTURED FIELDS:")
        print(f"   districts: {transformed_record.districts}")
        print(f"   voter_registration: {transformed_record.voter_registration}")
        print(f"   phone: {transformed_record.phone}")
        print(f"   data_source: {transformed_record.data_source}")
        print(f"   person_name: {transformed_record.person_name}")
        print(f"   address_list: {transformed_record.address_list}")

        # Check if extra fields are accessible
        print(f"\n🔍 EXTRA FIELDS:")
        extra_fields = []
        for field_name in sample_record.keys():
            if hasattr(transformed_record, field_name):
                value = getattr(transformed_record, field_name)
                extra_fields.append(f"   {field_name}: {value}")

        if extra_fields:
            for field in extra_fields:
                print(field)
        else:
            print("   No extra fields found")

        # Check model_extra
        if hasattr(transformed_record, "model_extra"):
            print(f"\n📦 MODEL_EXTRA:")
            print(f"   {transformed_record.model_extra}")

        # Convert to dict
        record_dict = transformed_record.model_dump()
        print(f"\n📋 AS DICT (first 10 fields):")
        for i, (key, value) in enumerate(record_dict.items()):
            if i >= 10:
                break
            print(f"   {key}: {value}")

    except Exception as e:
        print(f"\n❌ TRANSFORMATION FAILED: {e}")
        print(f"Error type: {type(e)}")


if __name__ == "__main__":
    test_rename_model()
