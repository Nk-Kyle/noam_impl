from typing import List


class QueryNode:
    from model.klass import Class

    def __init__(
        self, klass: Class, parent: "QueryNode" = None, attributes: List[str] = None
    ):
        self.klass = klass
        self.parent = parent
        self.children: List[RelNodeTuple] = []
        self.attributes = attributes if attributes is not None else []

    def __str__(self):
        return f"[QueryNode] {self.klass.name}"

    def add_child(self, tuple: "RelNodeTuple"):
        self.children.append(tuple)

    def print_tree(self, level=0):
        print("\t" * level + str(self), end=" ")
        if self.attributes:
            print(f"({', '.join(self.attributes)})")
        else:
            print()
        for child in self.children:
            child.node.print_tree(level + 1)


class RelNodeTuple:
    from model.relationship import Relationship

    def __init__(self, rel: Relationship, node: QueryNode):
        self.rel = rel
        self.node = node

    def __str__(self):
        return f"[RelNodeTuple] {self.rel.name} -> {self.node.klass.name}"
