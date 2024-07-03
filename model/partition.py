from collections import defaultdict


class PartitionNode:
    def __init__(self, key, prev_node=None):
        self.key = key
        self.prev_node: PartitionNode = prev_node
        self.prev_link = 0
        self.next_node: PartitionNode = None
        self.next_link = 0

        self.affinity_chain = 0

    def print_tree(self):
        node = self
        while node is not None:
            print("V")
            print(f"Node {node.key + 1} (Affinity chain: {node.affinity_chain})")
            node = node.next_node

    def print_partitions(self):
        partitions = defaultdict(list)
        node = self
        while node is not None:
            if node.affinity_chain not in partitions:
                partitions[node.affinity_chain] = []
            partitions[node.affinity_chain].append(node.key)
            node = node.next_node

        for key, val in partitions.items():
            print(f"Partition {key}: {val}")


class PartitionEdge:
    def __init__(self, my_key, from_node_key, weight):
        self.my_key = my_key
        self.from_node_key = from_node_key
        self.weight = weight
