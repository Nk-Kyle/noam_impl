import xml.etree.ElementTree as ET
from os import path
from enum import Enum
from model.diagram import ClassDiagram, Class, Relationship
from utils.choices import Stereotype, RelType


# File is located in the same directory in folder schemas
class ClassDiagramReader:
    class UMLType(str, Enum):
        CLASS = "uml:Class"
        ASSOCIATION = "uml:Association"
        DATA_TYPE = "uml:DataType"

    def __init__(self, folder: str, xs: str = "http://schema.omg.org/spec/XMI/2.1"):
        self.folder = folder
        self.xs = xs
        self.data_types = {}

    def read(self) -> ClassDiagram:
        """
        Reads the schema.xmi file and returns a ClassDiagram object

        Returns
        -------
        ClassDiagram
            The class diagram object
        """
        class_diagram = ClassDiagram()

        tree = ET.parse(path.join(self.folder, "schema.xmi"))
        # File is structured as follows:
        # <?xml version="1.0" encoding="UTF-8"?>
        # <xmi:XMI xmlns:xmi="http://www.omg.org/XMI" xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML" xmi:version="2.0">
        #  <uml:Model xmi:id="_0" name="Model" visibility="public">
        #  <ownedMember xmi:type="uml:Class" xmi:id="_1" name="Class1" visibility="public">
        #  </ownedMember>

        root = tree.getroot()

        modelTag = None
        for child in root:
            if child.tag.endswith("Model"):
                modelTag = child
                break

        if modelTag is None:
            raise Exception("Model tag not found")

        members = modelTag.findall("ownedMember")

        # Initialize the datatypes
        for member in members:
            member_type = member.attrib[f"{{{self.xs}}}type"]
            if member_type == self.UMLType.DATA_TYPE:
                self.data_types[member.attrib[f"{{{self.xs}}}id"]] = member.attrib[
                    "name"
                ]

        # First pass: read all classes
        for member in members:
            # Check xsi:type attribute
            member_type = member.attrib[f"{{{self.xs}}}type"]
            if member_type == self.UMLType.CLASS:
                klass = self._read_class(member)
                class_diagram.add_class(klass)

        # Second pass: read all relationships, since all classes are already created
        for member in members:
            member_type = member.attrib[f"{{{self.xs}}}type"]
            if member_type == self.UMLType.ASSOCIATION:
                rel = self._read_association(member, class_diagram)
                class_diagram.add_relationship(rel)
            elif (
                member_type == self.UMLType.CLASS
                and member.find("generalization") is not None
            ):
                # Checks for generalization
                rel = self._read_generalization(member, class_diagram)
                class_diagram.add_relationship(rel)

        return class_diagram

    def _read_class(self, class_tag) -> Class:
        """
        For each class tag, create a Class object and add it to the ClassDiagram

        Parameters
        ----------
        class_tag : Element
            The class tag element

        Returns
        -------
        Class
            The class object
        """
        # Class tag is structured as follows:
        # <ownedMember xmi:type="uml:Class" xmi:id="_1" name="Class1" visibility="public">
        #   <ownedAttribute xmi:type="uml:Property" xmi:id="_2" name="attribute1" visibility="public"/>
        #   <appliedStereotype xmi:type="uml:Stereotype" href="path/to/stereotype"/>
        # </ownedMember>
        klass = Class(class_tag.attrib[f"{{{self.xs}}}id"], class_tag.attrib["name"])
        for attribute in class_tag.findall("ownedAttribute"):
            attr_type = self.data_types.get(
                attribute.attrib["type"], attribute.attrib["type"]
            )
            klass.add_attribute((attribute.attrib["name"], attr_type))
            if attribute.find("appliedStereotype") is not None:
                stereotype_value = attribute.find("appliedStereotype").attrib[
                    f"{{{self.xs}}}value"
                ]
                if stereotype_value == Stereotype.PK.value:
                    klass.set_pk(attribute.attrib["name"])

        if class_tag.find("appliedStereotype") is not None:
            stereotype_value = class_tag.find("appliedStereotype").attrib[
                f"{{{self.xs}}}value"
            ]
            if stereotype_value == Stereotype.VALUE_OBJECT.value:
                klass.set_stereotype(Stereotype.VALUE_OBJECT)

        return klass

    def _read_association(
        self, association_tag, class_diagram: ClassDiagram
    ) -> Relationship:
        """
        For each association tag, create a Relationship object and add it to the ClassDiagram

        Parameters
        ----------
        association_tag : Element
            The association tag element
        class_diagram : ClassDiagram
            The class diagram object

        Returns
        -------
        Relationship
            The relationship object

        """
        # Association tag is structured as follows:
        # <ownedMember xmi:type="uml:Association" xmi:id="_3" visibility="public">
        #   <ownedEnd aggregation="composite" association="_3" xmi:id="_4" type="_a"/>
        #       <lowerValue xmi:type="uml:LiteralInteger" xmi:id="_6" value="1"/>
        #   <ownedEnd aggregation="none" association="_3" xmi:id="_5" type="_b"/>
        #       <lowerValue xmi:type="uml:LiteralInteger" xmi:id="_7" value="1"/>
        # </ownedMember>
        owned_ends = association_tag.findall("ownedEnd")
        composite_end = None
        for end in owned_ends:
            # Check for composite
            if end.attrib["aggregation"] == "composite":
                composite_end = end
                break

        if composite_end is None:
            from_end = owned_ends[0]
            to_end = owned_ends[1]
        else:
            from_end = composite_end
            to_end = owned_ends[0] if owned_ends[0] != composite_end else owned_ends[1]

        from_class = class_diagram.get_class(from_end.attrib["type"])
        to_class = class_diagram.get_class(to_end.attrib["type"])

        relationship = Relationship(
            association_tag.attrib[f"{{{self.xs}}}id"],
            from_class,
            to_class,
            float(from_end.find("lowerValue").attrib["value"]),
            float(to_end.find("lowerValue").attrib["value"]),
            RelType.COMPOSITION if composite_end is not None else RelType.ASSOCIATION,
            (
                association_tag.attrib["name"]
                if "name" in association_tag.attrib
                else None
            ),
        )

        return relationship

    def _read_generalization(self, class_tag, class_diagram: ClassDiagram):
        """
        For each generalization tag, create a Relationship object and add it to the ClassDiagram

        Parameters
        ----------
        class_tag : Element
            The class tag element
        class_diagram : ClassDiagram
            The class diagram object
        """
        # Generalization tag is structured as follows:
        # <ownedMember xmi:type="uml:Class" xmi:id="_1" name="Class1" visibility="public">
        #   <generalization xmi:type="uml:Generalization" xmi:id="_2" general="_3"/>
        # </ownedMember>
        generalization = class_tag.find("generalization")
        from_class = class_diagram.get_class(class_tag.attrib[f"{{{self.xs}}}id"])
        to_class = class_diagram.get_class(generalization.attrib["general"])

        relationship = Relationship(
            generalization.attrib[f"{{{self.xs}}}id"],
            from_class,
            to_class,
            1,
            1,
            RelType.GENERALIZATION,
            None,
        )

        return relationship
