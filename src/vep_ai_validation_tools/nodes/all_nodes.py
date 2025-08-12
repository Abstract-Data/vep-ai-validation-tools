"""
All graph nodes defined in a single file to avoid circular import issues with pydantic-graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union

from pydantic_ai import Agent
from pydantic_graph import BaseNode, Edge, End, GraphRunContext

from ..agents import parse_address_fields, parse_district_fields, parse_election_fields
from ..agents.base import create_ollama_model
from ..models import CompleteVoterRecord, ParsedName, VoterProcessingState
from .base import build_address_from_fields, extract_name_text


@dataclass
class ParseNameNode(BaseNode[VoterProcessingState]):
    """Parse voter name from raw record"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> ParseAddressNode | RetryNode:
        ctx.state.processing_stage = "parsing_name"

        try:
            # Check if name is already structured
            if "person_name" in ctx.state.raw_record and isinstance(
                ctx.state.raw_record["person_name"], dict
            ):
                name_data = ctx.state.raw_record["person_name"]
                from datetime import datetime

                from ..models import ParsedName

                # Parse date of birth
                dob_str = name_data.get("dob", "")
                try:
                    dob = (
                        datetime.strptime(dob_str, "%Y-%m-%d").date()
                        if dob_str
                        else datetime.now().date()
                    )
                except:
                    dob = datetime.now().date()

                ctx.state.parsed_name = ParsedName(
                    first_name=name_data.get("name_first", ""),
                    last_name=name_data.get("name_last", ""),
                    middle_name=name_data.get("name_middle"),
                    suffix=None,
                    dob=dob,
                    confidence=0.95,
                    raw_input=str(name_data),
                )
            else:
                # Extract name fields from raw record
                name_text = extract_name_text(ctx.state.raw_record)

                result = await name_agent.run(name_text)
                ctx.state.parsed_name = result.output

            ctx.state.confidence_scores["name"] = ctx.state.parsed_name.confidence

            print(
                f"✅ Parsed name: {ctx.state.parsed_name.first_name} {ctx.state.parsed_name.last_name}"
            )
            return ParseAddressNode()

        except Exception as e:
            error_msg = f"Name parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 1:
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
            # Skip AI agent for address parsing and use direct field mapping
            from ..models import ParsedAddress

            # Check for mailing address fields
            if (
                "mail_address1" in ctx.state.raw_record
                and ctx.state.raw_record["mail_address1"]
            ):
                ctx.state.parsed_mailing_address = ParsedAddress(
                    address1=ctx.state.raw_record.get("mail_address1", ""),
                    address2=ctx.state.raw_record.get("mail_address2", ""),
                    city=ctx.state.raw_record.get("mail_city", ""),
                    state=ctx.state.raw_record.get("mail_state", ""),
                    zip5=ctx.state.raw_record.get("mail_zip5", ""),
                    zip4=ctx.state.raw_record.get("mail_zip4", ""),
                    confidence=0.9,
                    raw_input=str(
                        {
                            k: v
                            for k, v in ctx.state.raw_record.items()
                            if k.startswith("mail_") and v
                        }
                    ),
                )
                ctx.state.confidence_scores["mailing_address"] = 0.9

            # Check for residence address fields
            if (
                "residence_address1" in ctx.state.raw_record
                and ctx.state.raw_record["residence_address1"]
            ):
                ctx.state.parsed_residence_address = ParsedAddress(
                    address1=ctx.state.raw_record.get("residence_address1", ""),
                    address2=ctx.state.raw_record.get("residence_address2", ""),
                    city=ctx.state.raw_record.get("residence_city", ""),
                    state=ctx.state.raw_record.get("residence_state", ""),
                    zip5=ctx.state.raw_record.get("residence_zip5", ""),
                    zip4=ctx.state.raw_record.get("residence_zip4", ""),
                    confidence=0.9,
                    raw_input=str(
                        {
                            k: v
                            for k, v in ctx.state.raw_record.items()
                            if k.startswith("residence_") and v
                        }
                    ),
                )
                ctx.state.confidence_scores["residence_address"] = 0.9

            print(
                f"✅ Parsed addresses: Mailing={bool(ctx.state.parsed_mailing_address)}, Residence={bool(ctx.state.parsed_residence_address)}"
            )
            return ParseDistrictNode()

        except Exception as e:
            error_msg = f"Address parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 1:
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

            if ctx.state.retry_count < 1:
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
            # Skip election parsing for Texas data - no election fields present
            ctx.state.parsed_elections = []
            ctx.state.confidence_scores["elections"] = (
                1.0  # High confidence that there are no elections
            )
            print(
                f"✅ Skipping election parsing - no election data in Texas voter file"
            )

            return ValidateAndAssembleNode()

        except Exception as e:
            error_msg = f"Election parsing failed: {str(e)}"
            ctx.state.processing_errors.append(error_msg)
            print(f"❌ {error_msg}")

            if ctx.state.retry_count < 3:
                return RetryNode("election_parsing")
            else:
                return ValidateAndAssembleNode()


