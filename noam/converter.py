from model.noam.collection import NoAMCollection
from model.aggtree import AggTree, AggNode
from model.frequency import FrequencyTable
from model.klass import Class
from typing import Dict, List, Set
from collections import defaultdict
from pprint import pprint
from noam.partitioner import Partitioner


class Converter:

    def __init__(self, frequency_table: FrequencyTable):
        self.key_query_map = defaultdict(set)
        self.query_map: Dict[str, Dict[Class, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self.frequency_table = frequency_table

    def aggregate_to_etf(self, agg_tree: AggTree) -> NoAMCollection:
        """
        Convert the aggregate tree to ETF Collection
        """
        self.key_query_map = defaultdict(set)
        self.query_map = agg_tree.query_map

        collection = NoAMCollection(agg_tree.root.klass.name)
        collection.add_related_queries(agg_tree.applied_queries)

        return_dict = self.__aggregate_recursive(agg_tree.root)
        for key, value in return_dict.items():
            collection.add_entry(key, value, self.key_query_map[key])

        return collection

    def etf_to_eao(self, collection: NoAMCollection) -> NoAMCollection:
        """
        Convert the ETF Collection to EAO Collection
        """
        eao_collection = NoAMCollection(collection.name)
        eao_collection.add_entry("e", collection.schema)
        eao_collection.add_related_queries(collection.related_queries)

        return eao_collection

    def etf_to_partition(self, collection: NoAMCollection) -> Partitioner:
        """
        Convert the ETF Collection to Partitioner
        """
        partitioner = Partitioner(collection, self.frequency_table)
        return partitioner

    def __aggregate_recursive(
        self, node: AggNode
    ) -> Dict[str, str | List[Dict[str, str]]]:
        """
        Recursively add the attributes to the collection
        """
        return_dict = {}
        for attr in node.related_attributes:
            return_dict[attr] = node.klass.attributes[attr]
            # Query Mapping
            self.__map_queries(node.klass, attr)

        for child in node.children:
            child_dict = self.__aggregate_recursive(child.node)
            if child.rel.count(child.node.klass) > 1:
                return_dict[child.node.klass.name] = [child_dict]
                self.__map_child_dict_queries(child_dict, child.node.klass.name)

            else:  # Flatten the list
                for key, value in child_dict.items():
                    return_dict[child.node.klass.name + "_" + key] = value
                    self.__map_child_dict_queries(
                        child_dict, child.node.klass.name + "_" + key
                    )

        for norm_child in node.normalized_children:
            pk = norm_child.node.klass.pk
            pk_key = f"{norm_child.node.klass.name}_{pk}"
            if norm_child.rel.count(norm_child.node.klass) > 1:
                return_dict[f"{norm_child.node.klass.name}_{pk}"] = [
                    norm_child.node.klass.attributes[pk]
                ]
                self.__map_queries(norm_child.node.klass, pk, pk_key)
            else:
                return_dict[f"{norm_child.node.klass.name}_{pk}"] = (
                    norm_child.node.klass.attributes[pk]
                )
                self.__map_queries(norm_child.node.klass, pk, pk_key)

        return return_dict

    def __map_queries(self, klass: Class, attribute: str, defined_key: str = None):
        queries = set()
        for query, class_map in self.query_map.items():
            if klass in class_map and attribute in class_map[klass]:
                queries.add(query)
        if defined_key:
            self.key_query_map[defined_key].update(queries)
        self.key_query_map[attribute].update(queries)

    def __map_child_dict_queries(self, child_dict: Dict, key_name: str):
        queries = set()
        for key in child_dict:
            queries.update(self.key_query_map[key])
        self.key_query_map[key_name].update(queries)
