"""
Base node types and common functionality.
"""

from typing import Any, Dict, List

from ..models import ParsedAddress, ParsedAddressField


def build_address_from_fields(fields: List[ParsedAddressField]) -> ParsedAddress:
    """Build complete address from parsed fields"""
    components = {f.component.value: f.field_value for f in fields}
    return ParsedAddress(
        address1=components.get("address1", ""),
        address2=components.get("address2", ""),
        city=components.get("city", ""),
        state=components.get("state", ""),
        zip5=components.get("zip5", ""),
        zip4=components.get("zip4", ""),
        confidence=sum(f.confidence for f in fields) / len(fields) if fields else 0.0,
        raw_input=str({f.field_name: f.field_value for f in fields}),
    )


def extract_name_text(record: Dict[str, Any]) -> str:
    """Extract name fields from various possible column names"""
    name_parts = []
    for field in ["first_name", "last_name", "middle_name", "name_first", "name_last"]:
        if field in record and record[field]:
            name_parts.append(str(record[field]))
    return " ".join(name_parts)
