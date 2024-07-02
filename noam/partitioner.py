from model.noam.collection import NoAMCollection
from collections import defaultdict


class Partitioner:
    def __init__(self, etf_model: NoAMCollection):
        self.etf_model = etf_model
        self.aum = self.create_AUM()

    def create_AUM(self):
        """
        Create AUM (Attribute Usage Matrix) from ETF model

        Rows: Queries
        Columns: Ek
        """
        aum = defaultdict(dict)
        for query in self.etf_model.related_queries:
            for ek in self.etf_model.schema.keys():
                if query in self.etf_model.ek_queries.get(ek, []):
                    aum[query][ek] = 1
                else:
                    aum[query][ek] = 0
        return aum

    def print_AUM(self):
        """
        Print AUM in tabular format
        """
        print("AUM")
        print("Queries", end="\t")
        for ek in self.etf_model.schema.keys():
            print(ek, end="\t")
        print()
        for query, ek_dict in self.aum.items():
            print(query, end="\t")
            for ek, value in ek_dict.items():
                print(value, end="\t")
            print()
