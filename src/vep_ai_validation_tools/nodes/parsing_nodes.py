"""
Nodes responsible for parsing different components of voter records.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any, Union

from pydantic_ai import Agent
from pydantic_graph import BaseNode, Edge, GraphRunContext

from ..agents import parse_address_fields, parse_district_fields, parse_election_fields
from ..agents.base import create_ollama_model
from ..models import ParsedName, VoterProcessingState
from .base import build_address_from_fields, extract_name_text

# Import all nodes to make them available for type hints
from .utility_nodes import RetryNode
from .validation_nodes import ValidateAndAssembleNode

# Create name parsing agent
ollama_model = create_ollama_model()
name_agent = Agent(
    ollama_model,
    output_type=ParsedName,
    system_prompt="Parse voter name from the provided text...",
)


@dataclass
class ParseNameNode(BaseNode[VoterProcessingState]):
    """Parse voter name from raw record"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> ParseAddressNode | RetryNode:
        ctx.state.processing_stage = "parsing_name"

        try:
            # Extract name fields from raw record
            name_text = extract_name_text(ctx.state.raw_record)

            result = await name_agent.run(name_text)
            ctx.state.parsed_name = result.output
            ctx.state.confidence_scores["name"] = result.output.confidence

            print(
                f"✅ Parsed name: {result.output.first_name} {result.output.last_name}"
            )
            return ParseAddressNode()

        except Exception as e:
            error_msg = f"Name parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 3:
                return RetryNode("name_parsing")
            else:
                return ParseAddressNode()  # Continue with empty name


@dataclass
class ParseAddressNode(BaseNode[VoterProcessingState]):
    """Parse both mailing and residence addresses"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> ParseDistrictNode | RetryNode:
        ctx.state.processing_stage = "parsing_addresses"

        try:
            # Parse addresses using the address agent
            address_result = await parse_address_fields(ctx.state.raw_record)

            # Separate mailing vs residence addresses from results
            mailing_fields = [f for f in address_result.mailing_fields]
            residence_fields = [f for f in address_result.residence_fields]

            if mailing_fields:
                ctx.state.parsed_mailing_address = build_address_from_fields(
                    mailing_fields
                )
                ctx.state.confidence_scores["mailing_address"] = sum(
                    f.confidence for f in mailing_fields
                ) / len(mailing_fields)

            if residence_fields:
                ctx.state.parsed_residence_address = build_address_from_fields(
                    residence_fields
                )
                ctx.state.confidence_scores["residence_address"] = sum(
                    f.confidence for f in residence_fields
                ) / len(residence_fields)

            print(
                f"✅ Parsed addresses: Mailing={bool(mailing_fields)}, Residence={bool(residence_fields)}"
            )
            return ParseDistrictNode()

        except Exception as e:
            error_msg = f"Address parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 3:
                return RetryNode("address_parsing")
            else:
                return ParseDistrictNode()


@dataclass
class ParseDistrictNode(BaseNode[VoterProcessingState]):
    """Parse legislative districts"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> ParseElectionNode | RetryNode:
        ctx.state.processing_stage = "parsing_districts"

        try:
            district_result = await parse_district_fields(ctx.state.raw_record)
            ctx.state.parsed_districts = district_result.districts
            ctx.state.confidence_scores["districts"] = (
                sum(d.confidence for d in district_result.districts)
                / len(district_result.districts)
                if district_result.districts
                else 0.0
            )

            print(f"✅ Parsed {len(district_result.districts)} districts")
            return ParseElectionNode()

        except Exception as e:
            error_msg = f"District parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 3:
                return RetryNode("district_parsing")
            else:
                return ParseElectionNode()


@dataclass
class ParseElectionNode(BaseNode[VoterProcessingState]):
    """Parse election history"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> ValidateAndAssembleNode | RetryNode:
        ctx.state.processing_stage = "parsing_elections"

        try:
            election_result = await parse_election_fields(ctx.state.raw_record)
            ctx.state.parsed_elections = election_result.elections
            ctx.state.confidence_scores["elections"] = (
                sum(e.confidence for e in election_result.elections)
                / len(election_result.elections)
                if election_result.elections
                else 0.0
            )

            print(f"✅ Parsed {len(election_result.elections)} elections")
            return ValidateAndAssembleNode()

        except Exception as e:
            error_msg = f"Election parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 3:
                return RetryNode("election_parsing")
            else:
                return ValidateAndAssembleNode()
