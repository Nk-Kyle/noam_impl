from model.noam.collection import NoAMCollection
from model.frequency import FrequencyTable
from collections import defaultdict
from navathe.vp import partition as vertical_partition
from typing import List, Dict
from copy import deepcopy
import pandas as pd


class Partitioner:
    def __init__(self, etf_model: NoAMCollection, frequency_table: FrequencyTable):
        self.etf_model = etf_model
        self.frequency_table = frequency_table
        self.aum = self.create_AUM()
        self.aam = self.create_AAM()

    def partition(self):
        # self.print_AAM()
        unused_attributes = self.get_unused_attributes()

        # Copy the AAM
        aam = deepcopy(self.aam)
        # Remove unused attributes from the AAM
        for unused_attribute in unused_attributes:
            for ek in aam.keys():
                del aam[ek][unused_attribute]
        for unused_attribute in unused_attributes:
            del aam[unused_attribute]

        # Create a mapping of id: aam key
        id_to_key = {}
        for idx, key in enumerate(aam.keys()):
            id_to_key[idx] = key

        # Convert AAM to adjacency matrix
        adjacency_matrix = []
        for ek1 in aam.keys():
            row = []
            for ek2 in aam.keys():
                row.append(aam[ek1][ek2])
            adjacency_matrix.append(row)

        # Perform vertical partitioning
        partitions = vertical_partition(adjacency_matrix)

        # Convert the partitions keys to ek keys
        partition_keys = []
        for partition in partitions:
            partition_keys.append([id_to_key[key] for key in partition])
        # Add the unused attributes to the partitions
        if unused_attributes:
            partition_keys.append(list(unused_attributes))

        return partition_keys

    def create_AUM(self) -> Dict[str, Dict[str, int]]:
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

    def create_AAM(self) -> Dict[str, Dict[str, float]]:
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
        Print AUM using pandas DataFrame for better alignment and presentation
        """
        # Convert AUM to DataFrame
        aum_df = pd.DataFrame(self.aum).T  # Transpose to get queries as rows
        # Print DataFrame
        print(aum_df.to_string())
        # Output to file txt
        with open(f"aum_{self.etf_model.name}.txt", "w") as f:
            f.write(aum_df.to_string())

    def print_AAM(self):
        """
        Print AAM using pandas DataFrame for better alignment and presentation
        """
        # Convert AAM to DataFrame
        aam_df = pd.DataFrame(self.aam)
        # Print DataFrame
        print(aam_df.to_string())
        # Output to file txt
        with open(f"aam_{self.etf_model.name}.txt", "w") as f:
            f.write(aam_df.to_string())

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
