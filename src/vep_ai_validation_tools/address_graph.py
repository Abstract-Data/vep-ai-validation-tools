"""
DEPRECATED: This file has been refactored into the new modular structure.

Use the following imports instead:
- from vep_ai_validation_tools.models import AddressParsingResult, AddressType, AddressComponent
- from vep_ai_validation_tools.agents import parse_address_fields
- from vep_ai_validation_tools.nodes import ParseAddressNode

This file is kept for reference but should not be used in new code.
"""

from .agents import parse_address_fields

# Re-export for backward compatibility
from .models import (
    AddressComponent,
    AddressParsingResult,
    AddressType,
    ParsedAddressField,
)
from .nodes import ParseAddressNode

__all__ = [
    "AddressType",
    "AddressComponent",
    "ParsedAddressField",
    "AddressParsingResult",
    "parse_address_fields",
    "ParseAddressNode",
]
