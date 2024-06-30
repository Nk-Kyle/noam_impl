from model.diagram import ClassDiagram, Class
from model.query import Query
from model.frequency import FrequencyTable
from typing import List, Dict, Set
from utils.choices import RelType, Stereotype
from collections import defaultdict
from model.aggtree import AggTree, AggNode
from aggregate.utils import Utils
from aggregate.transform import Transformer


class Aggregator:
    def __init__(
        self,
        class_diagram: ClassDiagram,
        queries: List[Query],
        frequency_table: FrequencyTable,
    ):
        self.class_diagram = class_diagram
        self.queries = queries
        self.frequency_table = frequency_table
        self.agg_map: Dict[Class, Set[Class]] = defaultdict(set)
        self.pruned_map: Dict[Class, Set[str]] = defaultdict(set)
        self.agg_trees: List[AggTree] = []

    def aggregate_relationship(self):
        """
        Aggregates the relationships in the class diagram

        Relationship to be aggregated:
        - Composition (Value Objects)
        - Generalization (Inheritance)

        Aggregate root class and its children
        """
        temp_classes = list(self.class_diagram.classes.values())
        for relation in self.class_diagram.relationships.values():
            if (
                relation.type == RelType.COMPOSITION
                or relation.type == RelType.GENERALIZATION
            ):
                root_class, _ = Utils.get_class_aggregate(
                    self.agg_map, relation.to_class
                )
                _, agg_set = Utils.get_class_aggregate(
                    self.agg_map, relation.from_class
                )
                self.agg_map[root_class].update(agg_set)
                temp_classes.remove(relation.from_class)

        for relation in self.class_diagram.relationships.values():
            if relation.type == RelType.GENERALIZATION:
                Utils.populate_parent(relation.from_class, relation.to_class)

        for klass in temp_classes:
            if klass not in self.agg_map:
                self.agg_map[klass] = {klass}
            else:
                self.agg_map[klass].add(klass)

    def create_aggregate_trees(self):
        """
        Create the aggregate trees from the class diagram
        """
        for query in self.queries:
            agg_tree = Transformer.create_aggtree_from_query(query)
            self.prune_redirect_path(agg_tree)
            self.agg_trees.append(agg_tree)

    def prune_redirect_path(self, agg_tree: AggTree):
        """
        Change the class of AggNode class to the root class
        based on self.agg_map
        """

        # replace the class with the root class
        def __pr_node(node: AggNode):
            root, _ = Utils.get_class_aggregate(self.agg_map, node.klass)
            if node.klass.stereotype == Stereotype.VALUE_OBJECT:
                self.pruned_map[node.klass].add(root.name)

            # replace the class with the root class
            node.klass = root

            for child in node.children:
                __pr_node(child.node)

        __pr_node(agg_tree.root)

        # remove consecutive classes (parent and child) with the same name
        def __prune_redirect(node: AggNode):
            for child in node.children[:]:
                if node.klass == child.node.klass:
                    node.children.remove(child)
                    continue
                __prune_redirect(child.node)

        __prune_redirect(agg_tree.root)
