from typing import Any, Set, Union


class NoAMCollection:
    def __init__(self, name: str = None):
        self.name = name
        self.schema = {}
        self.related_queries = set()
        self.ek_queries = {}
        self.type = "etf"

    def __str__(self):
        return self.name or "NoAM Collection"

    def add_entry(self, ek: str, ev: Any, queries: Set[str] = None):
        """
        Add entry to schema
        """
        self.schema[ek] = ev
        if queries:
            self.ek_queries[ek] = queries

    def add_related_queries(self, query: Union[str, Set[str]]):
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

    def export_schema_as_json(self):
        """
        Prints schema as json
        """
        DIRECTORY = "results/schema"
        import json
        import os

        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        if not os.path.exists(f"{DIRECTORY}/{self.type}"):
            os.makedirs(f"{DIRECTORY}/{self.type}")

        with open(f"{DIRECTORY}/{self.type}/{self.name}.json", "w") as f:
            json.dump(
                self.schema,
                f,
                indent=4,
            )
