import hashlib
import time
import random

def generate_unique_id():
    unique_string = str(time.time()) + str(random.randint(0, 1000000))
    return hashlib.sha256(unique_string.encode()).hexdigest()[:10]

