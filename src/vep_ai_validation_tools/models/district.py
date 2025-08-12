"""
District-related data models.
"""

from typing import List, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from .enums import DistrictLevel


class ParsedDistrict(BaseModel):
    """Parsed legislative/administrative district information"""

    field_name: str = PydanticField(description="Original field name from source data")
    district_level: DistrictLevel = PydanticField(
        description="Level of government (federal, state, county, city, court)"
    )
    district_type: str = PydanticField(
        description="Type of district (congressional, senate, school, etc)"
    )
    district_number: Optional[str] = PydanticField(
        default=None, description="District number/identifier if present"
    )
    district_value: str = PydanticField(description="The actual value from the data")
    confidence: float = PydanticField(
        default=0.0, ge=0.0, le=1.0, description="Parsing confidence"
    )

    class Config:
        use_enum_values = True


class DistrictParsingResult(BaseModel):
    """Result of parsing all district fields from a record"""

    districts: List[ParsedDistrict] = PydanticField(default_factory=list)
    parsing_errors: List[str] = PydanticField(default_factory=list)
    total_fields_processed: int = 0
    successfully_parsed: int = 0
