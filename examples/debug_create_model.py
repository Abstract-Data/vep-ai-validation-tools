#!/usr/bin/env python3
"""
Debug script to test the create_model call step by step.
"""

import sys
import traceback
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from typing import Optional

    from pydantic import ConfigDict
    from pydantic import Field as PydanticField
    from pydantic import create_model, model_validator

    from vep_ai_validation_tools.renaming.renaming import FieldManager

    print("🔧 Testing FieldManager creation...")

    # Create the field manager
    fields = FieldManager()
    print("✅ FieldManager created successfully")

    print(f"\n📊 Field data:")
    print(f"   Field mappings: {len(fields.field_mappings)}")

    print(f"\n🔧 Testing create_model step by step...")

    # Test 1: Basic model without field mappings
    print("   Test 1: Basic model without field mappings...")
    try:
        config = ConfigDict(str_strip_whitespace=True, extra="allow")
        basic_model = create_model(
            "BasicModel",
            __config__=config,
            districts=(
                list,
                PydanticField(default_factory=list, description="List of districts"),
            ),
            voter_registration=(
                dict,
                PydanticField(
                    default_factory=dict, description="Voter registration details"
                ),
            ),
        )
        print("   ✅ Basic model created successfully")
    except Exception as e:
        print(f"   ❌ Basic model failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Test 2: Model with validators
    print("   Test 2: Model with validators...")
    try:
        from vep_ai_validation_tools.renaming.renaming_funcs import (
            AgenticValidationFuncs as AVF,
        )

        # Only use validators that don't depend on config files
        safe_validators = {
            "strip_whitespace": model_validator(mode="before")(AVF._strip_whitespace),
            "set_file_origin": model_validator(mode="before")(AVF.set_file_origin),
        }
        print(f"   ✅ Got safe validators: {list(safe_validators.keys())}")

        model_with_validators = create_model(
            "ModelWithValidators",
            __config__=config,
            __validators__=safe_validators,
            districts=(
                list,
                PydanticField(default_factory=list, description="List of districts"),
            ),
        )
        print("   ✅ Model with validators created successfully")
    except Exception as e:
        print(f"   ❌ Model with validators failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Test 3: Model with a few field mappings
    print("   Test 3: Model with a few field mappings...")
    try:
        # Take just the first 3 field mappings
        sample_mappings = dict(list(fields.field_mappings.items())[:3])
        print(f"   Using {len(sample_mappings)} sample field mappings")

        model_with_mappings = create_model(
            "ModelWithMappings",
            __config__=config,
            __validators__=safe_validators,
            districts=(
                list,
                PydanticField(default_factory=list, description="List of districts"),
            ),
            **sample_mappings,
        )
        print("   ✅ Model with mappings created successfully")
    except Exception as e:
        print(f"   ❌ Model with mappings failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Test 4: Full model creation
    print("   Test 4: Full model creation...")
    try:
        full_model = create_model(
            "FullModel",
            __config__=config,
            __validators__=safe_validators,
            districts=(
                list,
                PydanticField(default_factory=list, description="List of districts"),
            ),
            voter_registration=(
                dict,
                PydanticField(
                    default_factory=dict, description="Voter registration details"
                ),
            ),
            phone=(
                list,
                PydanticField(default=None, description="List of phone numbers"),
            ),
            data_source=(
                list,
                PydanticField(default=None, description="List of data sources"),
            ),
            person_name=(
                dict,
                PydanticField(default=None, description="Person name details"),
            ),
            address_list=(
                list,
                PydanticField(
                    default_factory=list, description="List of address details"
                ),
            ),
            **fields.field_mappings,
        )
        print("   ✅ Full model created successfully")
        print(f"   Model has {len(full_model.model_fields)} fields")
    except Exception as e:
        print(f"   ❌ Full model failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("\n🎉 All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔍 Full traceback:")
    traceback.print_exc()
