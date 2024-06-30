from model.klass import Class
from typing import Dict, Set, Tuple


class Utils:
    @staticmethod
    def populate_parent(child: Class, parent: Class):
        """
        Populate the parent class by adding the child class attributes and a type attribute
        """
        parent.add_attribute(child.attributes)
        parent.add_attribute("type")

    @staticmethod
    def get_class_aggregate(
        agg_map: Dict[Class, Set[Class]], klass: Class
    ) -> Tuple[Class, Set[Class]]:
        """
        Get the aggregate relationship of a class

        Parameters
        ----------
        class_ : Class
            The class to get the aggregate relationship

        Returns
        -------
        Tuple[Class, Set[Class]]
            The root class and the set of classes that are aggregated
        """

        for root, children in agg_map.items():
            if klass in children:
                return root, children
        return klass, {klass}

    @staticmethod
    def print_aggregate(agg_map: Dict[Class, Set[Class]]):
        for root, children in agg_map.items():
            print(f"Root: {root.name}")
            for child in children:
                print(f"Member: {child.name}")
            print("")
