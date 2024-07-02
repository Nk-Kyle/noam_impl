from model.noam.collection import NoAMCollection
from model.aggtree import AggTree, AggNode, RelAggNodeTuple
from model.diagram import ClassDiagram
from typing import Dict, List
from pprint import pprint


class Converter:

    def __init__(self, class_diagram: ClassDiagram):
        pass

    def aggregate_to_etf(self, agg_tree: AggTree) -> NoAMCollection:
        """
        Convert the aggregate tree to ETF Collection
        """
        collection = NoAMCollection(agg_tree.root.klass.name)

        return_dict = self.__aggregate_recursive(agg_tree.root)
        for key, value in return_dict.items():
            collection.add_entry(key, value)
        collection.add_related_queries(agg_tree.applied_queries)

        return collection

    def etf_to_eao(self, collection: NoAMCollection) -> NoAMCollection:
        """
        Convert the ETF Collection to EAO Collection
        """
        eao_collection = NoAMCollection(collection.name)
        eao_collection.add_entry("e", collection.schema)
        eao_collection.add_related_queries(collection.related_queries)

        return eao_collection

    def __aggregate_recursive(
        self, node: AggNode
    ) -> Dict[str, str | List[Dict[str, str]]]:
        """
        Recursively add the attributes to the collection
        """
        return_dict = {}
        for attr in node.related_attributes:
            return_dict[attr] = node.klass.attributes[attr]

        for child in node.children:
            child_dict = self.__aggregate_recursive(child.node)
            if child.rel.count(child.node.klass) > 1:
                return_dict[child.node.klass.name] = [child_dict]
            else:  # Flatten the list
                for key, value in child_dict.items():
                    return_dict[child.node.klass.name + "_" + key] = value

        for norm_child in node.normalized_children:
            pk = norm_child.node.klass.pk
            if norm_child.rel.count(norm_child.node.klass) > 1:
                return_dict[f"{norm_child.node.klass.name}_{pk}"] = [
                    norm_child.node.klass.attributes[pk]
                ]
            else:
                return_dict[f"{norm_child.node.klass.name}_{pk}"] = (
                    norm_child.node.klass.attributes[pk]
                )

        return return_dict
