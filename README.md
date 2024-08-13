# NoAM Implementation Library

## About

This library is an implementation on modelling NoAM logic models from conceptual model. Implementing aggregation and partitioning parts described in NoAM modelling.

## Features

This library has three main features with respect to NoAM modelling:

1. Reading the conceptual model. UML Class Diagram with frequency and query document is used for conceptual model informations. The reading process is done through noam_impl.reader.Reader class.
2. Aggregating. Aggregating the class is done through DDD concepts and aggregation method developed by Chen L. et al. (2022) with some adjustments. This process is done through noam_impl.aggregate.aggregate.Aggregator
3. Convertion. Converting the aggregate trees resulting from Aggregator to three NoAM Logic Models: ETF, EAO, and Aggregate Partitioning. Partitioning algorithm uses method developed by Navathe & Ra (1989)

## Example

Example program can be seen in examples/example.py

## References (Readings)

-   Atzeni, P., Francesca, B., Cabibbo, L., & Torlone, R. (2020). Data modeling in the NoSQL world. Computer Standards & Interfaces, 103149.
-   Chen, L., Davoudian, A., & Liu, M. (2022). A workload-driven method for designing aggregate-oriented NoSQL. Data & Knowledge Engineering 142.
-   Evans, E. (2003). Domain-Driven Design: Tackling Complexity. Pearson Education.
-   Navathe, S. B., & Ra, M. (1989). Vertical Partitioning for Database Design: A Graphical Algorithm. Proceedings of the 1989 ACM SIGMOD International Conference on Management of Data, (pp. 440-450).
