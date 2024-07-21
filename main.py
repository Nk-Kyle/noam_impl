from reader import Reader
from aggregate.aggregate import Aggregator
from aggregate.optimizer import Optimizer
from noam.converter import Converter

reader = Reader("schemas/perpustakaan")
class_diagram, query_doc, frequency_table = reader.read()
agg = Aggregator(class_diagram, query_doc, frequency_table)
agg_trees = agg.create_optimized_trees()
converter = Converter(frequency_table)
for agg_tree in agg_trees:
    etf = converter.aggregate_to_etf(agg_tree)
    # etf.print_schema()
    partitioned = converter.etf_to_partition(etf)
    partitioned.print_schema()
