import random
import time

NUM_EVENTS = 1000
LOOKUPS = 1000

# generate events
events_vector = []
for i in range(NUM_EVENTS):
    events_vector.append({'source': 1, 'object': 1, 'objectid': i})

# create dict as hash-set
events_hash = {(e['source'], e['object'], e['objectid']): e for e in events_vector}

# choose random keys for lookup
keys = [random.randint(0, NUM_EVENTS - 1) for _ in range(LOOKUPS)]

# vector lookup
start = time.time()
for k in keys:
    for e in events_vector:
        if e['source'] == 1 and e['object'] == 1 and e['objectid'] == k:
            break
vector_time = time.time() - start

# hash-set lookup
start = time.time()
for k in keys:
    _ = events_hash.get((1, 1, k))
hash_time = time.time() - start

print(f"Vector lookup time: {vector_time:.3f}s")
print(f"Hash-set lookup time: {hash_time:.3f}s")
