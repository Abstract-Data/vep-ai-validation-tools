"""
Election parsing agent and functions.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from pydantic_ai import Agent

from ..models import ElectionJurisdiction, ElectionParsingResult, ElectionType
from .base import create_ollama_model

# Create the election parsing agent
ollama_model = create_ollama_model()
prompt_path = Path(__file__).parent.parent / "prompts" / "election_parsing.md"
election_parser_agent = Agent(
    ollama_model,
    output_type=ElectionParsingResult,
    system_prompt=prompt_path.read_text(),
)


async def validate_election_parsing(
    output: ElectionParsingResult,
) -> ElectionParsingResult:
    """Validate and clean election parsing results"""

    errors = []
    cleaned_elections = []
    years_found = set()

    for election in output.elections:
        # Validate and clean election year
        if election.election_year:
            current_year = datetime.now().year
            if (
                election.election_year < 1900
                or election.election_year > current_year + 4
            ):
                errors.append(f"Invalid election year: {election.election_year}")
                continue
            years_found.add(election.election_year)

        # Validate election date format if present
        if election.election_date:
            try:
                # Try to parse the date to validate format
                datetime.strptime(election.election_date, "%Y-%m-%d")
            except ValueError:
                # Try other common formats and convert
                date_patterns = [
                    r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY
                    r"(\d{4})-(\d{1,2})-(\d{1,2})",  # YYYY-MM-DD
                    r"(\d{1,2})-(\d{1,2})-(\d{4})",  # MM-DD-YYYY
                ]

                parsed_date = None
                for pattern in date_patterns:
                    match = re.search(pattern, election.election_date)
                    if match:
                        try:
                            if (
                                pattern == date_patterns[0]
                                or pattern == date_patterns[2]
                            ):  # MM/DD/YYYY or MM-DD-YYYY
                                month, day, year = match.groups()
                                parsed_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            else:  # YYYY-MM-DD
                                year, month, day = match.groups()
                                parsed_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            break
                        except:
                            continue

                if parsed_date:
                    election.election_date = parsed_date
                else:
                    election.election_date = None
                    errors.append(f"Could not parse date: {election.election_date}")

        # Infer missing jurisdiction based on election type and year
        if (
            not election.jurisdiction
            or election.jurisdiction == ElectionJurisdiction.UNKNOWN
        ):
            if election.election_type in [ElectionType.GENERAL, ElectionType.PRIMARY]:
                if election.election_year and election.election_year % 2 == 0:
                    election.jurisdiction = ElectionJurisdiction.FEDERAL
                else:
                    election.jurisdiction = ElectionJurisdiction.STATE
            elif election.election_type == ElectionType.MUNICIPAL:
                election.jurisdiction = ElectionJurisdiction.MUNICIPAL
            elif election.election_type == ElectionType.SCHOOL:
                election.jurisdiction = ElectionJurisdiction.SCHOOL_DISTRICT

        # Set minimum confidence for parsed elections
        if election.confidence < 0.3:
            election.confidence = 0.3

        cleaned_elections.append(election)

    output.elections = cleaned_elections
    output.successfully_parsed = len(cleaned_elections)
    output.election_years_found = sorted(list(years_found), reverse=True)
    output.parsing_errors.extend(errors)

    if len(errors) > len(cleaned_elections):  # More errors than successes
        print(f"Warning: Too many election parsing errors: {errors[:3]}")

    return output


async def parse_election_fields(voter_record: Dict[str, Any]) -> ElectionParsingResult:
    """Parse all election-related fields from a voter record"""

    # Extract election-related fields
    election_fields = {}

    # Common election field patterns
    election_patterns = [
        "election_",
        "vote_",
        "voted_",
        "elec_",
        "history_",
        "general",
        "primary",
        "special",
        "municipal",
        "school",
        "gen",
        "pri",
        "prir",
        "sp",
        "mun",
        "runoff",
        "2020",
        "2021",
        "2022",
        "2023",
        "2024",  # Recent years
    ]

    for field_name, value in voter_record.items():
        # Skip if value is None or empty string
        if not value:
            continue

        field_lower = field_name.lower()
        value_str = str(value).strip()

        # Check if field matches election patterns
        if any(pattern in field_lower for pattern in election_patterns):
            election_fields[field_name] = value_str

        # Also check for date-like patterns that might be elections
        elif re.search(r"\d{4}", field_name) and re.search(
            r"\d{1,2}[/_-]\d{1,2}[/_-]\d{4}", value_str
        ):
            election_fields[field_name] = value_str

    if not election_fields:
        return ElectionParsingResult(total_fields_processed=0)

    # Format input for the agent
    input_text = f"""
ELECTION FIELDS TO PARSE:
{election_fields}

Parse each field according to the election parsing rules above.
"""

    result = await election_parser_agent.run(input_text)
    result.output.total_fields_processed = len(election_fields)

    # Apply validation
    validated_output = await validate_election_parsing(result.output)

    return validated_output
