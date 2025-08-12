#!/usr/bin/env python3
"""
Debug script to examine field data that's causing the RenameModel error.
"""

import sys
import traceback
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from vep_ai_validation_tools.renaming.renaming import (
        FieldManager,
        FieldReferenceInfo,
    )

    print("🔧 Testing FieldManager creation...")

    # Create the field manager
    fields = FieldManager()
    print("✅ FieldManager created successfully")

    print(f"\n📊 Field data analysis:")
    print(f"   Loaded references: {len(fields.loaded_references)}")
    print(f"   Field mappings: {len(fields.field_mappings)}")

    # Check a few field definitions
    print(f"\n🔍 Sample field definitions:")
    for i, (field_name, field_info) in enumerate(fields.loaded_references.items()):
        if i >= 3:  # Only show first 3
            break
        print(f"   {field_name}:")
        print(f"     - Type: {type(field_info)}")
        print(f"     - Description: {field_info.field_description}")
        print(f"     - Possible values: {field_info.field_possible_values}")
        print(f"     - Possible values type: {type(field_info.field_possible_values)}")
        print(f"     - Possible values length: {len(field_info.field_possible_values)}")

    print(f"\n🔧 Testing field mappings creation...")

    # Test the field mappings creation step by step
    field_definitions = fields.loaded_references
    field_mappings = {}

    for field_name, field_info in field_definitions.items():
        try:
            print(f"   Processing field: {field_name}")

            # Ensure field_info is a FieldReferenceInfo object
            if not isinstance(field_info, FieldReferenceInfo):
                print(f"     ❌ Not a FieldReferenceInfo object: {type(field_info)}")
                continue

            print(f"     ✅ Is FieldReferenceInfo object")
            print(f"     - Possible values: {field_info.field_possible_values}")

            # Test the AliasChoices creation
            from pydantic import AliasChoices

            if field_info.field_possible_values:
                try:
                    alias_choices = AliasChoices(*field_info.field_possible_values)
                    print(f"     ✅ AliasChoices created successfully")
                except Exception as e:
                    print(f"     ❌ AliasChoices failed: {e}")
                    continue
            else:
                print(f"     ⚠️  No possible values, skipping AliasChoices")
                continue

            # Create the field mapping
            from typing import Optional

            from pydantic import Field as PydanticField

            field_mappings[field_info.field_name] = (
                Optional[str],
                PydanticField(
                    alias=alias_choices,
                    description=field_info.field_description,
                    default=None,
                ),
            )
            print(f"     ✅ Field mapping created")

        except Exception as e:
            print(f"     ❌ Error processing field {field_name}: {e}")
            traceback.print_exc()
            break

    print(f"\n✅ Processed {len(field_mappings)} field mappings")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔍 Full traceback:")
    traceback.print_exc()
