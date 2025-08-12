"""
Election-related data models.
"""

from typing import List, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from .enums import ElectionJurisdiction, ElectionType, VotingMethod


class ParsedElection(BaseModel):
    """Individual parsed election record"""

    field_name: str = PydanticField(description="Original field name from source")
    election_date: Optional[str] = PydanticField(
        default=None, description="Election date (YYYY-MM-DD if parseable)"
    )
    election_type: ElectionType = PydanticField(description="Type of election")
    election_year: Optional[int] = PydanticField(
        default=None, description="Election year"
    )
    participated: bool = PydanticField(description="Whether voter participated")
    voting_method: Optional[VotingMethod] = PydanticField(
        default=None, description="How they voted"
    )
    jurisdiction: Optional[ElectionJurisdiction] = PydanticField(
        default=None, description="Election jurisdiction"
    )
    raw_value: str = PydanticField(description="Original raw value from data")
    confidence: float = PydanticField(
        default=0.0, ge=0.0, le=1.0, description="Parsing confidence"
    )


class ElectionParsingResult(BaseModel):
    """Result of parsing all election fields from a record"""

    elections: List[ParsedElection] = PydanticField(default_factory=list)
    parsing_errors: List[str] = PydanticField(default_factory=list)
    total_fields_processed: int = 0
    successfully_parsed: int = 0
    election_years_found: List[int] = PydanticField(default_factory=list)
