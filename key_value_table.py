import redis
from config import REDIS_HOST, REDIS_PORT

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

try:
    print("to redis: PING? REDIS:", r.connection.check_health())
except:
    print("Cannot connect to Redis")


def save_to_idTable(id:str, elementID:str):
    prefix = "idTable_"
    key = prefix + id
    r.set(key, elementID)

def get_from_idTable(id:str):
    prefix = "idTable_"
    key = prefix + id
    res = str(r.get(key))                    # res = b'9ebe11ea-f383-4f9c-9de3-35ac6e3d1a6d:2'  <- Examples
    return res[1:].replace("'", "")          # res = 9ebe11ea-f383-4f9c-9de3-35ac6e3d1a6d:2

