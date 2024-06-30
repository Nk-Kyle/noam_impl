from model.klass import Class
from model.query import Query
from model.relationship import Relationship
from .component import AggNode, RelAggNodeTuple


class AggTree:
    AGGTREE_INDEX = 0

    def __init__(self, applied_query: str, root_class: Class):
        self.index = 1
        self.label = applied_query

        AggTree.AGGTREE_INDEX += 1
        self.root = AggNode(root_class, main_root=self, is_root=True)

    def print_tree(self):
        print(f"AggTree {self.label}")
        for _ in range(20):
            print("-", end="")
        print()
        self.root.print_tree()
        for _ in range(20):
            print("-", end="")
        print()
