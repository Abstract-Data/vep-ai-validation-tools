"""
Data models for voter registration validation.

This module contains all Pydantic models and data structures used throughout
the voter validation system.
"""

from .address import AddressParsingResult, ParsedAddressField
from .district import DistrictParsingResult, ParsedDistrict
from .election import ElectionParsingResult, ParsedElection
from .enums import (
    AddressComponent,
    AddressType,
    DistrictLevel,
    ElectionJurisdiction,
    ElectionType,
    VotingMethod,
)
from .voter import (
    CompleteVoterRecord,
    ParsedAddress,
    ParsedName,
    ParsedPhone,
    VoterProcessingState,
    create_failed_voter_record,
    create_partial_voter_record,
)

__all__ = [
    # Enums
    "AddressType",
    "AddressComponent",
    "DistrictLevel",
    "ElectionType",
    "VotingMethod",
    "ElectionJurisdiction",
    # Address models
    "ParsedAddressField",
    "AddressParsingResult",
    # District models
    "ParsedDistrict",
    "DistrictParsingResult",
    # Election models
    "ParsedElection",
    "ElectionParsingResult",
    # Voter models
    "ParsedName",
    "ParsedPhone",
    "ParsedAddress",
    "VoterProcessingState",
    "CompleteVoterRecord",
    "create_failed_voter_record",
    "create_partial_voter_record",
]
