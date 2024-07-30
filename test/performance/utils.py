def cold_start(mongo_client, riak_client):
    # Cold Start run a random query for the first time
    # MongoDB
    mongo_db_etf_book = mongo_client["etf"]["book"]
    book = mongo_db_etf_book.aggregate(
        [
            {"$match": {"_id": 1}},
            {
                "$project": {
                    "_id": 1,
                    "Loan": 1,
                }
            },
        ]
    )
    list(book)

    # RiakDB
    riak_db_etf_book = riak_client.bucket_type("etf").bucket("book")
    book = riak_db_etf_book.get("1_name")
    _ = book.data


def string_to_list(data):
    return data.strip("[] ").replace("'", "").split(", ")
