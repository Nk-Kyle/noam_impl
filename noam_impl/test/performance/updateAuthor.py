from test.generator.const import AUTHOR_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start
from faker import Faker

fake = Faker()


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Update Author

    # Random author ids
    author_ids = random.sample(range(1, AUTHOR_COUNT), n_run)
    author_update_data = {
        str(author_id): {
            "name": fake.name(),
        }
        for author_id in author_ids
    }

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_author = mongo_client["etf"]["author"]
    mongo_db_etf_book = mongo_client["etf"]["book"]
    start_time = time.time()

    for author_id, data in author_update_data.items():
        author_id = int(author_id)
        mongo_db_etf_author.update_one(
            {"_id": author_id},
            {
                "$set": {
                    "name": data["name"],
                }
            },
        )

        mongo_db_etf_book.update_many(
            {"Author.id": author_id},
            {"$set": {"Author.$.name": data["name"]}},
        )

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_author = mongo_client["aggregate"]["author"]
    mongo_db_aggregate_book = mongo_client["aggregate"]["book"]
    start_time = time.time()

    for author_id, data in author_update_data.items():
        author_id = int(author_id)
        mongo_db_aggregate_author.update_one(
            {"_id": author_id},
            {
                "$set": {
                    "name": data["name"],
                }
            },
        )

        mongo_db_aggregate_book.update_many(
            {"P1.Author.id": author_id},
            {"$set": {"P1.Author.$.name": data["name"]}},
        )

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_author = mongo_client["baseline"]["author"]
    start_time = time.time()

    for author_id, data in author_update_data.items():
        author_id = int(author_id)
        mongo_db_baseline_author.update_one(
            {"_id": author_id},
            {
                "$set": {
                    "name": data["name"],
                }
            },
        )

    end_time = time.time()
    print(
        f"MongoDB (Baseline) Average Average: {(end_time - start_time)/n_run} seconds"
    )

    # RiakDB
    # ETF
    riak_db_etf_author = riak_client.bucket_type("etf").bucket("author")
    riak_db_etf_book = riak_client.bucket_type("etf").bucket("book")
    start_time = time.time()

    for author_id, data in author_update_data.items():
        author_name = riak_db_etf_author.get(f"{author_id}_name")
        author_name.data = data["name"]

        # Update book
        author_book_ids = riak_db_etf_author.get(f"{author_id}_Book_id")
        for book_id in author_book_ids.data:
            book_author = riak_db_etf_book.get(f"{book_id}_Author")
            for author_data in book_author.data:
                if author_data["id"] == author_id:
                    author_data["name"] = data["name"]
                    break
            book_author.store()

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO
    riak_db_eao_author = riak_client.bucket_type("eao").bucket("author")
    riak_db_eao_book = riak_client.bucket_type("eao").bucket("book")
    start_time = time.time()

    for author_id, data in author_update_data.items():
        d = riak_db_eao_author.get(str(author_id))
        d.data.update(data)
        for book_id in d.data["Book_id"]:
            book = riak_db_eao_book.get(str(book_id))
            for author_data in book.data["Author"]:
                if author_data["id"] == author_id:
                    author_data["name"] = data["name"]
                    break
            book.store()
        d.store()

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate
    riak_db_aggregate_author = riak_client.bucket_type("aggregate").bucket("author")
    riak_db_aggregate_book = riak_client.bucket_type("aggregate").bucket("book")
    start_time = time.time()

    for author_id, data in author_update_data.items():
        d = riak_db_aggregate_author.get(f"{author_id}")
        d.data["name"] = data["name"]
        for book_id in d.data["Book_id"]:
            book = riak_db_aggregate_book.get(f"{book_id}_P1")
            for author_data in book.data["Author"]:
                if author_data["id"] == author_id:
                    author_data["name"] = data["name"]
                    break
            book.store()
        d.store()

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline
    riak_db_baseline_author = riak_client.bucket_type("baseline").bucket("author")
    start_time = time.time()

    for author_id, data in author_update_data.items():
        for key, value in data.items():
            d = riak_db_baseline_author.get(f"{author_id}_{key}")
            d.data = value
            d.store()

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
