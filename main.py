from reader import Reader
from aggregate.aggregate import Aggregator

reader = Reader("schemas/perpustakaan")
class_diagram, queries, frequency_table = reader.read()
agg = Aggregator(class_diagram, queries, frequency_table)
agg.aggregate_relationship()
