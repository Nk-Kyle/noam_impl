from typing import Dict
from model.klass import Class
from model.relationship import Relationship


class ClassDiagram:
    def __init__(self):
        self.classes: Dict[str, Class] = {}
        self.classes_names: Dict[str, Class] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.relationships_names: Dict[str, Relationship] = {}

    def add_class(self, klass: Class):
        self.classes[klass.id] = klass
        self.classes_names[klass.name] = klass

    def get_class(self, class_id):
        return self.classes.get(class_id)

    def add_relationship(self, relationship: Relationship):
        self.relationships[relationship.id] = relationship
        self.relationships_names[
            relationship.from_class.name + relationship.to_class.name
        ] = relationship

    def get_relationship(self, relationship_id):
        return self.relationships.get(relationship_id)
