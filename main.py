from reader import Reader
from aggregate.aggregate import Aggregator
from aggregate.optimizer import Optimizer
from aggregate.cost import CostUtil

reader = Reader("schemas/perpustakaan")
class_diagram, queries, frequency_table = reader.read()
agg = Aggregator(class_diagram, queries, frequency_table)
agg.aggregate_relationship()
agg.create_aggregate_trees()
Optimizer(frequency_table, agg.agg_trees).partition()
