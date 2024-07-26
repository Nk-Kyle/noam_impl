from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
from riak import RiakObject


def run():
    mongo_db = mongo_client["etf"]
    riak_db_etf = riak_client.bucket_type("etf")
    riak_db_eao = riak_client.bucket_type("eao")

    # =========== Book Collection =================
    book_collection = mongo_db["book"]
    book_bucket_etf = riak_db_etf.bucket("book")
    book_bucket_eao = riak_db_eao.bucket("book")

    # Get all books from mongodb
    for book in book_collection.find():
        # Inserting data into book kv
        # Book id
        # Get book id and remove it from the book dict
        book_id = str(book.pop("_id"))

        # ETF
        for k, v in book.items():
            if k == "_id":
                continue
            obj = RiakObject(riak_client, book_bucket_etf, f"{book_id}_{k}")
            obj.data = v
            obj.store()

        # EAO
        obj = RiakObject(riak_client, book_bucket_eao, book_id)
        obj.data = book
        obj.store()

    # =========== Member Collection =================
    member_collection = mongo_db["member"]
    member_bucket_etf = riak_db_etf.bucket("member")
    member_bucket_eao = riak_db_eao.bucket("member")

    # Get all members from mongodb
    for member in member_collection.find():
        # Inserting data into member kv
        # Member id
        member_id = str(member.pop("_id"))

        # ETF
        for k, v in member.items():
            if k == "_id" or v is None:
                continue
            obj = RiakObject(riak_client, member_bucket_etf, f"{member_id}_{k}")
            obj.data = v
            obj.store()

        # EAO
        obj = RiakObject(riak_client, member_bucket_eao, member_id)
        obj.data = member
        obj.store()

    # =========== Publisher Collection =================
    publisher_collection = mongo_db["publisher"]
    publisher_bucket_etf = riak_db_etf.bucket("publisher")
    publisher_bucket_eao = riak_db_eao.bucket("publisher")

    # Get all publishers from mongodb
    for publisher in publisher_collection.find():
        # Inserting data into publisher kv
        # Publisher id
        publisher_id = str(publisher.pop("_id"))

        # ETF
        for k, v in publisher.items():
            if k == "_id":
                continue
            obj = RiakObject(riak_client, publisher_bucket_etf, f"{publisher_id}_{k}")
            obj.data = v
            obj.store()

        # EAO
        obj = RiakObject(riak_client, publisher_bucket_eao, publisher_id)
        obj.data = publisher
        obj.store()

    # =========== Author Collection =================
    author_collection = mongo_db["author"]
    author_bucket_etf = riak_db_etf.bucket("author")
    author_bucket_eao = riak_db_eao.bucket("author")

    # Get all authors from mongodb
    for author in author_collection.find():
        # Inserting data into author kv
        # Author id
        author_id = str(author.pop("_id"))

        # ETF
        for k, v in author.items():
            if k == "_id":
                continue
            obj = RiakObject(riak_client, author_bucket_etf, f"{author_id}_{k}")
            obj.data = v
            obj.store()

        # EAO
        obj = RiakObject(riak_client, author_bucket_eao, author_id)
        obj.data = author
        obj.store()
