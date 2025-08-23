from csv import DictReader
from itertools import chain
from pathlib import Path
from typing import List, Optional

import toml
from icecream import ic
from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField
from pydantic_ai import Agent, capture_run_messages
from sqlmodel import Field as SQLModelField
from sqlmodel import Session, SQLModel, create_engine
from tqdm import tqdm

from vep_ai_validation_tools.agents import create_ollama_model
from vep_ai_validation_tools.renaming import DATA_PATH
from vep_ai_validation_tools.renaming.renaming import FieldManager, FieldReferenceInfo
from vep_ai_validation_tools.renaming.toml_reader import TomlReader
from vep_ai_validation_tools.renaming.validation_cls import ValidationClass

fields = FieldManager()
RenameModel = fields.create_rename_model_safe()
EXISTING_FIELD_DEFINITIONS = list(
    set(
        chain.from_iterable(
            v.field_possible_values for v in list(fields.new_field_definitions.values())
        )
    )
)
EXISTING_FIELD_JSON = [
    v.model_dump_json(indent=4) for v in list(fields.new_field_definitions.values())
]


class DataBaseFieldAlias(SQLModel, table=True):
    __tablename__ = "field_table"
    id: Optional[int] = SQLModelField(default=None, primary_key=True)
    field_name: str = SQLModelField(index=True, description="The name of the field")
    field_alias: str = SQLModelField(index=True, description="The alias of the field")
    field_description: Optional[str] = SQLModelField(
        default=None, description="The description of the field"
    )


canon_fields = []
for field in fields.new_field_definitions.values():
    for alias in field.field_possible_values:
        canon_fields.append(
            DataBaseFieldAlias(
                field_name=field.field_name,
                field_alias=alias,
                field_description=field.field_description,
            )
        )

# engine = create_engine("postgresql://postgres:postgres@localhost:5432/voterfiles")
# SQLModel.metadata.create_all(engine)
# with Session(engine) as session:
#     session.add_all(canon_fields)
#     session.commit()
FIELD_GUESSER_PROMPT = (
    (Path(__file__).parents[1] / "prompts" / "renaming_column_guesser.md")
    .read_text()
    .replace("<< field_reference_json >>", "\n".join(EXISTING_FIELD_JSON))
)

STATE_VOTERFILES = [
    Path("/Users/johneakin/PyCharmProjects/state-voterfiles/data"),
    Path(
        "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
    ),
]

ALL_VOTERFILES = []
for vf_file in STATE_VOTERFILES:
    p = Path(vf_file)
    if p.is_file() and p.suffix == ".csv":
        ALL_VOTERFILES.append(p)
    elif p.is_dir():
        # Recursively find all .csv files at any depth under this folder
        ALL_VOTERFILES.extend(p.rglob("*.csv"))

file_headers = dict()
for file in ALL_VOTERFILES:
    file_headers[file.name] = dict()
    with file.open("r", encoding="utf-8-sig") as f:
        reader = DictReader(f)
        row_count = 0
        for row in tqdm(reader, desc=f"Processing {file.name}"):
            if row_count == 100:
                break
            for key, value in row.items():
                if not file_headers[file.name].get(key):
                    file_headers[file.name][key] = set(value)
                elif len(file_headers[file.name].get(key)) < 50:
                    file_headers[file.name][key].add(value)
                else:
                    pass
            row_count += 1

unified_key_example_values = dict()
for file in file_headers:
    for key in file_headers[file]:
        if not unified_key_example_values.get(key):
            unified_key_example_values[key] = set()
        unified_key_example_values[key].update(file_headers[file][key])


# combined_headers = set()
# for file in file_headers:
#     combined_headers.update(file_headers[file])
class MissingFieldDefinition(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    internal_field: Optional[str] = PydanticField(
        default="", description="The internal field name of the missing field"
    )
    field_name: str = PydanticField(description="The name of the missing field")
    example_values: List[str] = PydanticField(
        description="Example values found in the data for this field"
    )


missing_definitions = [
    MissingFieldDefinition(field_name=k, example_values=list(filter(None, v))[:10])
    for k, v in unified_key_example_values.items()
    if k not in EXISTING_FIELD_DEFINITIONS and v
]

with open(DATA_PATH / "missing_field_definitions.toml", "w") as f:
    toml.dump({x.field_name: x.model_dump() for x in missing_definitions}, f)

    # TODO: Add function to figure out definitions from data for missing definitions.
    # TODO: Consider Browser-use to figure out definitions by searching for definitions from SoS sites, etc.


class ColumnSuggestion(BaseModel):
    input_header: str = PydanticField(
        description="The original input column header being analyzed"
    )
    field_name: str = PydanticField(
        description="The suggested/matching standardized field name"
    )
    field_description: str = PydanticField(
        description="The description of the field", max_length=200
    )
    field_possible_values: List[str] = PydanticField(
        description="The possible values for the field"
    )
    confidence: float = PydanticField(
        description="The confidence in the suggestion", ge=0, le=1
    )


# class PredictedColumnList(BaseModel):
#     suggestions: List[ColumnSuggestion] = PydanticField(description="The list of column suggestions")

# ic(PredictedColumnList.model_json_schema())

# ollama_model = create_ollama_model(model_name="mistral-small3.2")
# column_guesser_agent = Agent(
#     ollama_model,
#     output_type=ColumnSuggestion,
#     system_prompt=FIELD_GUESSER_PROMPT)

# suggestions = []
# with capture_run_messages() as messages:
#     for i in missing_definitions:
#         demo_data = unified_key_example_values[i]
#         try:
#             # Make the prompt much more explicit about analyzing the header name
#             prompt = f"""
# ANALYZE THIS HEADER: "{i}"

# Step 1: What does this header name mean?
# - "MZIPCD" = Mailing ZIP Code (M = Mailing, ZIPCD = ZIP Code)
# - "FNAME" = First Name
# - "VTRID" = Voter ID
# - "RA_CITY" = Residence Address City

# Step 2: What field type should this be?
# - If it's "MZIPCD" → mail_zip5 (mailing zip code)
# - If it's "FNAME" → person_name_first (first name)
# - If it's "VTRID" → voter_vuid (voter ID)

# Step 3: Example data: {", ".join(list(demo_data)[:10])}

# Now return a ColumnSuggestion for header "{i}":
# """
#             result = column_guesser_agent.run_sync(prompt)
#             ic(f"Success for {i}:")
#             ic(result.output)
#             suggestions.append(result.output)
#         except Exception as e:
#             ic(f"Error processing {i}:")
#             ic(e)
#             ic("Last message content:")
#             ic(messages)
#             # Continue with next item instead of raising
#             continue


# TODO: Figure out how to get the agent to return a list of suggestions.
