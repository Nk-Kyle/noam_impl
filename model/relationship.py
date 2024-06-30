from utils.choices import RelType
from .klass import Class


class Relationship:
    REL_INDEX = 0

    def __init__(
        self,
        id: str,
        from_class: Class,
        to_class: Class,
        from_arrity: int,
        to_arrity: int,
        type: RelType,
        name: str,
    ):
        self.id = id
        self.from_class = from_class
        self.to_class = to_class
        self.from_arrity = from_arrity
        self.to_arrity = to_arrity
        self.type = type
        self.name = name

        if self.name is None and self.type != RelType.GENERALIZATION:
            self.name = f"R{Relationship.REL_INDEX}"
            Relationship.REL_INDEX += 1
        elif self.type == RelType.GENERALIZATION:
            self.name = f"G{from_class.name}:{to_class.name}"

    def count(self, klass: Class):
        if klass == self.from_class:
            return self.from_arrity
        elif klass == self.to_class:
            return self.to_arrity
        else:
            raise ValueError(f"Class {klass.name} is not part of the relationship")

    def __str__(self):
        return f"[Relationship] {self.from_class.name} -> {self.to_class.name} ({self.from_arrity}, {self.to_arrity}) {self.type.name} ({self.name})"
