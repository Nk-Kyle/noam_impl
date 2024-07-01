from typing import Dict, Any


class NoAMCollection:
    def __init__(self, name: str = None):
        self.name = name
        self.schema = {}

    def __str__(self):
        return self.name or "NoAM Collection"

    def add_entry(self, ek: str, ev: Any):
        """
        Add entry to schema
        """
        self.schema[ek] = ev

    def print_schema(self):
        """
        Prints key of schema as ek and value as ev
        in tabular format
        """
        print(f"Schema of {self.name}")
        print("Ek\tEv")
        for ek, ev in self.schema.items():
            print(f"{ek}\t{ev}")
