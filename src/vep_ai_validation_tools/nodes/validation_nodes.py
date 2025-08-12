"""
Nodes responsible for validation and final assembly of voter records.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Union

from pydantic_graph import BaseNode, End, GraphRunContext

from ..models import CompleteVoterRecord, VoterProcessingState
from .utility_nodes import QueueForReviewNode


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
            from .utility_nodes import QueueForReviewNode

            return QueueForReviewNode()
        else:
            print(f"✅ Record {ctx.state.record_id} completed successfully")
            print(f"    Confidence: {overall_confidence:.2f}")
            return End(final_record)
