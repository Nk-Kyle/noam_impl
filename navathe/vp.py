from typing import List
from model.partition import PartitionNode, PartitionEdge


def partition(adjacency_matrix: List[List[int]]):

    # Define the adjacency matrix
    # AA_matrix[a][b] = weight of the edge between a and b
    AA_matrix = adjacency_matrix

    tree = PartitionNode(0)
    tail_node = tree
    head_node = tree

    unused_nodes = set(range(1, len(AA_matrix)))
    node_mapping = {0: head_node}

    affinity_idx = 1

    while unused_nodes:
        # Get the edges connected to tail_node and head_node
        # Place it in a list of Edge objects
        edges: List[PartitionEdge] = []
        for idx, val in enumerate(AA_matrix[tail_node.key]):
            # Check if the edge should be considered
            if (
                idx == tail_node.key
                or (tail_node.prev_node is not None and idx == tail_node.prev_node.key)
                or (tail_node.next_node is not None and idx == tail_node.next_node.key)
            ):
                continue

            edges.append(PartitionEdge(idx, tail_node.key, val))

        for idx, val in enumerate(AA_matrix[head_node.key]):
            # Check if the edge should be considered
            if (
                idx == head_node.key
                or (head_node.prev_node is not None and idx == head_node.prev_node.key)
                or (head_node.next_node is not None and idx == head_node.next_node.key)
            ):
                continue

            edges.append(PartitionEdge(idx, head_node.key, val))

        # Sort the edges by weight
        edges.sort(key=lambda x: x.weight, reverse=True)

        while True:  # Loop until a node is added to the tree
            # Get the edge with the largest weight
            edge = edges.pop(0)

            # Check if the edge is not connected to the tree
            # That is the node is not in the tree
            if edge.my_key not in node_mapping:
                # Create a new node
                new_node = PartitionNode(edge.my_key)

                # Add the new node to the tree, depending on the edge
                if edge.from_node_key == tail_node.key:
                    tail_node.prev_node = new_node
                    new_node.next_node = tail_node
                    tail_node.prev_link = edge.weight
                    new_node.next_link = edge.weight
                    tail_node = new_node
                else:  # edge.from_node_key == head_node.key
                    head_node.next_node = new_node
                    new_node.prev_node = head_node
                    head_node.next_link = edge.weight
                    new_node.prev_link = edge.weight
                    head_node = new_node

                # Update the node_mapping
                node_mapping[edge.my_key] = new_node
                unused_nodes.remove(edge.my_key)
                # print(
                #     f"Added node {edge.my_key + 1} from node {edge.from_node_key + 1}"
                # )
                # tail_node.print_tree()
                break

            else:  # There is a cycle
                # print(
                #     f"Cycle detected when trying to add node {edge.my_key + 1} from node {edge.from_node_key + 1}"
                # )

                # Check if the from_node is in a affinity chain
                from_node = node_mapping[edge.from_node_key]
                if from_node.affinity_chain == 0:

                    # Extending an affinity chain with from_node
                    if node_mapping[edge.my_key].affinity_chain != 0:

                        aff_idx_to_extend = node_mapping[edge.my_key].affinity_chain
                        # Find the smallest edge in the affinity chain
                        smallest_edge = float("inf")
                        if edge.from_node_key == tail_node.key:
                            node = node_mapping[edge.my_key].prev_node
                            while node and node.affinity_chain == aff_idx_to_extend:
                                if node.next_link < smallest_edge:
                                    smallest_edge = node.next_link
                                node = node.prev_node
                        else:  # edge.from_node_key == head_node.key
                            node = node_mapping[edge.my_key].next_node
                            while node and node.affinity_chain == aff_idx_to_extend:
                                if node.prev_link < smallest_edge:
                                    smallest_edge = node.prev_link
                                node = node.next_node
                        # tail_node.print_tree()
                        # print(f"Smallest edge in the affinity chain: {smallest_edge}")

                        if edge.weight < smallest_edge:
                            # Cant extend the affinity chain since the edge is smaller
                            # print(
                            #     "Cant extend the affinity chain since the edge is smaller",
                            #     edge.weight,
                            #     smallest_edge,
                            # )
                            continue

                    # print(
                    #     f"Creating a new affinity chain for node {edge.my_key + 1} from node {edge.from_node_key + 1}"
                    # )

                    # Create a new affinity chain
                    from_node.affinity_chain = affinity_idx
                    affinity_idx += 1

                    # to node will be in the same affinity chain
                    to_node = node_mapping[edge.my_key]
                    to_node.affinity_chain = from_node.affinity_chain

                    # all nodes in between will be in the same affinity chain
                    if edge.from_node_key == tail_node.key:
                        node = to_node.prev_node
                        # Update the affinity chain of all nodes in between
                        while node:
                            node.affinity_chain = from_node.affinity_chain
                            node = node.prev_node
                    else:  # edge.from_node_key == head_node.key
                        node = to_node.next_node
                        # Update the affinity chain of all nodes in between
                        while node:
                            node.affinity_chain = from_node.affinity_chain
                            node = node.next_node
                    # tail_node.print_tree()
                else:
                    # We are trying to extend an existing affinity chain
                    # If in different affinity chains, edge is not considered
                    # Check if the to_node is already in an affinity chain
                    if node_mapping[edge.my_key].affinity_chain != 0:
                        # print(f"Already in an affinity chain")
                        continue

                    # If in the same affinity chain, edge is considered
                    # Check if the edge is larger or uqual to the smallest edge in the affinity chain
                    # If it is, the edge is added to the tree

                    # Find the smallest edge in the affinity chain
                    aff_idx_to_extend = node_mapping[edge.my_key].affinity_chain
                    smallest_edge = float("inf")
                    if edge.from_node_key == tail_node.key:
                        node = node_mapping[edge.my_key].prev_node
                        while node and node.affinity_chain == aff_idx_to_extend:
                            if node.next_link < smallest_edge:
                                smallest_edge = node.next_link
                            node = node.prev_node
                    else:  # edge.from_node_key == head_node.key
                        node = node_mapping[edge.my_key].next_node
                        while node and node.affinity_chain == aff_idx_to_extend:
                            if node.prev_link < smallest_edge:
                                smallest_edge = node.prev_link
                            node = node.next_node
                    # print(f"Smallest edge in the affinity chain: {smallest_edge}")

                    if edge.weight < smallest_edge:
                        # Cant extend the affinity chain since the edge is smaller
                        # print(
                        #     "Cant extend the affinity chain since the edge is smaller",
                        #     edge.weight,
                        #     smallest_edge,
                        # )
                        continue

                    # Check if the edge is larger or equal to the smallest edge
                    if edge.weight >= smallest_edge:
                        # print(
                        #     f"Extended affinity chain {from_node.affinity_chain} with node {edge.my_key + 1}"
                        # )
                        # To node will be in the same affinity chain and also the nodes in between
                        node_mapping[edge.my_key].affinity_chain = (
                            from_node.affinity_chain
                        )
                        if edge.from_node_key == tail_node.key:
                            node = tail_node.next_node
                            while node.key != head_node.key:
                                node.affinity_chain = from_node.affinity_chain
                                node = node.next_node
                        else:  # edge.from_node_key == head_node.key
                            node = head_node.prev_node
                            while node.key != tail_node.key:
                                node.affinity_chain = from_node.affinity_chain
                                node = node.prev_node

    return tail_node.get_partitions()
