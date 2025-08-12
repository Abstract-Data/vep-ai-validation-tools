"""
Address parsing agent and functions.
"""

from pathlib import Path
from typing import Any, Dict

from pydantic_ai import Agent

from ..models import AddressParsingResult
from .base import create_ollama_model

# Create the address parsing agent
ollama_model = create_ollama_model()
prompt_path = Path(__file__).parent.parent / "prompts" / "address_parsing.md"
address_parser_agent = Agent(
    ollama_model,
    output_type=AddressParsingResult,
    system_prompt=prompt_path.read_text(),
)


async def parse_address_fields(voter_record: Dict[str, Any]) -> AddressParsingResult:
    """Parse all address fields from a voter record"""

    # Extract address-related fields
    address_fields = {}

    # Look for known address field patterns
    address_patterns = [
        "mail_",
        "residence_",
        "MAILING",
        "RESIDENTIAL",
        "ADDRESS",
        "MAILINGCITY",
        "MLCITY",
        "RCITY",
        "RZIP",
        "MZIP",
        "RA_",
        "MA_",
        "MLADD",
        "MADR",
        "STRNAM",
        "HOUSENUMBER",
    ]

    for field_name, value in voter_record.items():
        if value and any(pattern in field_name.upper() for pattern in address_patterns):
            address_fields[field_name] = value

    if not address_fields:
        return AddressParsingResult(total_fields_processed=0)

    # Format input for the agent
    input_text = f"""
ADDRESS FIELDS TO PARSE:
{address_fields}

Parse each field according to the rules above, identifying whether it's a mailing or residence address component.
"""

    result = await address_parser_agent.run(input_text)
    result.output.total_fields_processed = len(address_fields)

    return result.output
