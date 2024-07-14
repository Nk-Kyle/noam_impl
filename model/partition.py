from collections import defaultdict
from typing import List


class PartitionNode:
    def __init__(self, key, prev_node=None):
        self.key = key
        self.prev_node: PartitionNode = prev_node
        self.prev_link = 0
        self.next_node: PartitionNode = None
        self.next_link = 0

        self.affinity_chain = 0

    def print_tree(self):
        print("Printing tree")
        node = self
        while node is not None:
            print(f"Node {node.key + 1} (Affinity chain: {node.affinity_chain})")
            if node.next_node is not None:
                print(f"V ({node.next_link})")
            node = node.next_node
        print("End of tree")
        print()

    from collections import defaultdict

    def get_partitions(self) -> List[List[int]]:
        """
        Get the partitions of the tree based on the affinity chain
        """
        partitions = defaultdict(list)
        node = self
        zero_partition_counter = 1
        last_affinity_chain = None

        while node is not None:
            if node.affinity_chain == 0:
                # Use a unique key for each sequence of 0 values
                partition_key = f"0_{zero_partition_counter}"
            else:
                partition_key = node.affinity_chain
                # If transitioning from 0 to a non-zero value, increment the counter
                if last_affinity_chain == 0:
                    zero_partition_counter += 1

            partitions[partition_key].append(node.key)
            last_affinity_chain = node.affinity_chain
            node = node.next_node

        # for key, val in partitions.items():
        #     print(f"Partition {key}: {val}")

        return [val for val in partitions.values()]


class PartitionEdge:
    def __init__(self, my_key, from_node_key, weight):
        self.my_key = my_key
        self.from_node_key = from_node_key
        self.weight = weight
