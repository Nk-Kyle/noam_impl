from reader import Reader
from aggregate.aggregate import Aggregator
from aggregate.optimizer import Optimizer
from noam.converter import Converter

reader = Reader("schemas/perpustakaan")
class_diagram, query_doc, frequency_table = reader.read()
agg = Aggregator(class_diagram, query_doc, frequency_table)
agg_trees = agg.create_optimized_trees()
converter = Converter(class_diagram)
for agg_tree in agg_trees:
    print("=====================================")
    converter.aggregate_to_etf(agg_tree)
