from model.query import Query, QueryNode, RelNodeTuple
from model.aggtree import AggTree, AggNode, RelAggNodeTuple


class Transformer:
    @classmethod
    def create_aggtree_from_query(cls, query: Query) -> AggTree:
        """
        Duplicate the query tree to AggTree

         Query tree:
         - Query
             - QueryNode
                 - RelNodeTuple

         AggTree:
         - AggTree
            - AggNode
                - RelAggNodeTuple
        """

        agg_tree = AggTree(query.name, query.root.klass)
        cls.__transform_node(query.root, agg_tree.root)
        return agg_tree

    @classmethod
    def __transform_node(cls, q_node: QueryNode, a_node: AggNode):
        """
        Transform the QueryNode to AggNode
        """
        for q_child in q_node.children:
            a_child = AggNode(q_child.node.klass, a_node.main_root, a_node)
            a_node.add_child(RelAggNodeTuple(q_child.rel, a_child))
            cls.__transform_node(q_child.node, a_child)
