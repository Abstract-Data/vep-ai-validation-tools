from csv import DictReader
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import phonenumbers
from icecream import ic
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic_ai import Agent
from pydantic_core import PydanticCustomError
from tqdm import tqdm

from vep_ai_validation_tools.agents import create_ollama_model
from vep_ai_validation_tools.renaming import DATA_PATH
from vep_ai_validation_tools.renaming.toml_reader import TomlReader
from vep_ai_validation_tools.renaming.validation_cls import ValidationClass

# from vep_validation_tools.agentic.ai_utils import NewAIModel, DataQualityAssessment, ModelComponents

# TODO: Figure out how to ge the fields to quit overwriting validation dumps, specifically on contact phone fields.
# STATE_VOTERFILES = [
#     Path("/Users/johneakin/PyCharmProjects/state-voterfiles/data"),
#     Path(
#         "/Users/johneakin/PyCharmProjects/vep-2024/data/voterfiles/texas/texasnovember2024.csv"
#     ),
# ]

# ALL_VOTERFILES = []
# for vf_file in STATE_VOTERFILES:
#     p = Path(vf_file)
#     if p.is_file() and p.suffix == ".csv":
#         ALL_VOTERFILES.append(p)
#     elif p.is_dir():
#         # Recursively find all .csv files at any depth under this folder
#         ALL_VOTERFILES.extend(p.rglob("*.csv"))

# file_headers = dict()
# for file in ALL_VOTERFILES:
#     file_headers[file.name] = dict()
#     with file.open("r", encoding="utf-8-sig") as f:
#         reader = DictReader(f)
#         for row in tqdm(reader, desc=f"Processing {file.name}"):
#             for key, value in row.items():
#                 if not file_headers[file.name].get(key):
#                     file_headers[file.name][key] = set(value)
#                 if len(file_headers[file.name].get(key)) < 10:
#                     file_headers[file.name][key].add(value)

# combined_headers = dict()
# for file in file_headers:
#     combined_headers


# ollama_model = create_ollama_model()
# column_guesser_agent = Agent(
#     ollama_model,
#     output_type=dict,
#     system_prompt="""
#     You are a column guesser for state voter registration files. You will receive a list of column names and a list of values.
#     You will need to guess the column name based on the values. As a dictionary, return the column name as the key and the values as the value.
#     """)


