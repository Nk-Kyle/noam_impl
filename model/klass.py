from utils.choices import Stereotype
from typing import List


class Class:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.attributes: List[str] = []
        self.stereotype = Stereotype.ENTITY

    def add_attribute(self, attribute: str):
        self.attributes.append(attribute)

    def set_stereotype(self, stereotype: Stereotype):
        self.stereotype = stereotype
