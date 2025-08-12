"""
DEPRECATED: This file has been refactored into the new modular structure.

The functionality from this file has been split into multiple modules:
- Models: vep_ai_validation_tools.models
- Agents: vep_ai_validation_tools.agents
- Nodes: vep_ai_validation_tools.nodes
- Graph: vep_ai_validation_tools.graph

For the main processing function, use:
from vep_ai_validation_tools import process_voter_file_with_persistence

This file is kept for reference but should not be used in new code.
"""

from .agents import *
from .graph import *

# Re-export key functionality for backward compatibility
from .models import *
from .nodes import *

ollama_model = OpenAIModel(
    model_name="llama3.2",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1", api_key="ollama"),
    settings=ModelSettings(temperature=0.0, max_retries=3),
)


class ElectionType(str, Enum):
    GENERAL = "general"
    PRIMARY = "primary"
    PRIMARY_RUNOFF = "primary_runoff"
    GENERAL_RUNOFF = "general_runoff"
    SPECIAL = "special"
    MUNICIPAL = "municipal"
    SCHOOL = "school"
    LOCAL = "local"
    PRESIDENTIAL_PRIMARY = "presidential_primary"
    BOND = "bond"
    CONSTITUTIONAL = "constitutional"
    RECALL = "recall"
    UNKNOWN = "unknown"


class VotingMethod(str, Enum):
    EARLY = "early"
    ABSENTEE = "absentee"
    DAY_OF = "day_of"
    MAIL = "mail"
    PROVISIONAL = "provisional"
    UNKNOWN = "unknown"