@pydantic_dataclass
class AgenticValidationFuncs(ValidationClass):
    config = TomlReader(DATA_PATH / "address-config.toml").data

    def __init__(self):
        super().__init__()

    @classmethod
    def _log_field_edit(cls, message: str) -> None:
        """Helper function to log field edits consistently."""
        cls.EDIT_LOG[message] = cls.EDIT_LOG.get(message, 0) + 1

    # @staticmethod
    # def _create_address_list(data: BaseModel) -> BaseModel:
    #     """
    #     Create address lines from address parts in the data model.

    #     This function takes a Pydantic model and creates formatted address lines
    #     from individual address components.
    #     """

    #     _config = AgenticValidationFuncs.config

    #     # Initialize address_list if it's None
    #     if not hasattr(data, 'address_list') or data.address_list is None:
    #         data.address_list = []

    #     _data = data.model_dump()
    #     _address_list = []
    #     for address_type in _config['ADDRESS_TYPES']:
    #         _address_dict = AddressValidationFuncs.create_address_dict(_data, address_type)
    #         if not _address_dict:
    #             continue

    #         # _address_dict['std'] = _std

    #         # _address_dict['address_type'] = address_type
    #         data.address_list.append(_address_dict)
    #     return data

    @staticmethod
    def _strip_whitespace(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strip whitespace from string values in a dictionary.
        Returns None for empty strings after stripping.
        """
        return {
            k: None if isinstance(v, str) and v.strip() == "" else v
            for k, v in data.items()
        }

    @staticmethod
    def _format_date(v: Optional[str]) -> Optional[str]:
        """
        Format a date string to ISO format (YYYY-MM-DD).
        Supports multiple input formats: YYYY-MM-DD, MM/DD/YYYY, MM/DD/YY
        """
        if not v:
            return v
        if len(v) == 1:
            return None

        for fmt in AgenticValidationFuncs.config["DATE_FORMATS"]:
            try:
                parsed_date = datetime.strptime(v, fmt).date()
                formatted_date = str(parsed_date)
                AgenticValidationFuncs._log_field_edit(
                    f"Formatted date: {v} -> {formatted_date}"
                )
                return formatted_date
            except ValueError:
                continue

        raise PydanticCustomError(
            f"func:_format_date({v})",
            "Supported formats: YYYY-MM-DD, MM/DD/YYYY, MM/DD/YY",
        )

    @staticmethod
    def _replace_name_punctuation(v: Optional[str]) -> Optional[str]:
        """
        Remove punctuation from name fields.
        Currently removes periods, but can be extended for other punctuation.
        """
        if not v:
            return v

        if "." in v:
            cleaned_name = v.replace(".", "")
            AgenticValidationFuncs._log_field_edit(
                f"Removed punctuation from name: {v} -> {cleaned_name}"
            )
            return cleaned_name

        return v

    @staticmethod
    def _sort_districts(data: Any) -> Any:

        _data = data.model_dump()
        _district_levels = {
            (key.replace("district_", "").split("_")[0])
            for key, value in _data.items()
            if key.startswith("district") and value
        }
        for level in _district_levels:
            _details = [
                {
                    "district_level": level,
                    "district_name": k.replace(f"district_{level}_", "").strip(),
                    "district_number": v,
                }
                for k, v in _data.items()
                if k.startswith(f"district_{level}") and v
            ]
            data.districts.extend(_details)

        return data

    @staticmethod
    def _voter_registration_details(data: Any) -> Any:
        _data = data.model_dump()
        _reg_details = {
            k.replace("voter_", ""): v
            for k, v in _data.items()
            if k.startswith("voter_") and v
        }
        for k, v in _reg_details.items():
            if k == "voter_profile":
                _political_tags = {
                    k.replace("voter_profile_", "").strip(): v
                    for k, v in _data.items()
                    if k.startswith("voter_profile_") and v
                }
                if _political_tags:
                    _reg_details["attributes"] = {"political_tags": _political_tags}
        data.voter_registration = _reg_details
        return data

    @staticmethod
    def _set_person_name(data: Any) -> Dict[str, Any]:
        _data = data.model_dump()
        _name_dict = {
            k.replace("person_", ""): v
            for k, v in _data.items()
            if k.startswith("person_") and v
        }
        data.person_name = _name_dict
        return data

    @staticmethod
    def _validate_phones(data: Any) -> Any:
        phone_list = []
        _data = data.model_dump()
        _phone_dict = {
            k.replace("contact_phone_", ""): v
            for k, v in _data.items()
            if k.startswith("contact_phone_") and v
        }

        if _phone_dict:
            _phone_types = {k.split("_")[0] for k in _phone_dict.keys()}
            phone_list = []

            for phone_type in _phone_types:
                _type_fields = {
                    k.replace(phone_type, "").strip(): v
                    for k, v in _phone_dict.items()
                    if k.startswith(phone_type) and v
                }

                full_phone = _type_fields.get("phone")
                phone_areacode = _type_fields.get("areacode")
                phone_number = _type_fields.get("number")

                if not full_phone:
                    continue

                parsed_phone, _ = phonenumbers.parse(full_phone, "US")
                full_phone = _phone_dict.get(f"{phone_type}_phone")
                phone_areacode = _phone_dict.get(f"{phone_type}_areacode")
                phone_number = _phone_dict.get(f"{phone_type}_number")

                # corrections = []

                if full_phone:
                    parsed_phone, _ = phonenumbers.parse(full_phone, "US")
                    if phonenumbers.is_valid_number(parsed_phone):
                        phone_data = phonenumbers.format_number(
                            parsed_phone, phonenumbers.PhoneNumberFormat.E164
                        )
                        phone_data["phone_type"] = phone_type
                        phone_data["reliability"] = _phone_dict.get(
                            f"{phone_type}_reliability"
                        )
                        phone_list.append(phone_data)

                if phone_areacode and phone_number:
                    if len(phone_areacode) == 3 and len(phone_number) == 7:
                        merged_number = f"{phone_areacode}{phone_number}"
                        parsed_merged, _ = phonenumbers.parse(merged_number, "US")

                        if phonenumbers.is_valid_number(parsed_merged):
                            formatted_merged = phonenumbers.format_number(
                                parsed_merged, phonenumbers.PhoneNumberFormat.E164
                            )
                            formatted_merged["phone_type"] = phone_type
                            formatted_merged["reliability"] = _phone_dict.get(
                                f"{phone_type}_reliability"
                            )

                            if not any(
                                p.phone == formatted_merged["phone"] for p in phone_list
                            ):
                                phone_list.append(formatted_merged)
            data.phone = phone_list
        return data

    @staticmethod
    def set_file_origin(data: Dict[str, Any]) -> Dict[str, Any]:
        if _file_origin := data.get("file_origin"):
            data["data_source"] = []
            data["data_source"].append({"file": _file_origin})
        return data

    @classmethod
    def get_validators(cls) -> Dict[str, Callable]:
        """
        Get a dictionary of validation functions wrapped with Pydantic decorators.
        These can be applied to Pydantic models for data validation and transformation.
        """
        try:
            _config = AgenticValidationFuncs.config
            return {
                "strip_whitespace": model_validator(mode="before")(
                    cls._strip_whitespace
                ),
                "set_file_origin": model_validator(mode="before")(cls.set_file_origin),
                # 'create_address_list': model_validator(mode='after')(cls._create_address_list),
                "format_date": field_validator(
                    *_config.get("DATE_COLUMNS", []), mode="after"
                )(cls._format_date),
                "replace_name_punctuation": field_validator(
                    *_config.get("NAME_COLUMNS", []), mode="after"
                )(cls._replace_name_punctuation),
                "sort_districts": model_validator(mode="after")(cls._sort_districts),
                "voter_registration_details": model_validator(mode="after")(
                    cls._voter_registration_details
                ),
                "validate_phones": model_validator(mode="after")(cls._validate_phones),
                "set_person_name": model_validator(mode="after")(cls._set_person_name),
            }
        except Exception as e:
            # Fallback to safe validators if config is missing
            print(f"Warning: Using fallback validators due to config error: {e}")
            return {
                "strip_whitespace": model_validator(mode="before")(
                    cls._strip_whitespace
                ),
                "set_file_origin": model_validator(mode="before")(cls.set_file_origin),
            }

    @classmethod
    def get_edit_log(cls) -> Dict[str, int]:
        """Get the current field edit log."""
        return cls.EDIT_LOG.copy()

    @classmethod
    def clear_edit_log(cls) -> None:
        """Clear the field edit log."""
        cls.EDIT_LOG.clear()
