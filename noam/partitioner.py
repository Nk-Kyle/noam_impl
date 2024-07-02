from model.noam.collection import NoAMCollection
from model.frequency import FrequencyTable
from collections import defaultdict


class Partitioner:
    def __init__(self, etf_model: NoAMCollection, frequency_table: FrequencyTable):
        self.etf_model = etf_model
        self.frequency_table = frequency_table
        self.aum = self.create_AUM()
        self.am = self.create_AM()

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

    def create_AM(self):
        """
        Create AM (Affinity Matrix) from AUM and Frequency Table
        Representational of graph AM
        Rows: ek
        Columns: ek

        Aff_ij = sum ACC_ijk
        ACC_ijk = Freq_k * AUM_ki * AUM_kj
        """

        am = defaultdict(dict)
        for ek1 in self.etf_model.schema.keys():
            for ek2 in self.etf_model.schema.keys():
                affinity = 0
                for query in self.etf_model.related_queries:
                    freq = self.frequency_table.get_frequency(query)
                    affinity += freq * self.aum[query][ek1] * self.aum[query][ek2]
                am[ek1][ek2] = affinity
        return am

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

    def print_AM(self):
        """
        Print AM in tabular format
        """
        print("AM")
        print("Ek", end="\t")
        for ek in self.etf_model.schema.keys():
            print(ek, end="\t")
        print()
        for ek1, ek_dict in self.am.items():
            print(ek1, end="\t")
            for ek2, value in ek_dict.items():
                print(value, end="\t")
            print()
