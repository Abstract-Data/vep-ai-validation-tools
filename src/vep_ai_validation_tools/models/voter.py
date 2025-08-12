"""
Voter-related data models and processing state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .address import ParsedAddressField
from .district import ParsedDistrict
from .election import ParsedElection


class ParsedName(BaseModel):
    """Parsed voter name information"""

    first_name: str
    last_name: str
    middle_name: str | None = None
    suffix: str | None = None
    dob: date
    confidence: float
    raw_input: str


class ParsedPhone(BaseModel):
    """Parsed phone number information"""

    phone_type: str
    phone_number: str
    confidence: float
    raw_input: str


class ParsedAddress(BaseModel):
    """Complete parsed address"""

    address1: str = ""
    address2: str | None = None
    city: str = ""
    state: str = ""
    zip5: str = ""
    zip4: str | None = None
    confidence: float = 0.0
    raw_input: str = ""

    @property
    def normalized_address(self) -> str:
        """Get normalized address string"""
        parts = [self.address1, self.address2, self.city, self.state]
        address_parts = [p for p in parts if p.strip()]

        if self.zip5:
            zip_code = self.zip5
            if self.zip4:
                zip_code += f"-{self.zip4}"
            address_parts.append(zip_code)

        return ", ".join(address_parts)


@dataclass
class VoterProcessingState:
    """State that flows through the graph as we process a voter record"""

    # Original record
    raw_record: dict[str, Any]
    record_id: str

    # Parsed components (filled in by nodes)
    parsed_name: ParsedName | None = None
    parsed_mailing_address: ParsedAddress | None = None
    parsed_residence_address: ParsedAddress | None = None
    parsed_districts: list[ParsedDistrict] = field(default_factory=list)
    parsed_elections: list[ParsedElection] = field(default_factory=list)

    # Processing metadata
    processing_errors: list[str] = field(default_factory=list)
    retry_count: int = 0
    confidence_scores: dict[str, float] = field(default_factory=dict)
    processing_stage: str = "starting"

    # Final assembled record
    final_voter_record: CompleteVoterRecord | None = None


class CompleteVoterRecord(BaseModel):
    """Final assembled voter record with all parsed components"""

    # Record identification
    record_id: str = Field(description="Unique identifier for this voter record")
    original_record: dict[str, Any] | None = Field(
        default=None, description="Original raw CSV record"
    )

    # Parsed components
    name: ParsedName | None = Field(default=None, description="Parsed voter name")
    mailing_address: ParsedAddress | None = Field(
        default=None, description="Parsed mailing address"
    )
    residence_address: ParsedAddress | None = Field(
        default=None, description="Parsed residence address"
    )
    districts: list[ParsedDistrict] = Field(
        default_factory=list, description="All parsed legislative districts"
    )
    elections: list[ParsedElection] = Field(
        default_factory=list, description="All parsed election participation"
    )

    # Quality metrics
    confidence_scores: dict[str, float] = Field(
        default_factory=dict, description="Confidence score per component"
    )
    overall_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall parsing confidence"
    )

    # Processing metadata
    processing_errors: list[str] = Field(
        default_factory=list, description="Errors encountered during processing"
    )
    processing_warnings: list[str] = Field(
        default_factory=list, description="Warnings during processing"
    )
    processing_timestamp: datetime = Field(
        default_factory=datetime.now, description="When record was processed"
    )
    processing_duration_seconds: float | None = Field(
        default=None, description="How long processing took"
    )

    # Review flags
    needs_review: bool = Field(
        default=False, description="Whether record needs human review"
    )
    review_reasons: list[str] = Field(
        default_factory=list, description="Reasons why review is needed"
    )
    reviewed_by: str | None = Field(
        default=None, description="Who reviewed this record"
    )
    review_timestamp: datetime | None = Field(
        default=None, description="When record was reviewed"
    )
    review_notes: str | None = Field(default=None, description="Review notes")

    # Computed properties
    @property
    def is_complete(self) -> bool:
        """Check if record has minimum required components"""
        return bool(
            self.name
            and (self.mailing_address or self.residence_address)
            and self.districts
        )

    @property
    def primary_address(self) -> ParsedAddress | None:
        """Get the primary address (residence preferred, fallback to mailing)"""
        return self.residence_address or self.mailing_address

    @property
    def election_years(self) -> list[int]:
        """Get sorted list of election years voter participated in"""
        years = {
            e.election_year
            for e in self.elections
            if e.election_year and e.participated
        }
        return sorted(years, reverse=True)

    @property
    def latest_election_year(self) -> int | None:
        """Get most recent election year voter participated in"""
        years = self.election_years
        return years[0] if years else None

    @property
    def district_summary(self) -> dict[str, list[str]]:
        """Get summary of districts by level"""
        summary = {}
        for district in self.districts:
            level = district.district_level
            if level not in summary:
                summary[level] = []

            district_info = f"{district.district_type}"
            if district.district_number:
                district_info += f" {district.district_number}"
            summary[level].append(district_info)

        return summary

    def to_summary_dict(self) -> dict[str, Any]:
        """Convert to summary dictionary for reporting"""
        return {
            "record_id": self.record_id,
            "name": (
                f"{self.name.first_name} {self.name.last_name}"
                if self.name
                else "UNKNOWN"
            ),
            "primary_address": (
                self.primary_address.normalized_address
                if self.primary_address
                else "UNKNOWN"
            ),
            "district_count": len(self.districts),
            "election_count": len([e for e in self.elections if e.participated]),
            "latest_election": self.latest_election_year,
            "overall_confidence": self.overall_confidence,
            "needs_review": self.needs_review,
            "is_complete": self.is_complete,
            "processing_errors": len(self.processing_errors),
        }


def create_failed_voter_record(
    record_id: str, error_message: str, original_record: dict[str, Any] | None = None
) -> CompleteVoterRecord:
    """Create a voter record representing a processing failure"""
    return CompleteVoterRecord(
        record_id=record_id,
        original_record=original_record,
        processing_errors=[error_message],
        needs_review=True,
        review_reasons=["Processing failed"],
        overall_confidence=0.0,
    )


def create_partial_voter_record(
    record_id: str,
    parsed_components: dict[str, Any],
    errors: list[str] = None,
    confidence_scores: dict[str, float] = None,
) -> CompleteVoterRecord:
    """Create a voter record from partially parsed components"""

    return CompleteVoterRecord(
        record_id=record_id,
        name=parsed_components.get("name"),
        mailing_address=parsed_components.get("mailing_address"),
        residence_address=parsed_components.get("residence_address"),
        districts=parsed_components.get("districts", []),
        elections=parsed_components.get("elections", []),
        confidence_scores=confidence_scores or {},
        overall_confidence=(
            sum(confidence_scores.values()) / len(confidence_scores)
            if confidence_scores
            else 0.0
        ),
        processing_errors=errors or [],
        needs_review=bool(errors)
        or (
            confidence_scores
            and sum(confidence_scores.values()) / len(confidence_scores) < 0.7
        ),
    )
