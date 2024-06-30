from utils.choices import Stereotype
from typing import Set


class Class:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.attributes: Set[str] = set()
        self.stereotype = Stereotype.ENTITY
        self.pk = None

    def __str__(self):
        return f"[Class] [{self.stereotype}] {self.name}"

    def add_attribute(self, attribute: str | Set[str]):
        if isinstance(attribute, str):
            self.attributes.add(attribute)
        else:
            self.attributes.update(attribute)

    def set_stereotype(self, stereotype: Stereotype):
        self.stereotype = stereotype

    def set_pk(self, pk: str):
        self.pk = pk
