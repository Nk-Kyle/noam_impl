from typing import List, Tuple
from model.frequency import FrequencyTable
from model.aggtree import AggTree, AggNode
from aggregate.cost import CostUtil


class Optimizer:
    def __init__(self, frequency_table: FrequencyTable, agg_trees: List[AggTree]):
        self.frequency_table = frequency_table
        self.agg_trees = agg_trees
        self.set_initial_cost()

    def partition(self):
        """
        Partition the aggregate trees into subtress if necessary
        """
        for agg_tree in self.agg_trees:
            self.partition_agg_tree(agg_tree.root)

    def set_initial_cost(self):
        for agg_tree in self.agg_trees:
            self.set_initial_cost_agg_tree(agg_tree.root)

    @staticmethod
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

    def partition_agg_tree(self, agg_node: AggNode):
        """
        Partition the aggregate tree if necessary
        """
        cost_map = {}
        childs = agg_node.get_all_child_node()
        if len(childs) == 0:
            return
        for child in childs:
            cost_map[child] = CostUtil.delta_cost(self.frequency_table, child)
        max_node: AggNode = max(cost_map, key=cost_map.get)
        if cost_map[max_node] > 0:
            print(
                f"Partitioning {max_node.klass.name} from query {max_node.main_root.label} in {agg_node.klass.name}"
            )
            print(f"Delta Cost: {cost_map[max_node]}")
            self.normalize(max_node)
            self.partition_agg_tree(max_node)
            self.partition_agg_tree(agg_node)

    def set_initial_cost_agg_tree(self, agg_node: AggNode):
        """
        Set the initial cost for the aggregate tree
        """
        agg_node.read_cost = 1
        agg_node.update_cost = CostUtil.count_to_root(agg_node)

        for child in agg_node.children:
            # Set the cost for the relationship
            child.rel_update_cost = agg_node.update_cost
            self.set_initial_cost_agg_tree(child.node)
