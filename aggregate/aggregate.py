from model.diagram import ClassDiagram, Class
from model.query import QueryDocument
from model.frequency import FrequencyTable
from typing import List, Dict, Set, Tuple
from utils.choices import RelType, Stereotype
from collections import defaultdict
from model.aggtree import AggTree, AggNode, RelAggNodeTuple
from model.relationship import Relationship
from aggregate.utils import Utils
from aggregate.transform import Transformer
from aggregate.optimizer import Optimizer


class Aggregator:
    def __init__(
        self,
        class_diagram: ClassDiagram,
        query_doc: QueryDocument,
        frequency_table: FrequencyTable,
    ):
        self.class_diagram = class_diagram
        self.query_doc = query_doc
        self.frequency_table = frequency_table
        self.agg_map: Dict[Class, Set[Class]] = defaultdict(set)
        self.pruned_map: Dict[Class, Dict[str, Set[Relationship]]] = defaultdict(
            lambda: defaultdict(set)
        )  # Class -> {query -> Relationship}
        self.agg_trees: List[AggTree] = []

    def create_optimized_trees(self):
        """
        Create the optimized aggregate trees
        """
        self.aggregate_relationship()
        self.create_aggregate_trees()

        self.agg_trees = Optimizer(self.frequency_table, self.agg_trees).optimize()
        self.connect_value_objects()
        self.get_related_attributes()

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
        for query in self.query_doc.get_all_queries():
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
                relationship = node.parent.get_tuple_of_node(node).rel
                self.pruned_map[root][agg_tree.label].add(relationship)

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

    def connect_value_objects(self):
        """
        Connect the value objects to the root class
        """
        for agg_tree in self.agg_trees:
            for node in agg_tree.traverse(agg_tree.root):
                self.add_pruned_VOs(node)

    def get_related_attributes(self):
        for agg_tree in self.agg_trees:
            queries = self.query_doc.get_queries(list(agg_tree.applied_queries))
            for query in queries:
                for node in agg_tree.traverse(agg_tree.root):
                    node.related_attributes.update(query.get_attributes(node.klass))

    def add_pruned_VOs(self, node: AggNode) -> Set[RelAggNodeTuple]:
        """
        Get the pruned value objects of a class
        """

        pruneds: Set[Relationship] = set()

        for q_label in node.main_root.applied_queries:
            pruneds.update(self.pruned_map[node.klass][q_label])

        # Remove duplicate nodes
        # node1 = node2 if node1.klass == node2.klass
        klasses = set()
        for pruned in pruneds.copy():
            if pruned.from_class in klasses:
                pruneds.remove(pruned)
            else:
                klasses.add(pruned.from_class)

        # Create new RelAggNodeTuple with the same node
        for pruned in pruneds:
            new_node = AggNode(pruned.from_class, node.main_root, node)
            node.add_child(RelAggNodeTuple(pruned, new_node))
