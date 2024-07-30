from test.generator.const import AUTHOR_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import time
import datetime
import random
from test.performance.utils import cold_start
from faker import Faker
from riak import RiakObject

fake = Faker()


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Create Loans and add Returns
    # Loan ids
    current_timestamp = datetime.datetime.now().timestamp()
    loan_ids = [int(current_timestamp * 1000 + i) for i in range(n_run)]

    # Random member and book pairs
    member_book_pairs = [
        (random.randint(1, AUTHOR_COUNT), random.randint(1, AUTHOR_COUNT))
        for _ in range(n_run)
    ]

    # Random loan dates
    loan_dates = [fake.date_time_between(start_date="-1y") for _ in range(n_run)]

    # Random return dates (after loan dates)
    return_dates = [
        str(fake.date_time_between(date_start)) for date_start in loan_dates
    ]
    loan_dates = [str(date) for date in loan_dates]

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_book = mongo_client["etf"]["book"]
    mongo_db_etf_member = mongo_client["etf"]["member"]

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        member_doc = mongo_db_etf_member.find_one({"_id": member_id})
        book_doc = mongo_db_etf_book.find_one({"_id": book_id})

        mongo_db_etf_member.update_one(
            {"_id": member_id},
            {
                "$push": {
                    "Loan": {
                        "id": loan_id,
                        "loanedAt": loan_date,
                        "Book_id": book_id,
                        "Book_name": book_doc["name"],
                        "Book_description": book_doc["description"],
                    }
                }
            },
        )

        mongo_db_etf_book.update_one(
            {"_id": book_id},
            {
                "$push": {
                    "Loan": {
                        "id": loan_id,
                        "loanedAt": loan_date,
                        "Member_id": member_id,
                        "Member_name": member_doc["name"],
                        "Member_type": member_doc["type"],
                        "Member_year": member_doc["year"],
                        "Member_studentId": member_doc["studentId"],
                        "Member_employeeId": member_doc["employeeId"],
                    }
                }
            },
        )
    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Loans Average: {(end_time - start_time)/n_run} seconds")

    # Update Loans with Returns
    start_time = time.time()
    for (member_id, book_id), return_date, loan_id in zip(
        member_book_pairs, return_dates, loan_ids
    ):
        # Update last loan for Member by loan_id
        member_id = int(member_id)
        book_id = int(book_id)

        mongo_db_etf_member.update_one(
            {"_id": member_id, "Loan.id": loan_id},
            {
                "$set": {
                    "Loan.$.Return_returnedAt": return_date,
                    "Loan.$.Return_id": loan_id,
                    "Loan.$.Return_penalty": 0,
                }
            },
        )

        mongo_db_etf_book.update_one(
            {"_id": book_id, "Loan.id": loan_id},
            {
                "$set": {
                    "Loan.$.Return_returnedAt": return_date,
                    "Loan.$.Return_id": loan_id,
                    "Loan.$.Return_penalty": 0,
                }
            },
        )

    end_time = time.time()
    print(
        f"MongoDB (ETF & EAO) Returns Average: {(end_time - start_time)/n_run} seconds"
    )

    # Aggregate Model
    mongo_db_aggregate_book = mongo_client["aggregate"]["book"]
    mongo_db_aggregate_member = mongo_client["aggregate"]["member"]

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        member_doc = mongo_db_aggregate_member.find_one({"_id": member_id})
        book_doc = mongo_db_aggregate_book.find_one({"_id": book_id})

        mongo_db_aggregate_member.update_one(
            {"_id": member_id},
            {
                "$push": {
                    "P2_Loan": {
                        "id": loan_id,
                        "loanedAt": loan_date,
                        "Book_id": book_id,
                        "Book_name": book_doc["P1"]["name"],
                        "Book_description": book_doc["P2"]["description"],
                    }
                }
            },
        )

        mongo_db_aggregate_book.update_one(
            {"_id": book_id},
            {
                "$push": {
                    "P0_Loan": {
                        "id": loan_id,
                        "loanedAt": loan_date,
                        "Member_id": member_id,
                        "Member_name": member_doc["P0"]["name"],
                        "Member_type": member_doc["P0"]["type"],
                        "Member_year": member_doc["P1"]["year"],
                        "Member_studentId": member_doc["P1"]["studentId"],
                        "Member_employeeId": member_doc["P1"]["employeeId"],
                    }
                }
            },
        )
    end_time = time.time()
    print(f"MongoDB (Aggregate) Loans Average: {(end_time - start_time)/n_run} seconds")

    # Update Loans with Returns
    start_time = time.time()
    for (member_id, book_id), return_date, loan_id in zip(
        member_book_pairs, return_dates, loan_ids
    ):
        mongo_db_aggregate_member.update_one(
            {"_id": member_id, "P2_Loan.id": loan_id},
            {
                "$set": {
                    "P2_Loan.$.Return_returnedAt": return_date,
                    "P2_Loan.$.Return_id": loan_id,
                    "P2_Loan.$.Return_penalty": 0,
                }
            },
        )

        mongo_db_aggregate_book.update_one(
            {"_id": book_id, "P2_Loan.id": loan_id},
            {
                "$set": {
                    "P0_Loan.$.Return_returnedAt": return_date,
                    "P0_Loan.$.Return_id": loan_id,
                    "P0_Loan.$.Return_penalty": 0,
                }
            },
        )

    end_time = time.time()
    print(
        f"MongoDB (Aggregate) Returns Average: {(end_time - start_time)/n_run} seconds"
    )

    # Baseline Model
    mongo_db_baseline_loan = mongo_client["baseline"]["loan"]
    mongo_db_baseline_return = mongo_client["baseline"]["return"]

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        mongo_db_baseline_loan.insert_one(
            {
                "_id": loan_id,
                "loanedAt": loan_date,
                "bookID": book_id,
                "memberID": member_id,
            }
        )

    end_time = time.time()
    print(
        f"MongoDB (Baseline) Create Loans Average: {(end_time - start_time)/n_run} seconds"
    )

    # Create Loan Returns
    start_time = time.time()
    for return_date, loan_id in zip(return_dates, loan_ids):
        mongo_db_baseline_return.insert_one(
            {
                "_id": loan_id,
                "loanID": loan_id,
                "returnedAt": return_date,
                "penalty": 0,
            }
        )

    end_time = time.time()
    print(
        f"MongoDB (Baseline) Create Loan Returns Average: {(end_time - start_time)/n_run} seconds"
    )

    # RiakDB
    # ETF Model
    riak_bucket_etf_book = riak_client.bucket_type("etf").bucket("book")
    riak_bucket_etf_member = riak_client.bucket_type("etf").bucket("member")

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        book_name = riak_bucket_etf_book.get(f"{book_id}_name").data
        book_description = riak_bucket_etf_book.get(f"{book_id}_description").data
        member_name = riak_bucket_etf_member.get(f"{member_id}_name").data
        member_type = riak_bucket_etf_member.get(f"{member_id}_type").data
        member_year = riak_bucket_etf_member.get(f"{member_id}_year").data
        member_studentId = riak_bucket_etf_member.get(f"{member_id}_studentId").data
        member_employeeId = riak_bucket_etf_member.get(f"{member_id}_employeeId").data

        member_loan_data = riak_bucket_etf_member.get(f"{member_id}_Loan")
        if member_loan_data.data is None:
            member_loan_data.data = []
        member_loan_data.data.append(
            {
                "id": loan_id,
                "loanedAt": loan_date,
                "Book_id": book_id,
                "Book_name": book_name,
                "Book_description": book_description,
            }
        )
        member_loan_data.store()

        book_loan_data = riak_bucket_etf_book.get(f"{book_id}_Loan")
        if book_loan_data.data is None:
            book_loan_data.data = []
        book_loan_data.data.append(
            {
                "id": loan_id,
                "loanedAt": loan_date,
                "Member_id": member_id,
                "Member_name": member_name,
                "Member_type": member_type,
                "Member_year": member_year,
                "Member_studentId": member_studentId,
                "Member_employeeId": member_employeeId,
            }
        )
        book_loan_data.store()

    end_time = time.time()
    print(f"RiakDB (ETF) Loans Average: {(end_time - start_time)/n_run} seconds")

    # Update Loans with Returns
    start_time = time.time()
    for (member_id, book_id), return_date, loan_id in zip(
        member_book_pairs, return_dates, loan_ids
    ):
        member_loan_data = riak_bucket_etf_member.get(f"{member_id}_Loan")
        for loan_data in member_loan_data.data:
            if loan_data["id"] == loan_id:
                loan_data["Return_returnedAt"] = return_date
                loan_data["Return_id"] = loan_id
                loan_data["Return_penalty"] = 0
                break
        member_loan_data.store()

        book_loan_data = riak_bucket_etf_book.get(f"{book_id}_Loan")
        for loan_data in book_loan_data.data:
            if loan_data["id"] == loan_id:
                loan_data["Return_returnedAt"] = return_date
                loan_data["Return_id"] = loan_id
                loan_data["Return_penalty"] = 0
                break
        book_loan_data.store()

    end_time = time.time()
    print(f"RiakDB (ETF) Returns Average: {(end_time - start_time)/n_run} seconds")

    # EAO Model
    riak_bucket_eao_book = riak_client.bucket_type("eao").bucket("book")
    riak_bucket_eao_member = riak_client.bucket_type("eao").bucket("member")

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        book_data = riak_bucket_eao_book.get(str(book_id)).data
        member_data = riak_bucket_eao_member.get(str(member_id)).data

        member_loan_data = riak_bucket_eao_member.get(str(member_id))
        if member_loan_data.data.get("Loan") is None:
            member_loan_data.data["Loan"] = []
        member_loan_data.data["Loan"].append(
            {
                "id": loan_id,
                "loanedAt": loan_date,
                "Book_id": book_id,
                "Book_name": book_data["name"],
                "Book_description": book_data["description"],
            }
        )
        member_loan_data.store()

        book_loan_data = riak_bucket_eao_book.get(str(book_id))
        if book_loan_data.data.get("Loan") is None:
            book_loan_data.data["Loan"] = []
        book_loan_data.data["Loan"].append(
            {
                "id": loan_id,
                "loanedAt": loan_date,
                "Member_id": member_id,
                "Member_name": member_data.get("name"),
                "Member_type": member_data.get("type"),
                "Member_year": member_data.get("year"),
                "Member_studentId": member_data.get("studentId"),
                "Member_employeeId": member_data.get("employeeId"),
            }
        )
        book_loan_data.store()

    end_time = time.time()
    print(f"RiakDB (EAO) Loans Average: {(end_time - start_time)/n_run} seconds")

    # Update Loans with Returns
    start_time = time.time()
    for (member_id, book_id), return_date, loan_id in zip(
        member_book_pairs, return_dates, loan_ids
    ):
        member_loan_data = riak_bucket_eao_member.get(str(member_id))
        if member_loan_data.data.get("Loan") is None:
            member_loan_data.data["Loan"] = []
        for loan_data in member_loan_data.data["Loan"]:
            if loan_data["id"] == loan_id:
                loan_data["Return_returnedAt"] = return_date
                loan_data["Return_id"] = loan_id
                loan_data["Return_penalty"] = 0
                break
        member_loan_data.store()

        book_loan_data = riak_bucket_eao_book.get(str(book_id))
        if book_loan_data.data.get("Loan") is None:
            book_loan_data.data["Loan"] = []
        for loan_data in book_loan_data.data["Loan"]:
            if loan_data["id"] == loan_id:
                loan_data["Return_returnedAt"] = return_date
                loan_data["Return_id"] = loan_id
                loan_data["Return_penalty"] = 0
                break
        book_loan_data.store()

    end_time = time.time()
    print(f"RiakDB (EAO) Returns Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    riak_bucket_aggregate_book = riak_client.bucket_type("aggregate").bucket("book")
    riak_bucket_aggregate_member = riak_client.bucket_type("aggregate").bucket("member")

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        book_P1 = riak_bucket_aggregate_book.get(f"{book_id}_P1").data
        book_P2 = riak_bucket_aggregate_book.get(f"{book_id}_P2").data
        member_P0 = riak_bucket_aggregate_member.get(f"{member_id}_P0").data
        member_P1 = riak_bucket_aggregate_member.get(f"{member_id}_P1").data

        member_loan_data = riak_bucket_aggregate_member.get(f"{member_id}_P2_Loan")
        if member_loan_data.data is None:
            member_loan_data.data = []
        member_loan_data.data.append(
            {
                "id": loan_id,
                "loanedAt": loan_date,
                "Book_id": book_id,
                "Book_name": book_P1["name"],
                "Book_description": book_P2["description"],
            }
        )
        member_loan_data.store()

        book_loan_data = riak_bucket_aggregate_book.get(f"{book_id}_P0_Loan")
        if book_loan_data.data is None:
            book_loan_data.data = []
        book_loan_data.data.append(
            {
                "id": loan_id,
                "loanedAt": loan_date,
                "Member_id": member_id,
                "Member_name": member_P0.get("name"),
                "Member_type": member_P0.get("type"),
                "Member_year": member_P1.get("year"),
                "Member_studentId": member_P1.get("studentId"),
                "Member_employeeId": member_P1.get("employeeId"),
            }
        )
        book_loan_data.store()

    end_time = time.time()
    print(f"RiakDB (Aggregate) Loans Average: {(end_time - start_time)/n_run} seconds")

    # Update Loans with Returns
    start_time = time.time()
    for (member_id, book_id), return_date, loan_id in zip(
        member_book_pairs, return_dates, loan_ids
    ):
        member_loan_data = riak_bucket_aggregate_member.get(f"{member_id}_P2_Loan")
        for loan_data in member_loan_data.data:
            if loan_data["id"] == loan_id:
                loan_data["Return_returnedAt"] = return_date
                loan_data["Return_id"] = loan_id
                loan_data["Return_penalty"] = 0
                break
        member_loan_data.store()

        book_loan_data = riak_bucket_aggregate_book.get(f"{book_id}_P0_Loan")
        for loan_data in book_loan_data.data:
            if loan_data["id"] == loan_id:
                loan_data["Return_returnedAt"] = return_date
                loan_data["Return_id"] = loan_id
                loan_data["Return_penalty"] = 0
                break
        book_loan_data.store()

    end_time = time.time()
    print(
        f"RiakDB (Aggregate) Returns Average: {(end_time - start_time)/n_run} seconds"
    )

    # Baseline Model
    riak_bucket_baseline_loan = riak_client.bucket("baseline_loan")
    riak_bucket_baseline_return = riak_client.bucket("baseline_return")

    start_time = time.time()
    # Create Loans
    for (member_id, book_id), loan_date, loan_id in zip(
        member_book_pairs, loan_dates, loan_ids
    ):
        member = RiakObject(
            riak_client, riak_bucket_baseline_loan, f"{loan_id}_member_id"
        )
        member.data = member_id
        member.store()

        book = RiakObject(riak_client, riak_bucket_baseline_loan, f"{loan_id}_book_id")
        book.data = book_id
        book.store()

        loanedAt = RiakObject(
            riak_client, riak_bucket_baseline_loan, f"{loan_id}_loanedAt"
        )
        loanedAt.data = loan_date
        loanedAt.store()

    end_time = time.time()
    print(f"RiakDB (Baseline) Loans Average: {(end_time - start_time)/n_run} seconds")

    # Create Loan Returns
    start_time = time.time()
    for return_date, loan_id in zip(return_dates, loan_ids):
        loanID = RiakObject(
            riak_client, riak_bucket_baseline_return, f"{loan_id}_loan_id"
        )
        loanID.data = loan_id
        loanID.store()

        returnedAt = RiakObject(
            riak_client, riak_bucket_baseline_return, f"{loan_id}_returnedAt"
        )
        returnedAt.data = return_date
        returnedAt.store()

        penalty = RiakObject(
            riak_client, riak_bucket_baseline_return, f"{loan_id}_penalty"
        )
        penalty.data = 0
        penalty.store()

    end_time = time.time()
    print(f"RiakDB (Baseline) Returns Average: {(end_time - start_time)/n_run} seconds")
