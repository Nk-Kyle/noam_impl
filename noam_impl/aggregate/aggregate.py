from noam_impl.model.diagram import ClassDiagram, Class
from noam_impl.model.query import QueryDocument
from noam_impl.model.frequency import FrequencyTable
from noam_impl.model.aggtree import AggTree, AggNode, RelAggNodeTuple
from noam_impl.model.relationship import Relationship
from noam_impl.aggregate.utils import Utils
from noam_impl.aggregate.transform import Transformer
from noam_impl.aggregate.optimizer import Optimizer
from noam_impl.utils.choices import RelType, Stereotype
from typing import List, Dict, Set
from collections import defaultdict


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
        self.unused_vos: Set[Class] = set()

    def create_optimized_trees(self) -> List[AggTree]:
        """
        Create the optimized aggregate trees
        """
        self.aggregate_relationship()
        self.create_aggregate_trees()

        self.agg_trees = Optimizer(self.frequency_table, self.agg_trees).optimize()
        self.connect_value_objects()
        self.get_related_attributes()

        return self.agg_trees

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
                self.add_unused_VOs(node)

    def get_related_attributes(self):

        unused_attrs = self.get_unused_attributes()
        root_classes = self.get_root_classes()

        for agg_tree in self.agg_trees:
            queries = self.query_doc.get_queries(list(agg_tree.applied_queries))
            for query in queries:
                for node in agg_tree.traverse(agg_tree.root):
                    attributes = query.get_attributes(node.klass)
                    node.related_attributes.update(query.get_attributes(node.klass))
                    agg_tree.query_map[query.name][node.klass].update(attributes)

                    if node.klass not in root_classes:
                        # If not root class, make sure to add unused attributes
                        node.related_attributes.update(unused_attrs[node.klass])

    def add_pruned_VOs(self, node: AggNode):
        """
        Add the pruned value objects of a class
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

    def add_unused_VOs(self, node: AggNode):
        """
        Add the unused value objects of a class
        """
        unused = self.get_unused_value_objects()
        for vo in unused:
            rel = self.class_diagram.get_relationship_of_vo_to_entity(vo, node.klass)
            if rel is not None:
                print(f"Adding unused VO {vo.name} to {node.klass.name}")
                new_node = AggNode(vo, node.main_root, node)
                node.add_child(RelAggNodeTuple(rel, new_node))

    def get_unused_attributes(self) -> Dict[Class, Set[str]]:
        """
        Get the unused attributes of the class diagram for each class
        from the queries
        """
        unused = defaultdict(set)  # Class -> Set[Attribute]

        # Get the used attributes from the queries
        used_attributes = defaultdict(set)  # Class -> Set[Attribute]
        for klass in self.class_diagram.classes.values():
            for query in self.query_doc.get_all_queries():
                used_attributes[klass].update(query.get_attributes(klass))

        # Get the unused attributes
        for klass in self.class_diagram.classes.values():
            all_attributes = set(klass.attributes.keys())
            unused[klass] = all_attributes - used_attributes[klass]

        return unused

    def get_unused_value_objects(self) -> Set[Class]:
        """
        Get the unused value objects of the class diagram
        """
        if self.unused_vos:
            return self.unused_vos

        used: Set[Class] = set()
        for query in self.query_doc.get_all_queries():
            for klass in query.all_classes():
                if klass.stereotype == Stereotype.VALUE_OBJECT:
                    used.add(klass)

        all_vos = set()
        for klass in self.class_diagram.classes.values():
            if klass.stereotype == Stereotype.VALUE_OBJECT:
                all_vos.add(klass)

        self.unused_vos = all_vos - used
        return self.unused_vos

    def get_root_classes(self) -> Set[Class]:
        """
        Get the root classes of the class diagram
        """
        roots = set()
        for agg_tree in self.agg_trees:
            roots.add(agg_tree.root.klass)
        return roots
