from test.generator.const import BOOK_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Query 1
    # Search Book loan detail by book_id

    # Generate n_run random book_id
    book_ids = random.sample(range(1, BOOK_COUNT), n_run)

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_book = mongo_client["etf"]["book"]
    start_time = time.time()

    for book_id in book_ids:
        book_data = mongo_db_etf_book.find_one({"_id": book_id}, {"Loan": 1})

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_book = mongo_client["aggregate"]["book"]
    start_time = time.time()

    for book_id in book_ids:
        book_data = mongo_db_aggregate_book.find_one({"_id": book_id}, {"P0_Loan": 1})

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_loan = mongo_client["baseline"]["loan"]
    start_time = time.time()

    for book_id in book_ids:
        loans_with_returns = mongo_db_baseline_loan.aggregate(
            [
                {"$match": {"bookID": book_id}},
                {
                    "$project": {
                        "_id": 1,
                        "loanedAt": 1,
                    }
                },
                {
                    "$lookup": {
                        "from": "return",
                        "localField": "_id",
                        "foreignField": "loanID",
                        "as": "returns",
                    }
                },
                {"$unwind": "$returns"},
                {
                    "$project": {
                        "_id": 1,
                        "loanedAt": 1,
                        "returns._id": 1,
                        "returns.returnedAt": 1,
                    }
                },
            ]
        )
        list(loans_with_returns)

    end_time = time.time()
    print(
        f"MongoDB (Baseline) Average Average: {(end_time - start_time)/n_run} seconds"
    )

    # RiakDB
    # ETF Model
    riak_db_etf_book = riak_client.bucket_type("etf").bucket("book")

    start_time = time.time()
    for book_id in book_ids:
        book_data = riak_db_etf_book.get(f"{book_id}_Loan").data

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO Model
    riak_db_eao_book = riak_client.bucket_type("eao").bucket("book")

    start_time = time.time()
    for book_id in book_ids:
        book_data = riak_db_eao_book.get(str(book_id)).data

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    riak_db_aggregate_book = riak_client.bucket_type("aggregate").bucket("book")

    start_time = time.time()
    for book_id in book_ids:
        book_data = riak_db_aggregate_book.get(f"{book_id}_P0_Loan").data

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    print(f"RiakDB (Baseline): Inapplicable")
