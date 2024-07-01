from model.noam.collection import NoAMCollection
from model.aggtree import AggTree, AggNode, RelAggNodeTuple
from model.diagram import ClassDiagram


class Converter:

    def __init__(self, class_diagram: ClassDiagram):
        pass

    def aggregate_to_etf(self, agg_tree: AggTree) -> NoAMCollection:
        """
        Convert the aggregate tree to ETF Collection
        """
        collection = NoAMCollection(agg_tree.root.klass.name)

        # add the root class attributes to the schema
        root_class = agg_tree.root.klass
        for attr, type in root_class.attributes.items():
            collection.schema[attr] = type

        # For each child, add the attributes to the schema recursively as dictionary keys
        for child in agg_tree.root.children:
            child_attributes = self._get_attributes(child)

        collection.print_schema()

        return collection

    def _get_attributes(self, t: RelAggNodeTuple) -> dict:
        """
        Get the attributes of a node child
        """
        attributes = {}
