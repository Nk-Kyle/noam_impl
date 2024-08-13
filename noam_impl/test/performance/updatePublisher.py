from test.generator.const import PUBLISHER_COUNT
from test.mongodb.db import client as mongo_client
from test.riakdb.db import client as riak_client
import random
import time
from test.performance.utils import cold_start
from faker import Faker

fake = Faker()


def run(n_run: int = 10):
    cold_start(mongo_client, riak_client)
    # Update Publisher

    # Random publisher ids
    publisher_ids = random.sample(range(1, PUBLISHER_COUNT), n_run)
    publisher_update_data = {
        str(publisher_id): {
            "contact": fake.phone_number(),
        }
        for publisher_id in publisher_ids
    }

    # MongoDB
    # ETF & EAO Model
    mongo_db_etf_publisher = mongo_client["etf"]["publisher"]
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        publisher_id = int(publisher_id)
        mongo_db_etf_publisher.update_one(
            {"_id": publisher_id},
            {
                "$set": {
                    "contact": data["contact"],
                }
            },
        )

    end_time = time.time()
    print(f"MongoDB (ETF & EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate Model
    mongo_db_aggregate_publisher = mongo_client["aggregate"]["publisher"]
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        publisher_id = int(publisher_id)
        mongo_db_aggregate_publisher.update_one(
            {"_id": publisher_id},
            {
                "$set": {
                    "contact": data["contact"],
                }
            },
        )

    end_time = time.time()
    print(f"MongoDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline Model
    mongo_db_baseline_publisher = mongo_client["baseline"]["publisher"]
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        publisher_id = int(publisher_id)
        mongo_db_baseline_publisher.update_one(
            {"_id": publisher_id},
            {
                "$set": {
                    "contact": data["contact"],
                }
            },
        )

    end_time = time.time()
    print(
        f"MongoDB (Baseline) Average Average: {(end_time - start_time)/n_run} seconds"
    )

    # RiakDB
    # ETF
    riak_db_etf_publisher = riak_client.bucket_type("etf").bucket("publisher")
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        publisher_contact = riak_db_etf_publisher.get(f"{publisher_id}_contact")
        publisher_contact.data = data["contact"]
        publisher_contact.store()

    end_time = time.time()
    print(f"RiakDB (ETF) Average: {(end_time - start_time)/n_run} seconds")

    # EAO
    riak_db_eao_publisher = riak_client.bucket_type("eao").bucket("publisher")
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        d = riak_db_eao_publisher.get(str(publisher_id))
        d.data.update(data)
        d.store()

    end_time = time.time()
    print(f"RiakDB (EAO) Average: {(end_time - start_time)/n_run} seconds")

    # Aggregate
    riak_db_aggregate_publisher = riak_client.bucket_type("aggregate").bucket(
        "publisher"
    )
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        d = riak_db_aggregate_publisher.get(f"{publisher_id}")
        d.data["contact"] = data["contact"]
        d.store()

    end_time = time.time()
    print(f"RiakDB (Aggregate) Average: {(end_time - start_time)/n_run} seconds")

    # Baseline
    riak_db_baseline_publisher = riak_client.bucket_type("baseline").bucket("publisher")
    start_time = time.time()

    for publisher_id, data in publisher_update_data.items():
        d = riak_db_baseline_publisher.get(f"{publisher_id}_contact")
        d.data = data["contact"]
        d.store()

    end_time = time.time()
    print(f"RiakDB (Baseline) Average: {(end_time - start_time)/n_run} seconds")
