from test.generator.const import BOOK_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start, string_to_list
from faker import Faker

fake = Faker()


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Update Book

    # Random book ids
    book_ids = random.sample(range(1, BOOK_COUNT), n_run)
    book_update_data = {
        str(book_id): {
            "name": fake.catch_phrase(),
            "keywords": str(fake.words(nb=5, unique=True)),
        }
        for book_id in book_ids
    }

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_book = mongo_client["etf"]["book"]
    mongo_db_etf_member = mongo_client["etf"]["member"]
    start_time = time.time()

    for book_id, data in book_update_data.items():
        book_id = int(book_id)
        mongo_db_etf_book.update_one(
            {"_id": book_id},
            {
                "$set": {
                    "name": data["name"],
                    "keywords": string_to_list(data["keywords"]),
                }
            },
        )

        mongo_db_etf_member.update_many(
            {"Loan.Book_id": book_id},
            {"$set": {"Loan.$.Book_name": data["name"]}},
        )

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_book = mongo_client["aggregate"]["book"]
    mongo_db_aggregate_member = mongo_client["aggregate"]["member"]
    start_time = time.time()

    for book_id, data in book_update_data.items():
        book_id = int(book_id)
        mongo_db_aggregate_book.update_one(
            {"_id": book_id},
            {
                "$set": {
                    "P1.name": data["name"],
                    "P2.keywords": string_to_list(data["keywords"]),
                }
            },
        )

        mongo_db_aggregate_member.update_many(
            {"P2_Loan.Book_id": book_id},
            {"$set": {"P2_Loan.$.Book_name": data["name"]}},
        )

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_book = mongo_client["baseline"]["book"]
    start_time = time.time()

    for book_id, data in book_update_data.items():
        book_id = int(book_id)
        mongo_db_baseline_book.update_one(
            {"_id": book_id},
            {
                "$set": {
                    "name": data["name"],
                    "keywords": string_to_list(data["keywords"]),
                }
            },
        )

    end_time = time.time()

    print(
        f"MongoDB (Baseline) Average Average: {(end_time - start_time)/n_run} seconds"
    )

    # RiakDB
    # ETF
    riak_db_etf_book = riak_client.bucket_type("etf").bucket("book")
    start_time = time.time()

    for book_id, data in book_update_data.items():
        for key, value in data.items():
            d = riak_db_etf_book.get(f"{book_id}_{key}")
            d.data = value
            d.store()

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO
    riak_db_eao_book = riak_client.bucket_type("eao").bucket("book")
    start_time = time.time()

    for book_id, data in book_update_data.items():
        d = riak_db_eao_book.get(str(book_id))
        d.data.update(data)
        d.store()

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate
    riak_db_aggregate_book = riak_client.bucket_type("aggregate").bucket("book")
    start_time = time.time()

    for book_id, data in book_update_data.items():
        p1 = riak_db_aggregate_book.get(f"{book_id}_P1")
        p1.data["name"] = data["name"]
        p2 = riak_db_aggregate_book.get(f"{book_id}_P2")
        p2.data["keywords"] = data["keywords"]
        p1.store()
        p2.store()

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline
    riak_db_baseline_book = riak_client.bucket_type("baseline").bucket("book")
    start_time = time.time()

    for book_id, data in book_update_data.items():
        for key, value in data.items():
            d = riak_db_baseline_book.get(f"{book_id}_{key}")
            d.data = value
            d.store()

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
