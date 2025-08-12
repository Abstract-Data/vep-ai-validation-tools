"""
Factory for creating voter processing graphs and components.
"""

from pydantic_graph import Graph

from ..models import VoterProcessingState
from ..nodes.all_nodes import (
    ParseAddressNode,
    ParseDistrictNode,
    ParseElectionNode,
    ParseNameNode,
    QueueForReviewNode,
    RetryNode,
    ValidateAndAssembleNode,
)


def create_voter_processing_graph() -> Graph:
    """Factory function to create the voter processing graph"""
    return Graph(
        nodes=[
            ParseNameNode,
            ParseAddressNode,
            ParseDistrictNode,
            ParseElectionNode,
            ValidateAndAssembleNode,
            RetryNode,
            QueueForReviewNode,
        ],
        state_type=VoterProcessingState,
    )
