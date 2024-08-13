from noam_impl.reader import Reader
from noam_impl.aggregate.aggregate import Aggregator
from noam_impl.noam.converter import Converter

reader = Reader("schemas/perpustakaan")
class_diagram, query_doc, frequency_table = reader.read()
agg = Aggregator(class_diagram, query_doc, frequency_table)
agg_trees = agg.create_optimized_trees()
converter = Converter(frequency_table)
for agg_tree in agg_trees:
    etf = converter.aggregate_to_etf(agg_tree)
    eao = converter.etf_to_eao(etf)
    etf.export_schema_as_json()
    eao.export_schema_as_json()
    partitioned = converter.etf_to_partition(etf)
    partitioned.export_schema_as_json()
