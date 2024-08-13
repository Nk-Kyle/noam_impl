from noam_impl.model.klass import Class
from .component import QueryNode, RelNodeTuple
from typing import List, Set


class QueryDocument:
    def __init__(self):
        self.queries = {}

    def add_query(self, query: "Query"):
        self.queries[query.name] = query

    def get_query(self, name: str) -> "Query":
        return self.queries[name]

    def get_queries(self, names: List[str]) -> List["Query"]:
        return [self.queries[name] for name in names]

    def get_all_queries(self) -> List["Query"]:
        return list(self.queries.values())


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

    def get_attributes(self, klass: Class) -> list:
        node = self.find_node(klass)
        return node.attributes if node is not None else []

    def all_classes(self) -> Set[Class]:
        return self._all_classes(self.root)

    def _all_classes(self, node: QueryNode) -> Set[Class]:
        classes = set()
        classes.add(node.klass)
        for child in node.children:
            classes.update(self._all_classes(child.node))
        return classes

    def print_tree(self):
        print(f"Query {self.name}")
        for _ in range(20):
            print("-", end="")
        print()
        self.root.print_tree()
        for _ in range(20):
            print("-", end="")
        print()