@dataclass
class RetryNode(BaseNode[VoterProcessingState]):
    """Handle retries for failed parsing steps"""

    stage: str

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> ParseNameNode | ParseAddressNode | ParseDistrictNode | ParseElectionNode:
        ctx.state.retry_count += 1
        print(f"🔄 Retrying {self.stage} (attempt {ctx.state.retry_count})")

        # Return to appropriate node based on stage
        if self.stage == "name_parsing":
            return ParseNameNode()
        elif self.stage == "address_parsing":
            return ParseAddressNode()
        elif self.stage == "district_parsing":
            return ParseDistrictNode()
        else:  # election_parsing
            return ParseElectionNode()


@dataclass
class ValidateAndAssembleNode(
    BaseNode[VoterProcessingState, None, CompleteVoterRecord]
):
    """Validate all parsed data and assemble final record"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> End[CompleteVoterRecord] | QueueForReviewNode:
        ctx.state.processing_stage = "validating_and_assembling"

        # Calculate overall confidence
        overall_confidence = (
            sum(ctx.state.confidence_scores.values()) / len(ctx.state.confidence_scores)
            if ctx.state.confidence_scores
            else 0.0
        )

        # Determine review reasons
        review_reasons = []
        if overall_confidence < 0.7:
            review_reasons.append(f"Low overall confidence: {overall_confidence:.2f}")
        if len(ctx.state.processing_errors) > 2:
            review_reasons.append(
                f"Multiple processing errors: {len(ctx.state.processing_errors)}"
            )
        if not ctx.state.parsed_name:
            review_reasons.append("Missing name information")
        if (
            not ctx.state.parsed_mailing_address
            and not ctx.state.parsed_residence_address
        ):
            review_reasons.append("Missing address information")
        if not ctx.state.parsed_districts:
            review_reasons.append("Missing district information")

        # Build final record
        final_record = CompleteVoterRecord(
            record_id=ctx.state.record_id,
            original_record=ctx.state.raw_record,
            name=ctx.state.parsed_name,
            mailing_address=ctx.state.parsed_mailing_address,
            residence_address=ctx.state.parsed_residence_address,
            districts=ctx.state.parsed_districts,
            elections=ctx.state.parsed_elections,
            confidence_scores=ctx.state.confidence_scores,
            overall_confidence=overall_confidence,
            processing_errors=ctx.state.processing_errors,
            needs_review=bool(review_reasons),
            review_reasons=review_reasons,
            processing_timestamp=datetime.now(),
        )

        ctx.state.final_voter_record = final_record

        # Decide if needs human review
        if final_record.needs_review:
            print(f"⚠️  Record {ctx.state.record_id} queued for review")
            print(f"    Reasons: {', '.join(review_reasons)}")
            return QueueForReviewNode()
        else:
            print(f"✅ Record {ctx.state.record_id} completed successfully")
            print(f"    Confidence: {overall_confidence:.2f}")
            return End(final_record)


@dataclass
class QueueForReviewNode(BaseNode[VoterProcessingState, None, CompleteVoterRecord]):
    """Queue record for human review"""

    async def run(
        self, ctx: GraphRunContext[VoterProcessingState]
    ) -> End[CompleteVoterRecord]:
        # Add to review queue (could be database, file, etc.)
        await self._queue_for_human_review(ctx.state.final_voter_record)

        print(f"📋 Record {ctx.state.record_id} queued for human review")
        return End(ctx.state.final_voter_record)

    async def _queue_for_human_review(self, record: CompleteVoterRecord):
        """Implementation depends on your review system"""
        # Could write to database, file, queue service, etc.
        pass


# Create the name parsing agent
ollama_model = create_ollama_model()
name_agent = Agent(
    ollama_model,
    output_type=ParsedName,
    system_prompt="Parse voter name information from text. Extract first name, last name, middle name, and any suffixes.",
)
