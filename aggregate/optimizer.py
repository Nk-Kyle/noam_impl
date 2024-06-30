from typing import List, Tuple
from model.frequency import FrequencyTable
from model.aggtree import AggTree, AggNode


class Optimizer:
    def __init__(self, frequency_table: FrequencyTable, agg_trees: List[AggTree]):
        self.frequency_table = frequency_table
        self.agg_trees = agg_trees

    def normalize(node: AggNode) -> Tuple[AggTree, AggTree]:
        """
        Normalize the aggregate tree at node creating two separate trees
        tree 1: agg_tree with node normalized
        tree 2: node as a separate tree and its children
        """
        node.is_root = True
        parent = node.parent

        # Set the relationship tuple to normalized
        # to give information on the need of identity
        parent.get_tuple_of_node(node).normalized = True

    @staticmethod
    def count_to_root(node: AggNode) -> int:
        """
        Calculate the count of nodes to the root even if the node is normalized
        formally: Pi count(nk, nk-1) for 1 < k <= i
        """
        count = 1
        if node.parent is not None:
            parent = node.parent
            rel_tuple = parent.get_tuple_of_node(node)
            count *= rel_tuple.prev_arrity
            if parent.parent is not None:
                count *= Optimizer.count_to_root(parent)
        return count

    @staticmethod
    def count_from_agg_tree(node: AggNode) -> int:
        """
        Calculate the count of nodes from the aggregate tree
        Thus, the count is stopped on the normalized node (or root node)
        """
        count = 1
        if node.parent is not None:
            parent = node.parent
            rel_tuple = parent.get_tuple_of_node(node)
            count *= rel_tuple.next_arrity
            if not parent.is_root:
                count *= Optimizer.count_from_agg_tree(parent)
        return count
