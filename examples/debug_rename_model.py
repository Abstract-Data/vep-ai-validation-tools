#!/usr/bin/env python3
"""
Debug script to isolate the RenameModel creation error.
"""

import sys
import traceback
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from vep_ai_validation_tools.renaming.renaming import FieldManager

    print("🔧 Testing FieldManager creation...")

    # Create the field manager
    fields = FieldManager()
    print("✅ FieldManager created successfully")

    print("🔧 Testing RenameModel creation...")

    # Try to create the rename model
    RenameModel = fields.create_rename_model_safe()
    print("✅ RenameModel created successfully")

    print("🎉 All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔍 Full traceback:")
    traceback.print_exc()
