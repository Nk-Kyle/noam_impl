from test.generator import generate
import time

print(f"Start generating data at {time.ctime()}")
generate.run()
print(f"Data generation finished at {time.ctime()}")
