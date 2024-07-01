from model.noam.collection import NoAMCollection
from model.aggtree import AggTree
from model.diagram import ClassDiagram


class Converter:

    def __init__(self, class_diagram: ClassDiagram):
        pass

    def aggregate_to_etf(self, agg_tree: AggTree) -> NoAMCollection:
        """
        Convert the aggregate tree to ETF Collection
        """
        collection = NoAMCollection()

        # add the root class attributes to the schema
        root_class = agg_tree.root.klass
        for attr in root_class.attributes:
            collection.schema[attr] = attr