class ElectionJurisdiction(str, Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    MUNICIPAL = "municipal"
    SCHOOL_DISTRICT = "school_district"
    SPECIAL_DISTRICT = "special_district"
    UNKNOWN = "unknown"


class DistrictLevel(str, Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    CITY = "city"
    COURT = "court"


class ParsedName(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    dob: date
    confidence: float
    raw_input: str


class ParsedPhone(BaseModel):
    phone_type: str
    phone_number: str
    confidence: float
    raw_input: str


class ParsedElectionParticipation(BaseModel):
    election_date: str
    election_type: str  # primary, general, special
    date_voted: Optional[date]
    method: Optional[str] = None  # early, absentee, day-of
    confidence: float
    raw_input: str


class ParsedDistrict(BaseModel):
    """Parsed legislative/administrative district information"""

    field_name: str = PydanticField(description="Original field name from source data")
    district_level: DistrictLevel = PydanticField(
        description="Level of government (federal, state, county, city, court)"
    )
    district_type: str = PydanticField(
        description="Type of district (congressional, senate, school, etc)"
    )
    district_number: Optional[str] = PydanticField(
        default=None, description="District number/identifier if present"
    )
    district_value: str = PydanticField(description="The actual value from the data")
    confidence: float = PydanticField(
        default=0.0, ge=0.0, le=1.0, description="Parsing confidence"
    )

    class Config:
        use_enum_values = True


class DistrictParsingResult(BaseModel):
    """Result of parsing all district fields from a record"""

    districts: List[ParsedDistrict] = PydanticField(default_factory=list)
    parsing_errors: List[str] = PydanticField(default_factory=list)
    total_fields_processed: int = 0
    successfully_parsed: int = 0


class ParsedElection(BaseModel):
    """Individual parsed election record"""

    field_name: str = PydanticField(description="Original field name from source")
    election_date: Optional[str] = PydanticField(
        default=None, description="Election date (YYYY-MM-DD if parseable)"
    )
    election_type: ElectionType = PydanticField(description="Type of election")
    election_year: Optional[int] = PydanticField(
        default=None, description="Election year"
    )
    participated: bool = PydanticField(description="Whether voter participated")
    voting_method: Optional[VotingMethod] = PydanticField(
        default=None, description="How they voted"
    )
    jurisdiction: Optional[ElectionJurisdiction] = PydanticField(
        default=None, description="Election jurisdiction"
    )
    raw_value: str = PydanticField(description="Original raw value from data")
    confidence: float = PydanticField(
        default=0.0, ge=0.0, le=1.0, description="Parsing confidence"
    )


class ElectionParsingResult(BaseModel):
    """Result of parsing all election fields from a record"""

    elections: List[ParsedElection] = PydanticField(default_factory=list)
    parsing_errors: List[str] = PydanticField(default_factory=list)
    total_fields_processed: int = 0
    successfully_parsed: int = 0
    election_years_found: List[int] = PydanticField(default_factory=list)


@dataclass
class VoterProcessingState:
    """State that flows through the graph as we process a voter record"""

    # Original record
    raw_record: Dict[str, Any]
    record_id: str

    # Parsed components (filled in by nodes)
    parsed_name: Optional[ParsedName] = None
    parsed_mailing_address: Optional[ParsedAddress] = None
    parsed_residence_address: Optional[ParsedAddress] = None
    parsed_districts: List[ParsedDistrict] = field(default_factory=list)
    parsed_elections: List[ParsedElection] = field(default_factory=list)

    # Processing metadata
    processing_errors: List[str] = field(default_factory=list)
    retry_count: int = 0
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    processing_stage: str = "starting"

    # Final assembled record
    final_voter_record: Optional[CompleteVoterRecord] = None


# Your existing agents
name_agent = Agent(ollama_model, output_type=ParsedName, system_prompt="...")
address_agent = Agent(
    ollama_model, output_type=AddressParsingResult, system_prompt="..."
)
district_agent = Agent(
    ollama_model, output_type=DistrictParsingResult, system_prompt="..."
)
election_agent = Agent(
    ollama_model, output_type=ElectionParsingResult, system_prompt="..."
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
            name_text = self._extract_name_text(ctx.state.raw_record)

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

    def _extract_name_text(self, record: Dict[str, Any]) -> str:
        # Extract name fields from various possible column names
        name_parts = []
        for field in [
            "first_name",
            "last_name",
            "middle_name",
            "name_first",
            "name_last",
        ]:
            if field in record and record[field]:
                name_parts.append(str(record[field]))
        return " ".join(name_parts)


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
        # Implementation depends on your review system
        # Could write to database, file, queue service, etc.
        pass


class CompleteVoterRecord(BaseModel):
    """Final assembled voter record with all parsed components"""

    # Record identification
    record_id: str = Field(description="Unique identifier for this voter record")
    original_record: Optional[Dict[str, Any]] = Field(
        default=None, description="Original raw CSV record"
    )

    # Parsed components
    name: Optional[ParsedName] = Field(default=None, description="Parsed voter name")
    mailing_address: Optional[ParsedAddress] = Field(
        default=None, description="Parsed mailing address"
    )
    residence_address: Optional[ParsedAddress] = Field(
        default=None, description="Parsed residence address"
    )
    districts: List[ParsedDistrict] = Field(
        default_factory=list, description="All parsed legislative districts"
    )
    elections: List[ParsedElection] = Field(
        default_factory=list, description="All parsed election participation"
    )

    # Quality metrics
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict, description="Confidence score per component"
    )
    overall_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall parsing confidence"
    )

    # Processing metadata
    processing_errors: List[str] = Field(
        default_factory=list, description="Errors encountered during processing"
    )
    processing_warnings: List[str] = Field(
        default_factory=list, description="Warnings during processing"
    )
    processing_timestamp: datetime = Field(
        default_factory=datetime.now, description="When record was processed"
    )
    processing_duration_seconds: Optional[float] = Field(
        default=None, description="How long processing took"
    )

    # Review flags
    needs_review: bool = Field(
        default=False, description="Whether record needs human review"
    )
    review_reasons: List[str] = Field(
        default_factory=list, description="Reasons why review is needed"
    )
    reviewed_by: Optional[str] = Field(
        default=None, description="Who reviewed this record"
    )
    review_timestamp: Optional[datetime] = Field(
        default=None, description="When record was reviewed"
    )
    review_notes: Optional[str] = Field(default=None, description="Review notes")

    # Computed properties
    @property
    def is_complete(self) -> bool:
        """Check if record has minimum required components"""
        return bool(
            self.name
            and (self.mailing_address or self.residence_address)
            and self.districts
        )

    @property
    def primary_address(self) -> Optional[ParsedAddress]:
        """Get the primary address (residence preferred, fallback to mailing)"""
        return self.residence_address or self.mailing_address

    @property
    def election_years(self) -> List[int]:
        """Get sorted list of election years voter participated in"""
        years = {
            e.election_year
            for e in self.elections
            if e.election_year and e.participated
        }
        return sorted(years, reverse=True)

    @property
    def latest_election_year(self) -> Optional[int]:
        """Get most recent election year voter participated in"""
        years = self.election_years
        return years[0] if years else None

    @property
    def district_summary(self) -> Dict[str, List[str]]:
        """Get summary of districts by level"""
        summary = {}
        for district in self.districts:
            level = district.district_level
            if level not in summary:
                summary[level] = []

            district_info = f"{district.district_type}"
            if district.district_number:
                district_info += f" {district.district_number}"
            summary[level].append(district_info)

        return summary

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for reporting"""
        return {
            "record_id": self.record_id,
            "name": (
                f"{self.name.first_name} {self.name.last_name}"
                if self.name
                else "UNKNOWN"
            ),
            "primary_address": (
                self.primary_address.normalized_address
                if self.primary_address
                else "UNKNOWN"
            ),
            "district_count": len(self.districts),
            "election_count": len([e for e in self.elections if e.participated]),
            "latest_election": self.latest_election_year,
            "overall_confidence": self.overall_confidence,
            "needs_review": self.needs_review,
            "is_complete": self.is_complete,
            "processing_errors": len(self.processing_errors),
        }


# Helper function to create a failed record
def create_failed_voter_record(
    record_id: str, error_message: str, original_record: Optional[Dict[str, Any]] = None
) -> CompleteVoterRecord:
    """Create a voter record representing a processing failure"""
    return CompleteVoterRecord(
        record_id=record_id,
        original_record=original_record,
        processing_errors=[error_message],
        needs_review=True,
        review_reasons=["Processing failed"],
        overall_confidence=0.0,
    )


# Helper function to create a partial record
def create_partial_voter_record(
    record_id: str,
    parsed_components: Dict[str, Any],
    errors: List[str] = None,
    confidence_scores: Dict[str, float] = None,
) -> CompleteVoterRecord:
    """Create a voter record from partially parsed components"""

    return CompleteVoterRecord(
        record_id=record_id,
        name=parsed_components.get("name"),
        mailing_address=parsed_components.get("mailing_address"),
        residence_address=parsed_components.get("residence_address"),
        districts=parsed_components.get("districts", []),
        elections=parsed_components.get("elections", []),
        confidence_scores=confidence_scores or {},
        overall_confidence=(
            sum(confidence_scores.values()) / len(confidence_scores)
            if confidence_scores
            else 0.0
        ),
        processing_errors=errors or [],
        needs_review=bool(errors)
        or (
            confidence_scores
            and sum(confidence_scores.values()) / len(confidence_scores) < 0.7
        ),
    )


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


@election_parser_agent.output_validator
async def validate_election_parsing(
    ctx: RunContext, output: ElectionParsingResult
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
        raise ModelRetry(f"Too many election parsing errors: {errors[:3]}")

    return output


# Create the graph
voter_processing_graph = Graph(
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

    # Run the graph with persistence
    result = await voter_processing_graph.run(
        ParseNameNode(), state=initial_state, persistence=persistence
    )

    # Clean up persistence file on success (optional)
    if persistence_file.exists():
        persistence_file.unlink()

    print(f"🎉 Completed processing record {record_id}")
    return result.output


# Process multiple records with resumable execution
async def process_voter_file_with_persistence(csv_records: List[Dict[str, Any]]):
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
            error_record = CompleteVoterRecord(
                record_id=record_id,
                processing_errors=[f"Graph execution failed: {str(e)}"],
                needs_review=True,
            )
            results.append(error_record)

    return results


# For resumable processing of interrupted records
async def resume_voter_record_processing(record_id: str) -> CompleteVoterRecord:
    """Resume processing of a voter record from persistence"""

    persistence_file = Path(f"voter_processing_{record_id}.json")
    if not persistence_file.exists():
        raise ValueError(f"No persistence file found for record {record_id}")

    persistence = FileStatePersistence(persistence_file)

    print(f"🔄 Resuming processing of record {record_id}")

    # Resume from persistence
    async with voter_processing_graph.iter_from_persistence(persistence) as run:
        async for node in run:
            if isinstance(node, End):
                print(f"🎉 Resumed processing completed for record {record_id}")
                break

    # Clean up
    if persistence_file.exists():
        persistence_file.unlink()

    return run.result.output


# Usage example
if __name__ == "__main__":
    import asyncio

    import pandas as pd

    # Read CSV
    df = pd.read_csv("voter_file.csv")
    records = df.to_dict("records")

    # Process with persistence
    results = asyncio.run(process_voter_file_with_persistence(records))

    # Analysis
    successful = [r for r in results if not r.needs_review]
    needs_review = [r for r in results if r.needs_review]

    print(f"📊 Results: {len(successful)} successful, {len(needs_review)} need review")
