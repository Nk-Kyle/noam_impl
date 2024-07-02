from model.klass import Class
from model.query import Query
from model.relationship import Relationship
from .component import AggNode, RelAggNodeTuple
from typing import List, Dict, Set
from collections import defaultdict


class AggTree:
    AGGTREE_INDEX = 0

    def __init__(self, applied_query: str, root_class: Class):
        self.index = 1
        self.label = applied_query
        self.applied_queries = set([applied_query])
        self.query_map: Dict[str, Dict[Class, Set[str]]] = defaultdict(
            lambda: defaultdict(set)  # Query -> {Class -> Set[Attributes]}
        )

        AggTree.AGGTREE_INDEX += 1
        self.root = AggNode(root_class, main_root=self, is_root=True)

    def traverse(self, node: AggNode) -> List[AggNode]:
        nodes = [node]
        for child in node.children:
            nodes.extend(self.traverse(child.node))
        return nodes

    def print_tree(self, with_attributes=False):
        print(f"AggTree {self.label}")
        print(f"Applied Queries: {self.applied_queries}")
        for _ in range(20):
            print("-", end="")
        print()
        self.root.print_tree(with_attributes=with_attributes)
        for _ in range(20):
            print("-", end="")
        print()
