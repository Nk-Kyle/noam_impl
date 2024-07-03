class PartitionNode:
    def __init__(self, key, prev_node=None):
        self.key = key
        self.prev_node: PartitionNode = prev_node
        self.prev_link = 0
        self.next_node: PartitionNode = None
        self.next_link = 0

        self.affinity_chain = 0


class Edge:
    def __init__(self, my_key, from_node_key, weight):
        self.my_key = my_key
        self.from_node_key = from_node_key
        self.weight = weight
