"""
Address-related data models.
"""

from typing import List

from pydantic import BaseModel
from pydantic import Field as PydanticField

from .enums import AddressComponent, AddressType


class ParsedAddressField(BaseModel):
    """Individual parsed address field"""

    field_name: str = PydanticField(description="Original field name from source")
    address_type: AddressType = PydanticField(
        description="Whether this is mailing or residence address"
    )
    component: AddressComponent = PydanticField(
        description="What address component this represents"
    )
    field_value: str = PydanticField(description="The actual value from the data")
    confidence: float = PydanticField(
        default=0.0, ge=0.0, le=1.0, description="Parsing confidence"
    )


class AddressParsingResult(BaseModel):
    """Result of parsing all address fields from a record"""

    mailing_fields: List[ParsedAddressField] = PydanticField(default_factory=list)
    residence_fields: List[ParsedAddressField] = PydanticField(default_factory=list)
    parsing_errors: List[str] = PydanticField(default_factory=list)
    total_fields_processed: int = 0
    successfully_parsed: int = 0
