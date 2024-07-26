from test.generator.const import MEMBER_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Query 3
    # Search Member loan detail by member_id

    # Generate n_run random member_id
    member_ids = set()
    while len(member_ids) < n_run:
        member_id = random.randint(1, MEMBER_COUNT)
        if member_id not in member_ids:
            member_ids.add(member_id)

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_member = mongo_client["etf"]["member"]
    start_time = time.time()

    for member_id in member_ids:
        member = mongo_db_etf_member.find_one(
            {"_id": member_id}, {"Loan": 1, "name": 1, "type": 1}
        )

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_member = mongo_client["aggregate"]["member"]
    start_time = time.time()

    for member_id in member_ids:
        member = mongo_db_aggregate_member.find_one({"_id": member_id}, {"P1": 0})

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_loan = mongo_client["baseline"]["loan"]
    start_time = time.time()

    for member_id in member_ids:
        loans_with_returns = mongo_db_baseline_loan.aggregate(
            [
                {"$match": {"memberID": member_id}},
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
    print(f"MongoDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")

    # RiakDB
    # ETF Model
    riak_db_etf_member = riak_client.bucket_type("etf").bucket("member")
    keys = ["name", "type", "Loan"]
    start_time = time.time()

    for member_id in member_ids:
        member_data = {}
        for key in keys:
            member_data[key] = riak_db_etf_member.get(f"{member_id}_{key}").data

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO Model
    riak_db_eao_member = riak_client.bucket_type("eao").bucket("member")
    start_time = time.time()

    for member_id in member_ids:
        member = riak_db_eao_member.get(str(member_id)).data

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    riak_db_aggregate_member = riak_client.bucket_type("aggregate").bucket("member")
    start_time = time.time()

    for member_id in member_ids:
        member = riak_db_aggregate_member.get(f"{member_id}_P0").data
        member["Loan"] = riak_db_aggregate_member.get(f"{member_id}_P2_Loan").data

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    print(f"RiakDB (Baseline): Inapplicable")
