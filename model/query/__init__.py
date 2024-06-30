from model.klass import Class
from model.relationship import Relationship
from .component import QueryNode, RelNodeTuple


class Query:
    QUERY_INDEX = 0

    def __init__(
        self, name: str = None, root_class: Class = None, root_attributes: list = None
    ):
        self.id = Query.QUERY_INDEX
        self.name = name if name is not None else f"Q{Query.QUERY_INDEX}"
        Query.QUERY_INDEX += 1
        self.root = QueryNode(root_class, attributes=root_attributes)

    def find_node(self, klass: Class) -> QueryNode:
        return self._find_node(klass, self.root)

    def _find_node(self, klass: Class, node: QueryNode) -> QueryNode:
        if node.klass == klass:
            return node
        for child in node.children:
            found = self._find_node(klass, child.node)
            if found is not None:
                return found
        return None

    def print_tree(self):
        self.root.print_tree()
