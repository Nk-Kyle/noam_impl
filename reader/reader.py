import xml.etree.ElementTree as ET
from os import path
from enum import StrEnum
from model.diagram import ClassDiagram, Class, Relationship
from utils.choices import Stereotype, RelType
from .diagram import ClassDiagramReader
from .query import QueryReader


# File is located in the same directory in folder schemas
class Reader:
    class UMLType(StrEnum):
        CLASS = "uml:Class"
        ASSOCIATION = "uml:Association"

    def __init__(self, folder, xs="http://schema.omg.org/spec/XMI/2.1"):
        self.folder = folder
        self.xs = xs

    def read(self) -> ClassDiagram:
        class_diagram = ClassDiagramReader(self.folder, self.xs).read()
        queries = QueryReader(self.folder, class_diagram).read()
