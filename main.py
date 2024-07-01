from reader import Reader
from aggregate.aggregate import Aggregator
from aggregate.optimizer import Optimizer
from noam.converter import Converter

reader = Reader("schemas/perpustakaan")
class_diagram, queries, frequency_table = reader.read()
agg = Aggregator(class_diagram, queries, frequency_table)
agg.create_optimized_trees()
