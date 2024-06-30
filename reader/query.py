import xml.etree.ElementTree as ET
from os import path
from model.query import Query, QueryNode, RelNodeTuple
from model.diagram import ClassDiagram
from typing import List


# File is located in the same directory in folder schemas
class QueryReader:

    def __init__(self, folder: str, class_diagram: ClassDiagram):
        self.folder = folder
        self.class_diagram = class_diagram

    def read(self) -> List[Query]:
        """
        Reads the query.xml file and returns a list of Query objects

        Returns
        -------
        List[Query]
            The list of query objects
        """

        tree = ET.parse(path.join(self.folder, "query.xml"))
        root = tree.getroot()

        queries = []
        for query in root:
            root = query.find("class")
            root_class = self.class_diagram.get_class_by_name(root.attrib["name"])
            # root_class_attributs: data in <attribute> data </attribute>
            # i.e. <attribute>my attribute</attribute>
            root_class_attributes = [attr.text for attr in root.findall("attribute")]
            query = Query(query.attrib["name"], root_class, root_class_attributes)

            # Read the query recursively
            self.read_recursive(root, query.root)

            queries.append(query)

        return queries

    def read_recursive(self, class_tree, parent: QueryNode = None):
        """
        Reads the query.xml file recursively and updates adds the nodes to the parent node

        Parameters
        ----------
        class_tree : xml.etree.ElementTree.Element
            The class node to read
        parent : QueryNode, optional
            The parent node, by default None

        """
        relationship = class_tree.findall("relation")
        for rel in relationship:
            child = rel.find("class")
            child_class = self.class_diagram.get_class_by_name(child.attrib["name"])
            child_class_attributes = [attr.text for attr in child.findall("attribute")]
            query_node = QueryNode(child_class, parent, child_class_attributes)
            relationship = self.class_diagram.get_relationship_by_name(
                rel.attrib["name"]
            )
            parent.add_child(RelNodeTuple(relationship, query_node))
            self.read_recursive(child, query_node)
