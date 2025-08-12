"""
Main processing functions for voter records using the graph workflow.
"""

from pathlib import Path
from typing import Any, Dict, List

from pydantic_graph import End
from pydantic_graph.persistence.file import FileStatePersistence

from ..models import CompleteVoterRecord, VoterProcessingState
from ..nodes import ParseNameNode
from .factory import create_voter_processing_graph


async def process_individual_voter_record(
    record: Dict[str, Any], record_id: str
) -> CompleteVoterRecord:
    """Process a single voter record with state persistence"""

    # Create persistence for this specific record
    persistence_file = Path(f"voter_processing_{record_id}.json")
    persistence = FileStatePersistence(persistence_file)

    # Initialize state
    initial_state = VoterProcessingState(raw_record=record, record_id=record_id)

    print(f"🚀 Processing voter record {record_id}")

    # Create and run the graph with persistence
    graph = create_voter_processing_graph()
    result = await graph.run(
        ParseNameNode(), state=initial_state, persistence=persistence
    )

    # Clean up persistence file on success (optional)
    if persistence_file.exists():
        persistence_file.unlink()

    print(f"🎉 Completed processing record {record_id}")
    return result.output


async def process_voter_file_with_persistence(
    csv_records: List[Dict[str, Any]],
) -> List[CompleteVoterRecord]:
    """Process entire voter file with individual record persistence"""

    results = []

    for i, record in enumerate(csv_records):
        record_id = f"record_{i:06d}"

        try:
            # Each record gets its own persistent processing
            result = await process_individual_voter_record(record, record_id)
            results.append(result)

        except Exception as e:
            print(f"💥 Failed to process record {record_id}: {e}")
            # Record failure but continue with next record
            from ..models import create_failed_voter_record

            error_record = create_failed_voter_record(
                record_id=record_id,
                error_message=f"Graph execution failed: {str(e)}",
                original_record=record,
            )
            results.append(error_record)

    return results


async def resume_voter_record_processing(record_id: str) -> CompleteVoterRecord:
    """Resume processing of a voter record from persistence"""

    persistence_file = Path(f"voter_processing_{record_id}.json")
    if not persistence_file.exists():
        raise ValueError(f"No persistence file found for record {record_id}")

    persistence = FileStatePersistence(persistence_file)

    print(f"🔄 Resuming processing of record {record_id}")

    # Resume from persistence
    graph = create_voter_processing_graph()
    async with graph.iter_from_persistence(persistence) as run:
        async for node in run:
            if isinstance(node, End):
                print(f"🎉 Resumed processing completed for record {record_id}")
                break

    # Clean up
    if persistence_file.exists():
        persistence_file.unlink()

    return run.result.output
