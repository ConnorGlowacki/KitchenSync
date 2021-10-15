from dataclasses import dataclass
from enum import Enum
from typing import List
from uuid import UUID

@dataclass
class Ingredient:
    name: str
    amount: float
    uom: str

@dataclass
class Recipe:
    id: UUID
    name: str
    ingredients: List[Ingredient]
