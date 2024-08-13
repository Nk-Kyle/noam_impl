from test.generator.const import AUTHOR_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Query 5
    # Search Author book detail by author_id

    # Generate n_run random author_id
    author_ids = random.sample(range(1, AUTHOR_COUNT), n_run)

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_author = mongo_client["etf"]["author"]
    start_time = time.time()

    for author_id in author_ids:
        author_with_books = mongo_db_etf_author.aggregate(
            [
                {"$match": {"_id": author_id}},
                {
                    "$lookup": {
                        "from": "book",
                        "localField": "Book_id",
                        "foreignField": "_id",
                        "as": "Book",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "Book._id": 1,
                        "Book.name": 1,
                        "Book.Publisher_id": 1,
                        "Book.Category": 1,
                    }
                },
                {"$unwind": "$Book"},
                {
                    "$lookup": {
                        "from": "publisher",
                        "localField": "Book.Publisher_id",
                        "foreignField": "_id",
                        "as": "Book.Publisher",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "Book": 1,
                    }
                },
            ]
        )
        list(author_with_books)

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_author = mongo_client["aggregate"]["author"]
    start_time = time.time()

    for author_id in author_ids:
        author_with_books = mongo_db_aggregate_author.aggregate(
            [
                {"$match": {"_id": author_id}},  # Match the author by ID
                {
                    "$lookup": {
                        "from": "book",
                        "localField": "Book_id",
                        "foreignField": "_id",
                        "as": "Book",
                    }
                },
                {"$unwind": "$Book"},  # Unwind the Book array
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "Book._id": 1,
                        "Book.P1.name": 1,
                        "Book.P1.Publisher_id": 1,
                        "Book.P1.Category": 1,
                    }
                },
                {
                    "$lookup": {
                        "from": "publisher",
                        "localField": "Book.P1.Publisher_id",
                        "foreignField": "_id",
                        "as": "Book.Publisher",
                    }
                },
                {"$unwind": "$Book.Publisher"},
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "Book": {
                            "id": "$Book._id",
                            "name": "$Book.P1.name",
                            "Publisher_id": "$Book.P1.Publisher_id",
                            "Publisher": {"name": "$Book.Publisher.name"},
                            "Category": "$Book.P1.Category",
                        },
                    }
                },
            ]
        )
        list(author_with_books)

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_author = mongo_client["baseline"]["author"]
    start_time = time.time()

    for author_id in author_ids:
        author_with_books = mongo_db_baseline_author.aggregate(
            [
                {"$match": {"_id": author_id}},
                {
                    "$lookup": {
                        "from": "book",
                        "localField": "bookID",
                        "foreignField": "_id",
                        "as": "Book",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "Book.id": 1,
                        "Book.name": 1,
                        "Book.publisherID": 1,
                        "Book.Category": 1,
                    }
                },
                {"$unwind": "$Book"},
                {
                    "$lookup": {
                        "from": "publisher",
                        "localField": "Book.publisherID",
                        "foreignField": "_id",
                        "as": "Book.Publisher",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "Book": 1,
                    }
                },
            ]
        )
        list(author_with_books)

    end_time = time.time()
    print(f"MongoDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")

    # RiakDB
    # ETF Model
    riak_db_etf_author = riak_client.bucket_type("etf").bucket("author")
    riak_db_etf_book = riak_client.bucket_type("etf").bucket("book")
    riak_db_etf_publisher = riak_client.bucket_type("etf").bucket("publisher")
    start_time = time.time()

    for author_id in author_ids:
        author_data = {}
        author_data["name"] = riak_db_etf_author.get(f"{author_id}_name").data
        author_book_ids = riak_db_etf_author.get(f"{author_id}_Book_id").data

        author_data["Book"] = []
        for book_id in author_book_ids:
            book_data = {}
            book_data["name"] = riak_db_etf_book.get(f"{book_id}_name").data
            book_data["Publisher_id"] = riak_db_etf_book.get(
                f"{book_id}_Publisher_id"
            ).data
            book_data["Publisher_name"] = riak_db_etf_publisher.get(
                f"{book_data['Publisher_id']}_name"
            ).data
            book_data["Publisher_contact"] = riak_db_etf_publisher.get(
                f"{book_data['Publisher_id']}_contact"
            ).data
            book_data["Category"] = riak_db_etf_book.get(f"{book_id}_Category").data
            author_data["Book"].append(book_data)

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO Model
    riak_db_eao_author = riak_client.bucket_type("eao").bucket("author")
    riak_db_eao_book = riak_client.bucket_type("eao").bucket("book")
    riak_db_eao_publisher = riak_client.bucket_type("eao").bucket("publisher")
    start_time = time.time()

    for author_id in author_ids:
        author = riak_db_eao_author.get(str(author_id)).data
        author["Book"] = []
        for book_id in author["Book_id"]:
            book = riak_db_eao_book.get(str(book_id)).data
            book["Publisher"] = riak_db_eao_publisher.get(
                str(book["Publisher_id"])
            ).data
            author["Book"].append(book)

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    riak_db_aggregate_author = riak_client.bucket_type("aggregate").bucket("author")
    riak_db_aggregate_book = riak_client.bucket_type("aggregate").bucket("book")
    riak_db_aggregate_publisher = riak_client.bucket_type("aggregate").bucket(
        "publisher"
    )
    start_time = time.time()

    for author_id in author_ids:
        author = riak_db_aggregate_author.get(str(author_id)).data

        author["Book"] = []
        for book_id in author["Book_id"]:
            book = riak_db_aggregate_book.get(f"{book_id}_P1").data
            book["Publisher"] = riak_db_aggregate_publisher.get(
                str(book["Publisher_id"])
            ).data
            author["Book"].append(book)

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    riak_db_baseline_author = riak_client.bucket_type("baseline").bucket("author")
    riak_db_baseline_book_author = riak_client.bucket_type("baseline").bucket(
        "book_author"
    )
    riak_db_baseline_publisher = riak_client.bucket_type("baseline").bucket("publisher")
    riak_db_baseline_book = riak_client.bucket_type("baseline").bucket("book")
    riak_db_baseline_category = riak_client.bucket_type("baseline").bucket("category")
    riak_db_baseline_book_category = riak_client.bucket_type("baseline").bucket(
        "book_category"
    )

    start_time = time.time()
    for author_id in author_ids:
        author = {}
        author["name"] = riak_db_baseline_author.get(f"{author_id}_name").data

        author_book_ids = riak_db_baseline_book_author.get(
            f"author_{author_id}_book"
        ).data
        author["Book"] = []
        for book_id in author_book_ids:
            book_data = {}
            book_data["name"] = riak_db_baseline_book.get(f"{book_id}_name").data
            publisher_id = riak_db_baseline_book.get(f"{book_id}_publisher_id").data
            book_data["publisher_name"] = riak_db_baseline_publisher.get(
                f"{publisher_id}_name"
            ).data
            book_data["publisher_contact"] = riak_db_baseline_publisher.get(
                f"{publisher_id}_contact"
            ).data

            book_data["category"] = []
            book_category_ids = riak_db_baseline_book_category.get(
                f"book_{book_id}_category"
            ).data
            for category_id in book_category_ids:
                category_name = riak_db_baseline_category.get(
                    f"{category_id}_name"
                ).data
                category_subcategory = riak_db_baseline_category.get(
                    f"{category_id}_subcategory"
                ).data
                book_data["category"].append(
                    {"name": category_name, "subcategory": category_subcategory}
                )

            author["Book"].append(book_data)

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
