from model.aggtree import AggNode
from model.frequency import FrequencyTable


class CostUtil:
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
                count *= CostUtil.count_to_root(parent)
        return count

    @staticmethod
    def count_from_agg_tree(node: AggNode) -> int:
        """
        Calculate the count of nodes from the aggregate tree
        Thus, the count is stopped on the normalized node (or root node)
        formally: Pi count(nk-1, nk) for 1 < k <= i
        """
        count = 1
        if node.parent is not None:
            parent = node.parent
            rel_tuple = parent.get_tuple_of_node(node)
            count *= rel_tuple.next_arrity
            if not parent.is_root:
                count *= CostUtil.count_from_agg_tree(parent)
        return count

    @staticmethod
    def delta_cost(freq_table: FrequencyTable, node: AggNode) -> int:
        """
        Calculate the delta cost of the node if the node is normalized from the aggregate tree
        positive value means the cost is decreased
        """

        # Total Cw (This and descendants)
        total_cw = node.update_cost * freq_table.get_frequency(node.klass.name)
        for child in node.children:
            total_cw += child.rel_update_cost * freq_table.get_frequency(child.rel.name)
            total_cw += CostUtil.total_cw(freq_table, child.node)

        print(f"Total Cw: {total_cw}")
        print(f"Update Cost: {node.update_cost}")
        # Delta Cw
        delta_cw = total_cw - (total_cw / node.update_cost)

        # Delta Cr = cr
        delta_cr = (1 - CostUtil.count_from_agg_tree(node)) * freq_table.get_frequency(
            node.klass.name
        )
        print(f"Delta Cw: {delta_cw}")
        print(f"Delta Cr: {delta_cr}")

        return delta_cw + delta_cr

    @staticmethod
    def total_cw(freq_table: FrequencyTable, node: AggNode) -> int:
        """
        Calculate the total write cost of the node and its descendants
        """
        total_cw = node.update_cost * freq_table.get_frequency(node.klass.name)
        for child in node.children:
            total_cw += child.rel_update_cost * freq_table.get_frequency(child.rel.name)
            total_cw += CostUtil.total_cw(freq_table, child.node)
        return total_cw
