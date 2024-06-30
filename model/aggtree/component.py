from typing import List
from model.klass import Class


class AggNode:
    def __init__(
        self, klass: Class, main_root, parent: "AggNode" = None, is_root=False
    ):
        from model.aggtree import AggTree

        self.klass = klass
        self.parent: AggNode = parent
        self.main_root: AggTree = main_root
        self.children: List[RelAggNodeTuple] = []
        self.is_root = is_root
        self.read_cost = 1
        self.update_cost = 1

    def get_tuple_of_node(self, node: "AggNode") -> "RelAggNodeTuple":
        for child in self.children:
            if child.node == node:
                return child
        return None

    def __str__(self):
        return f"[AggNode] {self.klass.name}"

    def add_child(self, tuple: "RelAggNodeTuple"):
        self.children.append(tuple)

    def print_tree(self, level=0):
        print("\t" * level + str(self))
        for child in self.children:
            child.node.print_tree(level + 1)

    @property
    def descendants_class_rel_count(self):
        count = 0
        for child in self.children:
            count += 2
            count += child.node.descendants_class_rel_count
        return count


class RelAggNodeTuple:
    from model.relationship import Relationship

    def __init__(self, rel: Relationship, node: AggNode):
        self.rel = rel
        self.node = node
        self.normalized = False
        self.prev_arrity = rel.count(node.parent.klass)
        self.next_arrity = rel.count(node.klass)
        self.rel_update_cost = 1

    def __str__(self):
        return f"[AggNodeTuple] {self.rel.name} -> {self.node.klass.name}"
