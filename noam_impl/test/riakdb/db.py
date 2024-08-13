import riak

# Connect to the Riak cluster
client = riak.RiakClient(pb_port=8087, protocol="pbc")
