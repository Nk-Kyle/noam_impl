from enum import Enum


class Stereotype(str, Enum):
    ENTITY = "Entity"
    VALUE_OBJECT = "Value Object"
    PK = "PK"


class RelType(Enum):
    ASSOCIATION = 0
    COMPOSITION = 1
    GENERALIZATION = 2
