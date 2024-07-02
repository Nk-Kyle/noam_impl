from typing import List, Tuple
from model.frequency import FrequencyTable
from model.aggtree import AggTree, AggNode
from aggregate.cost import CostUtil
from model.klass import Class
from typing import Dict


class Optimizer:
    def __init__(self, frequency_table: FrequencyTable, agg_trees: List[AggTree]):
        self.frequency_table = frequency_table
        self.agg_trees = agg_trees
        self.result: Dict[Class, AggTree] = {}
        self.set_initial_cost()

    def optimize(self) -> List[AggTree]:
        """
        Optimize the aggregate tree
        """
        self.partition()
        return self.denormalize()

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
        node.main_root.query_map[node.main_root.label][node.klass].add(node.klass.pk)
        node.is_root = True

        # Set the relationship tuple to normalized
        # to give information on the need of identity
        parent = node.parent
        parent.normalized_children.append(parent.get_tuple_of_node(node))
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
            # DEBUG
            # print(
            #     f"Partitioning {max_node.klass.name} from query {max_node.main_root.label} in {agg_node.klass.name}"
            # )
            # print(f"Delta Cost: {cost_map[max_node]}")
            self.normalize(max_node)
            self.partition_agg_tree(max_node)
            self.partition_agg_tree(agg_node)

    def denormalize(self) -> List[AggTree]:
        """
        Create new Aggregate Tree from the normalized node
        """
        # DEBUG
        # for agg_tree in self.agg_trees:
        #     agg_tree.print_tree()
        new_agg_trees: List[AggTree] = []

        new_agg_trees.extend(self.agg_trees)

        # Create new Aggregate Tree from the normalized node

        # Get the normalized nodes
        normalized_nodes: List[AggNode] = []
        for agg_tree in self.agg_trees:
            for node in agg_tree.traverse(agg_tree.root):
                if node.is_root and node.parent is not None:
                    normalized_nodes.append(node)

        for node in normalized_nodes:
            new_agg_tree = AggTree(node.main_root.label, node.klass)
            new_agg_trees.append(new_agg_tree)

        # Merge trees
        for agg_tree in new_agg_trees:
            # If the tree is not in the result, add it
            if agg_tree.root.klass not in self.result:
                self.result[agg_tree.root.klass] = agg_tree
            else:  # Merge the tree to the existing tree
                self.merge_tree(self.result[agg_tree.root.klass], agg_tree)

        # Remove the normalized nodes
        for agg_tree in self.result.values():
            self.remove_normalized_nodes(agg_tree.root)

        # DEBUG
        # print("================ Result ================")
        # for agg_tree in self.result.values():
        #     agg_tree.print_tree()

        return list(self.result.values())

    def merge_tree(self, tree1: AggTree, tree2: AggTree):
        """
        Merge two aggregate trees leaving any normalized node and its children
        tree1 as the base tree

        Precondition:
        - The tree1 and tree2 have the same root class
        """
        # Update tree2 query map to tree1
        for query, class_map in tree2.query_map.items():
            for klass, attributes in class_map.items():
                tree1.query_map[query][klass].update(attributes)

        tree1.applied_queries.add(tree2.label)
        self.merge_node(tree1.root, tree2.root)

    def merge_node(self, node1: AggNode, node2: AggNode):
        """
        Merge two nodes
        """
        node1_children_klass = [child.node.klass for child in node1.children]
        node1.normalized_children += node2.normalized_children
        for child in node2.children:
            if child.node.is_root:
                # Skip the normalized node
                continue

            if child.node.klass in node1_children_klass:
                self.merge_node(node1.get_child_by_class(child.node.klass), child.node)
            else:
                node1.add_child(child)

    def remove_normalized_nodes(self, node: AggNode):
        """
        Remove the normalized nodes from the aggregate tree
        """
        for child in node.children:
            if child.normalized:
                node.children.remove(child)
            else:
                self.remove_normalized_nodes(child.node)

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
