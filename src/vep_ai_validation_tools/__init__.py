"""
vep-ai-validation-tools - A Python package built with UV

A comprehensive toolkit for validating and processing voter registration data
using AI-powered parsing and validation workflows.
"""

__version__ = "0.1.0"
__author__ = "John R. Eakin"
__email__ = "dev@abstractdata.io"

import logfire

from .graph import (
    create_voter_processing_graph,
    process_individual_voter_record,
    process_voter_file_with_persistence,
    resume_voter_record_processing,
)

# Import main functionality
from .models import CompleteVoterRecord, VoterProcessingState

logfire.configure(service_name="vep-ai-validation-tools")
logfire.instrument_pydantic_ai()

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "VoterProcessingState",
    "CompleteVoterRecord",
    "create_voter_processing_graph",
    "process_individual_voter_record",
    "process_voter_file_with_persistence",
    "resume_voter_record_processing",
]
