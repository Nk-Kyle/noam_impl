from test.generator.const import MEMBER_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Query 4
    # Search Member Information by member_id

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
        member = mongo_db_etf_member.find_one({"_id": member_id}, {"Loan": 0})

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_member = mongo_client["aggregate"]["member"]
    start_time = time.time()

    for member_id in member_ids:
        member = mongo_db_aggregate_member.find_one({"_id": member_id}, {"P2_Loan": 0})

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_member = mongo_client["baseline"]["member"]
    start_time = time.time()

    for member_id in member_ids:
        member = mongo_db_baseline_member.find_one({"_id": member_id})

    end_time = time.time()
    print(f"MongoDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")

    # RiakDB
    # ETF Model
    riak_db_etf_member = riak_client.bucket_type("etf").bucket("member")
    keys = [
        "name",
        "type",
        "studentId",
        "year",
        "employeeId",
        "Faculty_id",
        "Faculty_name",
        "Address_city",
        "Address_address",
        "Address_postal",
    ]
    start_time = time.time()

    for member_id in member_ids:
        book_data = {}
        for key in keys:
            book_data[key] = riak_db_etf_member.get(f"{member_id}_{key}").data

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
        member.update(riak_db_aggregate_member.get(f"{member_id}_P1").data)

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    riak_db_baseline_member = riak_client.bucket_type("baseline").bucket("member")
    keys = [
        "name",
        "studentId",
        "year",
        "employeeId",
        "faculty_id",
        "faculty_name",
        "address_city",
        "address_address",
        "address_postal",
    ]
    start_time = time.time()

    for member_id in member_ids:
        member_data = {}
        for key in keys:
            member_data[key] = riak_db_baseline_member.get(f"{member_id}_{key}").data

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
