"""
District parsing agent and functions.
"""

from pathlib import Path
from typing import Any, Dict

from pydantic_ai import Agent

from ..models import DistrictParsingResult, ParsedDistrict
from .base import create_ollama_model

# Create the district parsing agent
ollama_model = create_ollama_model()
prompt_path = Path(__file__).parent.parent / "prompts" / "district_parsing.md"
district_parser_agent = Agent(
    ollama_model,
    output_type=DistrictParsingResult,
    system_prompt=prompt_path.read_text(),
)


async def parse_district_fields(voter_record: Dict[str, Any]) -> DistrictParsingResult:
    """Parse all district fields from a voter record"""

    # Check if districts are already structured as a list
    if "districts" in voter_record and isinstance(voter_record["districts"], list):
        # Districts are already parsed, convert to ParsedDistrict objects
        districts = []
        for district_data in voter_record["districts"]:
            if isinstance(district_data, dict):
                district = ParsedDistrict(
                    field_name="districts",
                    district_level=district_data.get("district_level", "unknown"),
                    district_type=district_data.get("district_name", "unknown"),
                    district_number=district_data.get("district_number"),
                    district_value=str(district_data),
                    confidence=0.95,
                )
                districts.append(district)

        return DistrictParsingResult(
            districts=districts,
            total_fields_processed=len(voter_record["districts"]),
            successfully_parsed=len(districts),
        )

    # Extract district-related fields
    district_fields = {}

    # Common district field patterns
    district_patterns = [
        "district_",
        "dist_",
        "legislative_",
        "congress",
        "senate",
        "house",
        "school_",
        "municipal_",
        "county_",
        "court_",
        "precinct",
        "ward",
        "beat",
        "council",
        "commissioner",
    ]

    for field_name, value in voter_record.items():
        if value and any(
            pattern in field_name.lower() for pattern in district_patterns
        ):
            district_fields[field_name] = value

    if not district_fields:
        return DistrictParsingResult(total_fields_processed=0)

    # Format input for the agent
    input_text = f"""
DISTRICT FIELDS TO PARSE:
{district_fields}

Parse each field according to the district parsing rules above.
"""

    result = await district_parser_agent.run(input_text)
    result.output.total_fields_processed = len(district_fields)

    return result.output
