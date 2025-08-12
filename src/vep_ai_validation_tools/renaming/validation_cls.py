from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass
class ValidationClass:
    EDIT_LOG: ClassVar[Dict[str, int]] = {}
