import xml.etree.ElementTree as ET
from os import path
from enum import Enum
from model.diagram import ClassDiagram, Class, Relationship
from model.query import QueryDocument
from model.frequency import FrequencyTable
from utils.choices import Stereotype, RelType
from .diagram import ClassDiagramReader
from .query import QueryReader
from .frequency import FrequencyReader
from typing import Tuple


# File is located in the same directory in folder schemas
class Reader:
    class UMLType(str, Enum):
        CLASS = "uml:Class"
        ASSOCIATION = "uml:Association"

    def __init__(self, folder, xs="http://schema.omg.org/spec/XMI/2.1"):
        self.folder = folder
        self.xs = xs

    def read(self) -> Tuple[ClassDiagram, QueryDocument, FrequencyTable]:
        class_diagram = ClassDiagramReader(self.folder, self.xs).read()
        query_doc = QueryReader(self.folder, class_diagram).read()
        frequency_table = FrequencyReader(self.folder).read()

        return class_diagram, query_doc, frequency_table
