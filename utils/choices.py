from enum import Enum, StrEnum


class Stereotype(Enum):
    ENTITY = "Entity"
    VALUE_OBJECT = "Value Object"


class RelType(Enum):
    ASSOCIATION = 0
    COMPOSITION = 1
    GENERALIZATION = 2
