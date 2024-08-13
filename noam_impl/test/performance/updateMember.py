from test.generator.const import BOOK_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start
from faker import Faker

fake = Faker()


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Update Member

    # Random member ids
    member_ids = random.sample(range(1, BOOK_COUNT), n_run)
    member_update_data = {
        str(member_id): {
            "name": fake.catch_phrase(),
            "Address_address": fake.address(),
            "Address_city": fake.city(),
            "Address_postal": fake.postcode(),
        }
        for member_id in member_ids
    }

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_member = mongo_client["etf"]["member"]
    mongo_db_etf_book = mongo_client["etf"]["book"]
    start_time = time.time()

    for member_id, data in member_update_data.items():
        member_id = int(member_id)
        mongo_db_etf_member.update_one(
            {"_id": member_id},
            {
                "$set": {
                    "name": data["name"],
                    "Address_address": data["Address_address"],
                    "Address_city": data["Address_city"],
                    "Address_postal": data["Address_postal"],
                }
            },
        )

        mongo_db_etf_book.update_many(
            {"Loan.Member_id": member_id},
            {"$set": {"Loan.$.Member_name": data["name"]}},
        )

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_member = mongo_client["aggregate"]["member"]
    mongo_db_aggregate_book = mongo_client["aggregate"]["book"]
    start_time = time.time()

    for member_id, data in member_update_data.items():
        member_id = int(member_id)
        mongo_db_aggregate_member.update_one(
            {"_id": member_id},
            {
                "$set": {
                    "P0.name": data["name"],
                    "P1.Address_address": data["Address_address"],
                    "P1.Address_city": data["Address_city"],
                    "P1.Address_postal": data["Address_postal"],
                }
            },
        )

        mongo_db_aggregate_book.update_many(
            {"P0_Loan.Member_id": member_id},
            {"$set": {"P0_Loan.$.Member_name": data["name"]}},
        )

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_member = mongo_client["baseline"]["member"]
    start_time = time.time()

    for member_id, data in member_update_data.items():
        member_id = int(member_id)
        mongo_db_baseline_member.update_one(
            {"_id": member_id},
            {
                "$set": {
                    "name": data["name"],
                    "Address_address": data["Address_address"],
                    "Address_city": data["Address_city"],
                    "Address_postal": data["Address_postal"],
                }
            },
        )

    end_time = time.time()
    print(
        f"MongoDB (Baseline) Average Average: {(end_time - start_time)/n_run} seconds"
    )

    # RiakDB
    # ETF
    riak_db_etf_member = riak_client.bucket_type("etf").bucket("member")
    start_time = time.time()

    for member_id, data in member_update_data.items():
        for key, value in data.items():
            d = riak_db_etf_member.get(f"{member_id}_{key}")
            d.data = value
            d.store()

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO
    riak_db_eao_member = riak_client.bucket_type("eao").bucket("member")
    start_time = time.time()

    for member_id, data in member_update_data.items():
        d = riak_db_eao_member.get(str(member_id))
        d.data.update(data)
        d.store()

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate
    riak_db_aggregate_member = riak_client.bucket_type("aggregate").bucket("member")
    start_time = time.time()

    for member_id, data in member_update_data.items():
        p0 = riak_db_aggregate_member.get(f"{member_id}_P0")
        p0.data["name"] = data["name"]
        p1 = riak_db_aggregate_member.get(f"{member_id}_P1")
        p1.data["Address_address"] = data["Address_address"]
        p1.data["Address_city"] = data["Address_city"]
        p1.data["Address_postal"] = data["Address_postal"]
        p0.store()
        p1.store()

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline
    riak_db_baseline_member = riak_client.bucket_type("baseline").bucket("member")
    start_time = time.time()

    for member_id, data in member_update_data.items():
        for key, value in data.items():
            d = riak_db_baseline_member.get(f"{member_id}_{key}")
            d.data = value
            d.store()

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
