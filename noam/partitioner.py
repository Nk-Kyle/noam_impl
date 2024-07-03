from model.noam.collection import NoAMCollection
from model.frequency import FrequencyTable
from collections import defaultdict
from navathe.vp import partition as vertical_partition
from typing import List


class Partitioner:
    def __init__(self, etf_model: NoAMCollection, frequency_table: FrequencyTable):
        self.etf_model = etf_model
        self.frequency_table = frequency_table
        self.aum = self.create_AUM()
        self.aam = self.create_AAM()

    def partition(self):
        unused_attributes = self.get_unused_attributes()
        # Remove unused attributes from the AAM
        for unused_attribute in unused_attributes:
            for ek in self.aam.keys():
                del self.aam[ek][unused_attribute]
        for unused_attribute in unused_attributes:
            del self.aam[unused_attribute]

        # Create a mapping of id: aam key
        id_to_key = {}
        for idx, key in enumerate(self.aam.keys()):
            id_to_key[idx] = key

        # Convert AAM to adjacency matrix
        adjacency_matrix = []
        for ek1 in self.aam.keys():
            row = []
            for ek2 in self.aam.keys():
                row.append(self.aam[ek1][ek2])
            adjacency_matrix.append(row)

        # Perform vertical partitioning
        vertical_partition(adjacency_matrix)

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

    def create_AAM(self):
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

    def print_AAM(self):
        """
        Print AM in tabular format
        """
        print("AM")
        print("Ek", end="\t")
        for ek in self.aam.keys():
            print(ek, end="\t")
        print()
        for ek1, ek_dict in self.aam.items():
            print(ek1, end="\t")
            for ek2, value in ek_dict.items():
                print(value, end="\t")
            print()

    def get_unused_attributes(self):
        """
        Get the attributes that are not used in any query
        """
        # unused attributes will have a sum of 0 in the AUM
        unused_attributes = set()
        for ek in self.etf_model.schema.keys():
            if (
                sum([self.aum[query][ek] for query in self.etf_model.related_queries])
                == 0
            ):
                unused_attributes.add(ek)
        return unused_attributes
