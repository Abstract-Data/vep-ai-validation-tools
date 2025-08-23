from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import logfire
import toml
import tomli
from pydantic import AliasChoices, BaseModel, ConfigDict
from pydantic import Field as PydanticField
from pydantic import create_model, model_validator
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.settings import ModelSettings

from ..agents.base import OllamaProvider
from . import DATA_PATH
from .renaming_funcs import AgenticValidationFuncs as AVF

STATE_FIELDS = DATA_PATH / "state_voterfiles"
FIELD_DEFINITION_TOML = DATA_PATH / "field_definitions.toml"
FIELD_CRITERIA_TOML = DATA_PATH / "field_criteria.toml"
FIELD_REFERENCE_INFO_TOML = DATA_PATH / "field_reference_info.toml"


class FieldReferenceInfo(BaseModel):
    field_name: str = PydanticField(description="The name of the field")
    field_description: str = PydanticField(
        description="The description of the field", max_length=200
    )
    field_possible_values: list[str] = PydanticField(
        default_factory=list, description="The possible values for the field"
    )


class FieldDefinitionCreator:
    @staticmethod
    def create_fallback_definition(key: str, values: list[Any]) -> FieldReferenceInfo:
        """Create a basic field definition when AI processing fails."""
        return FieldReferenceInfo(
            field_name=key,
            field_description=f"DESCRIPTION NEEDED FOR{key}",
            field_possible_values=list(
                set(
                    [str(v) for v in values]
                    if isinstance(values, list)
                    else str(values)
                )
            ),
        )


ollama_model = OpenAIModel(
    model_name="llama3.2",
    provider=OllamaProvider(base_url="http://localhost:11434/v1"),
    settings=ModelSettings(temperature=0.1, max_retries=5),
)
rename_agent = Agent(
    ollama_model,
    output_type=FieldReferenceInfo,
    system_prompt="""
    Analyze the field name and values to provide a concise, direct description.
    Write a single sentence (max 200 characters) that clearly identifies what this field contains.
    Do not use phrases like 'The field represents', 'Here is a description', or 'This field contains'.
    Instead, directly describe the content. For example: 'Voter identification number' instead of 'The field represents the voter identification number'.
    Use the field name for context to help create an accurate description for the field level (like state, county, city, etc.)

    Return a FieldReferenceInfo object with:
    - field_name: the original field name
    - field_description: a concise description of what this field contains
    - field_possible_values: list of possible values for this field""",
)


