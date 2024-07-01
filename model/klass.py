from utils.choices import Stereotype
from typing import Dict, Tuple


class Class:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.attributes: Dict[str, str] = {}  # attribute name: type
        self.stereotype = Stereotype.ENTITY
        self.pk = None

    def __str__(self):
        return f"[Class] [{self.stereotype}] {self.name}"

    def add_attribute(self, attribute: Tuple[str, str] | Dict[str, str]):
        if isinstance(attribute, tuple):
            self.attributes[attribute[0]] = attribute[1]
        else:
            self.attributes.update(attribute)

    def set_stereotype(self, stereotype: Stereotype):
        self.stereotype = stereotype

    def set_pk(self, pk: str):
        self.pk = pk
