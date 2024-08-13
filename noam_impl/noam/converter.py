from noam_impl.model.noam.collection import NoAMCollection
from noam_impl.model.aggtree import AggTree, AggNode
from noam_impl.model.frequency import FrequencyTable
from noam_impl.model.klass import Class
from noam_impl.noam.partitioner import Partitioner
from typing import Dict, List, Set, Union
from collections import defaultdict


class Converter:

    def __init__(self, frequency_table: FrequencyTable):
        self.key_query_map: Dict[Class, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )  # Class -> {Attribute -> Set[Query]}
        self.query_map: Dict[str, Dict[Class, Set[str]]] = defaultdict(
            lambda: defaultdict(set)  # Query -> {Class -> Set[Attribute]}
        )
        self.frequency_table = frequency_table

    def aggregate_to_etf(self, agg_tree: AggTree) -> NoAMCollection:
        """
        Convert the aggregate tree to ETF Collection
        """
        self.key_query_map = defaultdict(lambda: defaultdict(set))
        self.query_map = agg_tree.query_map

        collection = NoAMCollection(agg_tree.root.klass.name)
        collection.add_related_queries(agg_tree.applied_queries)

        # add all the attributes to the collection from the aggregate tree
        return_dict = self.__aggregate_recursive(agg_tree.root)
        for key, value in return_dict.items():
            collection.add_entry(
                key, value, self.key_query_map[agg_tree.root.klass][key]
            )

        # add all root attributes to the collection
        for attr in agg_tree.root.klass.attributes:
            collection.add_entry(attr, agg_tree.root.klass.attributes[attr])

        return collection

    def etf_to_eao(self, etf_collection: NoAMCollection) -> NoAMCollection:
        """
        Convert the ETF Collection to EAO Collection
        """
        eao_collection = NoAMCollection(etf_collection.name)
        eao_collection.add_entry("e", etf_collection.schema)
        eao_collection.add_related_queries(etf_collection.related_queries)
        eao_collection.type = "eao"
        return eao_collection

    def etf_to_partition(self, etf_collection: NoAMCollection) -> NoAMCollection:
        """
        Convert the ETF Collection to Partitioner
        """
        partitioner = Partitioner(etf_collection, self.frequency_table)
        partitions = partitioner.partition()

        # Convert the partitions to a NoAMCollection
        partition_collection = NoAMCollection(etf_collection.name)
        partition_collection.add_related_queries(etf_collection.related_queries)
        for idx, partition in enumerate(partitions):
            # Add an entry for each partition
            if len(partition) > 1:
                # Create a dictionary for the partition
                partition_dict = {}
                for ek in partition:
                    partition_dict[ek] = etf_collection.schema[ek]
                partition_collection.add_entry(f"p{idx}", partition_dict)
            else:
                # Add the single attribute to the collection
                partition_collection.add_entry(
                    f"p{idx}:{partition[0]}", etf_collection.schema[partition[0]]
                )
        partition_collection.type = "partition"
        return partition_collection

    def __aggregate_recursive(
        self, node: AggNode
    ) -> Dict[str, Union[str, List[Dict[str, str]]]]:
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
            child_queries = self.__get_child_queries(child_dict, child.node.klass)
            if child.rel.count(child.node.klass) > 1:
                return_dict[child.node.klass.name] = [child_dict]
                # Query Mapping
                self.__map_child_queries(
                    node.klass, child.node.klass.name, child_queries
                )
            else:  # Flatten the list
                for key, value in child_dict.items():
                    return_dict[child.node.klass.name + "_" + key] = value
                    self.__map_child_queries(
                        node.klass, child.node.klass.name + "_" + key, child_queries
                    )

        for norm_child in node.normalized_children:
            pk = norm_child.node.klass.pk
            pk_key = f"{norm_child.node.klass.name}_{pk}"
            if norm_child.rel.count(norm_child.node.klass) > 1:
                return_dict[f"{norm_child.node.klass.name}_{pk}"] = [
                    norm_child.node.klass.attributes[pk]
                ]
                self.__map_queries(node.klass, pk, pk_key)
            else:
                return_dict[f"{norm_child.node.klass.name}_{pk}"] = (
                    norm_child.node.klass.attributes[pk]
                )
                self.__map_queries(node.klass, pk, pk_key)

        return return_dict

    def __map_queries(self, klass: Class, attribute: str, defined_key: str = None):
        queries = set()
        for query, class_map in self.query_map.items():
            if klass in class_map and attribute in class_map[klass]:
                queries.add(query)

        attribute = defined_key if defined_key else attribute

        self.key_query_map[klass][attribute].update(queries)

    def __map_child_queries(self, klass: Class, key_name: str, queries: Set[str]):
        self.key_query_map[klass][key_name].update(queries)

    def __get_child_queries(self, child_dict: Dict, klass: Class) -> Set[str]:
        queries = set()
        for key in child_dict:
            queries.update(self.key_query_map[klass][key])
        return queries
