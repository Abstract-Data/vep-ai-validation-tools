"""
Utility nodes for retries, reviews, and other support functions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Union

from pydantic_graph import BaseNode, End, GraphRunContext

from ..models import CompleteVoterRecord, VoterProcessingState


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
            from .parsing_nodes import ParseNameNode

            return ParseNameNode()
        elif self.stage == "address_parsing":
            from .parsing_nodes import ParseAddressNode

            return ParseAddressNode()
        elif self.stage == "district_parsing":
            from .parsing_nodes import ParseDistrictNode

            return ParseDistrictNode()
        else:  # election_parsing
            from .parsing_nodes import ParseElectionNode

            return ParseElectionNode()


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
