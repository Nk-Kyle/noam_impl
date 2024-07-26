from test.generator.const import BOOK_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Query 2
    # Search Book detail by book_id

    # Generate n_run random book_id
    book_ids = set()
    while len(book_ids) < n_run:
        book_id = random.randint(1, BOOK_COUNT)
        if book_id not in book_ids:
            book_ids.add(book_id)

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_book = mongo_client["etf"]["book"]
    start_time = time.time()

    for book_id in book_ids:
        book = mongo_db_etf_book.aggregate(
            [
                {"$match": {"_id": book_id}},
                {
                    "$lookup": {
                        "from": "publisher",
                        "localField": "Publisher_id",
                        "foreignField": "_id",
                        "as": "Publisher",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "description": 1,
                        "language": 1,
                        "keywords": 1,
                        "Author": 1,
                        "Publisher": 1,
                        "Category": 1,
                    }
                },
            ]
        )
        list(book)  # Cast to get object

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_book = mongo_client["aggregate"]["book"]
    start_time = time.time()

    for book_id in book_ids:
        book = mongo_db_aggregate_book.aggregate(
            [
                {"$match": {"_id": book_id}},
                {
                    "$lookup": {
                        "from": "publisher",
                        "localField": "P1.Publisher_id",
                        "foreignField": "_id",
                        "as": "Publisher",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "P1": 1,
                        "P2": 1,
                        "Publisher": 1,
                    }
                },
            ]
        )
        list(book)  # Cast to get object

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_book = mongo_client["baseline"]["book"]
    start_time = time.time()

    for book_id in book_ids:
        book = mongo_db_baseline_book.aggregate(
            [
                {"$match": {"_id": book_id}},
                {
                    "$lookup": {
                        "from": "publisher",
                        "localField": "publisherID",
                        "foreignField": "_id",
                        "as": "Publisher",
                    }
                },
                {
                    "$lookup": {
                        "from": "author",
                        "localField": "authorID",
                        "foreignField": "_id",
                        "as": "Author",
                    }
                },
                {
                    "$project": {
                        "publisherID": 0,
                        "authorID": 0,
                        "Author.bookID": 0,
                    }
                },
            ]
        )
        list(book)  # Cast to get object

    end_time = time.time()
    print(f"MongoDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")

    # RiakDB
    # ETF Model
    riak_db_etf_book = riak_client.bucket_type("etf").bucket("book")
    riak_db_etf_publisher = riak_client.bucket_type("etf").bucket("publisher")
    keys = [
        "name",
        "language",
        "description",
        "keywords",
        "Author",
        "Category",
        "Publisher_id",
    ]

    start_time = time.time()
    for book_id in book_ids:
        book_data = {}
        for key in keys:
            book_data[key] = riak_db_etf_book.get(f"{book_id}_{key}").data

        publisher_id = book_data["Publisher_id"]
        book_data["publisher_name"] = riak_db_etf_publisher.get(
            f"{publisher_id}_name"
        ).data
        book_data["publisher_contact"] = riak_db_etf_publisher.get(
            f"{publisher_id}_contact"
        ).data

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO Model
    riak_db_eao_book = riak_client.bucket_type("eao").bucket("book")
    ria_db_eao_publisher = riak_client.bucket_type("eao").bucket("publisher")

    start_time = time.time()
    for book_id in book_ids:
        book = riak_db_eao_book.get(str(book_id)).data

        publisher_id = book["Publisher_id"]
        book["publisher_name"] = ria_db_eao_publisher.get(f"{publisher_id}_name").data
        book["publisher_contact"] = ria_db_eao_publisher.get(
            f"{publisher_id}_contact"
        ).data

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    riak_db_aggregate_book = riak_client.bucket_type("aggregate").bucket("book")
    riak_db_aggregate_publisher = riak_client.bucket_type("aggregate").bucket(
        "publisher"
    )

    start_time = time.time()
    for book_id in book_ids:
        book = riak_db_aggregate_book.get(f"{book_id}_P1").data
        book.update(riak_db_aggregate_book.get(f"{book_id}_P2").data)

        publisher_id = book["Publisher_id"]
        book["publisher"] = riak_db_aggregate_publisher.get(f"{publisher_id}").data

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    riak_db_baseline_book = riak_client.bucket_type("baseline").bucket("book")
    riak_db_baseline_publisher = riak_client.bucket_type("baseline").bucket("publisher")
    riak_db_baseline_book_category = riak_client.bucket_type("baseline").bucket(
        "book_category"
    )
    riak_db_baseline_category = riak_client.bucket_type("baseline").bucket("category")
    keys = [
        "name",
        "description",
        "language",
        "keywords",
        "publisher_id",
    ]

    start_time = time.time()
    book_data = {}
    for book_id in book_ids:
        for key in keys:
            book_data[key] = riak_db_baseline_book.get(f"{book_id}_{key}").data
        publisher_id = book_data["publisher_id"]
        book_data["publisher_name"] = riak_db_baseline_publisher.get(
            f"{publisher_id}_name"
        ).data
        book_data["publisher_contact"] = riak_db_baseline_publisher.get(
            f"{publisher_id}_contact"
        ).data

        book_data["category"] = []
        categories = riak_db_baseline_book_category.get(f"book_{book_id}_category").data
        for category_id in categories:
            category_data = {}
            category_data["name"] = riak_db_baseline_category.get(
                f"{category_id}_name"
            ).data
            category_data["subcategory"] = riak_db_baseline_category.get(
                f"{category_id}_subcategory"
            ).data
            book_data["category"].append(category_data)

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
