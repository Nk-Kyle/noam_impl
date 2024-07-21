# Migrate ETF structure to Aggregate structure
from test.mongodb.db import client as mongo_client


def run():
    """
    Prereq: ETF in MongoDB
    Post: Aggregate in MongoDB
    """

    etf_db = mongo_client["etf"]
    aggregate_db = mongo_client["aggregate"]

    # =========== Book Collection =================
    book_collection = etf_db["book"]
    aggregate_book_collection = aggregate_db["book"]

    # Copy data from ETF to Aggregate
    aggregate_book_collection.drop()
    book_collection.aggregate(
        [
            {
                "$project": {
                    "_id": 1,
                    "P0_Loan": "$Loan",
                    "P1": {
                        "name": "$name",
                        "Author": "$Author",
                        "Category": "$Category",
                        "Publisher_id": "$Publisher_id",
                    },
                    "P2": {
                        "description": "$description",
                        "language": "$language",
                        "keywords": "$keywords",
                    },
                }
            },
            {
                "$out": {
                    "db": "aggregate",
                    "coll": "book",
                }
            },
        ]
    )

    # # =========== Member Collection =================
    member_collection = etf_db["member"]
    aggregate_member_collection = aggregate_db["member"]

    # Copy data from ETF to Aggregate
    aggregate_member_collection.drop()
    member_collection.aggregate(
        [
            {
                "$project": {
                    "_id": 1,
                    "P0": {
                        "name": "$name",
                        "type": "$type",
                    },
                    "P1": {
                        "studentId": "$studentId",
                        "year": "$year",
                        "employeeId": "$employeeId",
                        "Faculty_id": "$Faculty_id",
                        "Faculty_name": "$Faculty_name",
                        "Address_address": "$Address_address",
                        "Address_city": "$Address_city",
                        "Address_postal": "$Address_postal",
                    },
                    "P2_Loan": "$Loan",
                }
            },
            {
                "$out": {
                    "db": "aggregate",
                    "coll": "member",
                }
            },
        ]
    )

    # =========== Publisher Collection =================
    publisher_collection = etf_db["publisher"]
    aggregate_publisher_collection = aggregate_db["publisher"]

    # Copy data from ETF to Aggregate
    aggregate_publisher_collection.drop()
    publisher_collection.aggregate(
        [
            {
                "$out": {
                    "db": "aggregate",
                    "coll": "publisher",
                }
            },
        ]
    )

    # =========== Author Collection =================
    author_collection = etf_db["author"]
    aggregate_author_collection = aggregate_db["author"]

    # Copy data from ETF to Aggregate
    aggregate_author_collection.drop()
    author_collection.aggregate(
        [
            {
                "$out": {
                    "db": "aggregate",
                    "coll": "author",
                }
            },
        ]
    )
