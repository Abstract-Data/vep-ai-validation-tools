"""
Enumeration types used throughout the voter validation system.
"""

from enum import Enum


class AddressType(str, Enum):
    """Type of address: mailing or residence"""

    MAILING = "mailing"
    RESIDENCE = "residence"


class AddressComponent(str, Enum):
    """Components that make up an address"""

    # Standard address components
    ADDRESS1 = "address1"
    ADDRESS2 = "address2"
    CITY = "city"
    STATE = "state"
    ZIP5 = "zip5"
    ZIP4 = "zip4"
    COUNTRY = "country"
    STANDARDIZED = "standardized"

    # Residence-specific granular components
    HOUSE_NUMBER = "house_number"
    HOUSE_DIRECTION = "house_direction"
    STREET_NAME = "street_name"
    STREET_TYPE = "street_type"
    STREET_DIRECTION = "street_direction"
    STREET_PRE_DIRECTIONAL = "street_pre_directional"
    STREET_POST_DIRECTIONAL = "street_post_directional"
    UNIT_NUMBER = "unit_number"
    UNIT_TYPE = "unit_type"

    # Special fields
    CHANGE_DATE = "change_date"
    EFFECTIVE_DATE = "effective_date"
    ADDRESS_ID = "address_id"


class DistrictLevel(str, Enum):
    """Level of government district"""

    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    CITY = "city"
    COURT = "court"


class ElectionType(str, Enum):
    """Type of election"""

    GENERAL = "general"
    PRIMARY = "primary"
    PRIMARY_RUNOFF = "primary_runoff"
    GENERAL_RUNOFF = "general_runoff"
    SPECIAL = "special"
    MUNICIPAL = "municipal"
    SCHOOL = "school"
    LOCAL = "local"
    PRESIDENTIAL_PRIMARY = "presidential_primary"
    BOND = "bond"
    CONSTITUTIONAL = "constitutional"
    RECALL = "recall"
    UNKNOWN = "unknown"


class VotingMethod(str, Enum):
    """Method used to vote"""

    EARLY = "early"
    ABSENTEE = "absentee"
    DAY_OF = "day_of"
    MAIL = "mail"
    PROVISIONAL = "provisional"
    UNKNOWN = "unknown"


class ElectionJurisdiction(str, Enum):
    """Jurisdiction level of election"""

    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    MUNICIPAL = "municipal"
    SCHOOL_DISTRICT = "school_district"
    SPECIAL_DISTRICT = "special_district"
    UNKNOWN = "unknown"
