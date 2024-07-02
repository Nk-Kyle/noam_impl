from typing import Dict, Any, Set


class NoAMCollection:
    def __init__(self, name: str = None):
        self.name = name
        self.schema = {}
        self.related_queries = set()

    def __str__(self):
        return self.name or "NoAM Collection"

    def add_entry(self, ek: str, ev: Any):
        """
        Add entry to schema
        """
        self.schema[ek] = ev

    def add_related_queries(self, query: str | Set[str]):
        """
        Add related queries to the collection
        """
        if isinstance(query, str):
            self.related_queries.add(query)
        else:
            self.related_queries.update(query)

    def print_schema(self):
        """
        Prints key of schema as ek and value as ev
        in tabular format
        """
        print(f"Schema of {self.name}")
        print("Related Queries: ", end="")
        print(", ".join(self.related_queries))
        print("Ek\tEv")
        for ek, ev in self.schema.items():
            print(f"{ek}\t{ev}")
