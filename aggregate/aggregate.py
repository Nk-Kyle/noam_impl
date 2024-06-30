from model.diagram import ClassDiagram, Class, Relationship
from model.query import Query, QueryNode, RelNodeTuple
from model.frequency import FrequencyTable
from typing import List, Dict, Set, Tuple
from utils.choices import RelType
from collections import defaultdict


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
                root_class = self.get_class_aggregate(relation.to_class)[0]
                agg_set = self.get_class_aggregate(relation.from_class)[1]
                self.agg_map[root_class].update(agg_set)
                temp_classes.remove(relation.from_class)

        for klass in temp_classes:
            if klass not in self.agg_map:
                self.agg_map[klass] = {klass}
            else:
                self.agg_map[klass].add(klass)

    def get_class_aggregate(self, klass: Class) -> Tuple[Class, Set[Class]]:
        """
        Get the aggregate relationship of a class

        Parameters
        ----------
        class_ : Class
            The class to get the aggregate relationship

        Returns
        -------
        Tuple[Class, Set[Class]]
            The root class and the set of classes that are aggregated
        """

        for root, children in self.agg_map.items():
            if klass in children:
                return root, children
        return klass, {klass}

    def print_aggregate(self):
        for root, children in self.agg_map.items():
            print(f"Root: {root.name}")
            for child in children:
                print(f"Member: {child.name}")
            print("")