class FieldManager:
    def __init__(self):
        self.old_field_definitions = self.load_existing_field_definitions()
        _, self.new_field_definitions = self.load_new_field_references(
            self.old_field_definitions
        )

        # Convert FieldReferenceInfo objects to a format that update_description_toml can handle
        new_field_map = {}
        for field_name, field_info in self.new_field_definitions.items():
            if isinstance(field_info, FieldReferenceInfo):
                new_field_map[field_name] = field_info.field_description
            else:
                new_field_map[field_name] = str(field_info)
        self.update_description_toml(new_field_map, self.old_field_definitions)
        self.loaded_references = self.load_field_reference_info_from_toml()
        self.field_mappings = self.create_field_mappings_safe()
        self.rename_model = None

    @classmethod
    def load_existing_field_definitions(cls, folder: Path = DATA_PATH):
        """Load existing field definitions from TOML files."""
        if not folder.exists():
            return {}
        _file = folder / "field_definitions.toml"
        if not _file.exists():
            _file = DATA_PATH / "field_definitions.toml"
            _file.touch()
        with open(_file, "rb") as f:
            return tomli.load(f) or {}

    @classmethod
    def load_new_field_references(
        cls, field_definition_toml: dict, folder: Path = STATE_FIELDS
    ) -> tuple[dict[str, list], dict[str, FieldReferenceInfo]]:
        """Safely load field references with comprehensive error handling."""
        FIELD_DICT = {}

        if not folder.exists():
            logfire.warning(f"Warning: Folder {folder} does not exist")
            return {}, {}

        # Load TOML files
        for file in folder.glob("*.toml"):
            # if file.name == 'field_definitions.toml':
            #     continue
            try:
                with open(file, "rb") as f:
                    file_data = tomli.load(f)
                for k, v in file_data.items():
                    if k not in FIELD_DICT:
                        FIELD_DICT[k] = []

                    # Clean the data to prevent recursive serialization
                    if isinstance(v, list):
                        cleaned_values = []
                        for item in v:
                            # Skip items that look like serialized FieldReferenceInfo objects
                            if isinstance(item, str) and (
                                "field_name" in item and "description" in item
                            ):
                                continue
                            cleaned_values.append(item)
                        FIELD_DICT[k].extend(cleaned_values)
                    else:
                        # Skip values that look like serialized FieldReferenceInfo objects
                        if not (
                            isinstance(v, str)
                            and ("field_name" in v and "description" in v)
                        ):
                            FIELD_DICT[k].append(v)

                    FIELD_DICT[k] = list(set(FIELD_DICT[k]))
            except Exception as e:
                logfire.error(f"Error loading {file}: {e}")
                continue

        # Clean FIELD_DICT to ensure it's TOML serializable
        clean_field_dict = {}
        for k, v in FIELD_DICT.items():
            if isinstance(v, list):
                # Convert all values to strings to ensure serializability
                clean_field_dict[k] = [str(item) for item in v]
            else:
                clean_field_dict[k] = [str(v)]

        with open(FIELD_CRITERIA_TOML, "w") as f:
            toml.dump(clean_field_dict, f)

            # NewAIModel(
            #     ModelComponents()
            #     )
            #     .create_agent(
            #         system_prompt="""
            #         Analyze the field name and values to provide a concise, direct description.
            #         Write a single sentence (max 200 characters) that clearly identifies what this field contains.
            #         Do not use phrases like 'The field represents', 'Here is a description', or 'This field contains'.
            #         Instead, directly describe the content. For example: 'Voter identification number' instead of 'The field represents the voter identification number'.
            #         Use the {key} for context to help create an accurate description for the field level (like state, county, city, etc.)""",
            #     )
            # )
        DEFINITIONS = {}
        with logfire.span("Creating AI definitions"):
            for k, v in FIELD_DICT.items():
                if k not in field_definition_toml:
                    if rename_agent:
                        try:
                            result = rename_agent.run_sync(f"Key: {k}, Values: {v}")
                            # The agent should return a FieldReferenceInfo object
                            if hasattr(result.output, "field_description"):
                                DEFINITIONS[k] = result.output
                                field_definition_toml[k] = (
                                    result.output.field_description
                                )
                            else:
                                # Fallback if the agent didn't return the expected structure
                                DEFINITIONS[k] = FieldReferenceInfo(
                                    field_name=k,
                                    field_description=str(result.output),
                                    field_possible_values=(
                                        [str(val) for val in v]
                                        if isinstance(v, list)
                                        else [str(v)]
                                    ),
                                )
                                field_definition_toml[k] = DEFINITIONS[
                                    k
                                ].field_description
                            logfire.info(
                                f"AI definition for {k}: {DEFINITIONS[k].field_description}"
                            )
                        except Exception as e:
                            logfire.error(f"AI failed for {k}: {e}")
                            fallback = (
                                FieldDefinitionCreator.create_fallback_definition(k, v)
                            )
                            field_definition_toml[k] = fallback.field_description
                            DEFINITIONS[k] = fallback
                    else:
                        field_definition_toml[k] = (
                            FieldDefinitionCreator.create_fallback_definition(k, v)
                        )
                        DEFINITIONS[k] = field_definition_toml[k]
                else:
                    # Handle case where field_definition_toml[k] might be a string or FieldReferenceInfo
                    if isinstance(field_definition_toml[k], str):
                        DEFINITIONS[k] = FieldReferenceInfo(
                            field_name=k,
                            field_description=field_definition_toml[k],
                            field_possible_values=(
                                [str(val) for val in v]
                                if isinstance(v, list)
                                else [str(v)]
                            ),
                        )
                    elif isinstance(field_definition_toml[k], FieldReferenceInfo):
                        DEFINITIONS[k] = field_definition_toml[k]
                    else:
                        # Fallback for any other type
                        DEFINITIONS[k] = FieldReferenceInfo(
                            field_name=k,
                            field_description=str(field_definition_toml[k]),
                            field_possible_values=(
                                [str(val) for val in v]
                                if isinstance(v, list)
                                else [str(v)]
                            ),
                        )
            cls.dump_field_reference_info_to_toml(DEFINITIONS)

        return FIELD_DICT, DEFINITIONS

    @classmethod
    def update_description_toml(
        cls,
        new_field_map: dict[str, PydanticField],
        current_field_map: dict[str, str],
        folder: Path = DATA_PATH,
    ):
        """Update the field definitions TOML file with new field descriptions."""
        _file = folder / FIELD_DEFINITION_TOML.name
        for k in current_field_map.keys():
            if k not in new_field_map.keys():
                if isinstance(current_field_map[k], str):
                    _description = current_field_map[k]
                elif isinstance(current_field_map[k], FieldReferenceInfo):
                    _description = current_field_map[k].field_description
                else:
                    _description = current_field_map[k]
                new_field_map[k] = _description
        with open(_file, "w") as f:
            new_field_map.pop("properties", None)
            logfire.info(f"Updating: {new_field_map}")
            toml.dump(dict(sorted(new_field_map.items())), f)
            logfire.info(f"Updated {_file}")

    @classmethod
    def dump_field_reference_info_to_toml(
        cls,
        field_definitions: dict[str, FieldReferenceInfo],
        output_file: Path | None = None,
        folder: Path = DATA_PATH,
    ):
        """Dump FieldReferenceInfo models to a TOML file."""
        if output_file is None:
            output_file = folder / FIELD_REFERENCE_INFO_TOML.name
            logfire.info(
                f"No output file provided, using default location: {output_file}"
            )
        else:
            output_file = Path(output_file)
            logfire.info(f"Output file provided: {output_file}")

        # Convert FieldReferenceInfo objects to TOML-compatible dictionary
        toml_data = {}

        for field_name, field_info in field_definitions.items():
            if isinstance(field_info, FieldReferenceInfo):
                toml_data[field_name] = {
                    "field_name": field_info.field_name,
                    "description": field_info.field_description,
                    "possible_values": field_info.field_possible_values,
                }
            else:
                # Handle case where field_info might be a string or other type
                toml_data[field_name] = {
                    "field_name": field_name,
                    "description": (
                        str(field_info) if field_info else f"Field for {field_name}"
                    ),
                    "possible_values": [],
                }

        # Ensure the output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to TOML file
        with open(output_file, "w") as f:
            sorted_data = dict(sorted(toml_data.items(), key=lambda x: x[0]))
            toml.dump(sorted_data, f)

        logfire.info(f"✓ Dumped {len(toml_data)} field definitions to {output_file}")
        return output_file

    @classmethod
    def load_field_reference_info_from_toml(
        cls, input_file: Path | None = None, folder: Path = DATA_PATH
    ) -> dict[str, FieldReferenceInfo]:
        """Load FieldReferenceInfo models from a TOML file."""
        if input_file is None:
            input_file = folder / FIELD_REFERENCE_INFO_TOML.name

        if not input_file.exists():
            logfire.warning(f"File {input_file} does not exist")
            return {}

        # Read TOML file
        with open(input_file, "rb") as f:
            toml_data = tomli.load(f)

        # Convert TOML data back to FieldReferenceInfo objects
        field_definitions = {}

        for field_name, field_data in toml_data.items():
            if isinstance(field_data, dict):
                field_definitions[field_name] = FieldReferenceInfo(
                    field_name=field_name,
                    field_description=field_data.get(
                        "description", f"Field for {field_name}"
                    ),
                    field_possible_values=field_data.get("possible_values", []),
                )
            else:
                # Handle case where field_data might be a string
                field_definitions[field_name] = FieldReferenceInfo(
                    field_name=field_name,
                    field_description=(
                        str(field_data) if field_data else f"Field for {field_name}"
                    ),
                    field_possible_values=[],
                )

        logfire.info(
            f"✓ Loaded {len(field_definitions)} field definitions from {input_file}"
        )
        return field_definitions

    def create_field_mappings_safe(self) -> dict[str, Any]:
        """Create field mappings for Pydantic model generation with error handling."""
        field_definitions = self.loaded_references

        field_mappings = {}

        for field_name, field_info in field_definitions.items():
            try:
                # Ensure field_info is a FieldReferenceInfo object
                if not isinstance(field_info, FieldReferenceInfo):
                    warning = f"Field info for {field_name} is not a FieldReferenceInfo object, creating fallback"
                    logfire.warning(warning)
                    raise ValueError(warning)

                field_mappings[field_info.field_name] = (
                    Optional[str],
                    PydanticField(
                        alias=AliasChoices(*field_info.field_possible_values),
                        description=field_info.field_description,
                        default=None,
                    ),
                )
            except Exception as e:
                logfire.error(f"Error creating field mapping for {field_name}: {e}")
                # Create basic field without alias
                field_mappings[field_name] = (
                    Optional[str],
                    PydanticField(
                        description=(
                            str(field_info)
                            if field_info
                            else f"DESCRIPTION NEEDED FOR {field_name}"
                        ),
                        default=None,
                    ),
                )

        return field_mappings

    def create_rename_model_safe(self):
        """Create the final RenameModel with comprehensive error handling."""
        try:

            if not self.field_mappings:
                logfire.warning("No field mappings found. Creating empty model.")
                raise ValueError("No field mappings found.")

            # Use create_model with extra='allow' to keep all fields in the main model
            config = ConfigDict(str_strip_whitespace=True, extra="allow")

            RenameModel = create_model(
                "RenameModel",
                __config__=config,
                __validators__=AVF.get_validators(),
                districts=(
                    list,
                    PydanticField(
                        default_factory=list, description="List of districts"
                    ),
                ),
                voter_registration=(
                    dict,
                    PydanticField(
                        default_factory=dict, description="Voter registration details"
                    ),
                ),
                phone=(
                    Optional[list],
                    PydanticField(default=None, description="List of phone numbers"),
                ),
                data_source=(
                    Optional[list],
                    PydanticField(default=None, description="List of data sources"),
                ),
                person_name=(
                    Optional[dict],
                    PydanticField(default=None, description="Person name details"),
                ),
                address_list=(
                    list,
                    PydanticField(
                        default_factory=list, description="List of address details"
                    ),
                ),
                **self.field_mappings,
            )

            logfire.info(
                f"✓ Created RenameModel with {len(self.field_mappings)} fields"
            )
            self.rename_model = RenameModel
            return self.rename_model

        except Exception as e:
            logfire.error(f"✗ Error creating RenameModel: {e}")
            return create_model("RenameModel")
