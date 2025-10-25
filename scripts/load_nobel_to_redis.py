import os
import json
import requests
import redis
from dotenv import load_dotenv

#  Load environment variables
load_dotenv()

#  Connect to Redis Cloud 
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,  # Non-TLS
    socket_timeout=15
)

# Test connection
try:
    r.ping()
    print("Connected to Redis Cloud successfully (non-TLS)!")
except Exception as e:
    print(" Redis connection failed:", e)
    exit(1)

# Fetch Nobel dataset
URL = "https://api.nobelprize.org/v1/prize.json"
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
data = resp.json()["prizes"]

# Filter for 2013–2023
filtered = [p for p in data if p.get("year") and 2013 <= int(p["year"]) <= 2023]
print(f" Filtered {len(filtered)} prize records between 2013–2023.")

#  Store in Redis as JSON
pipe = r.pipeline()
for p in filtered:
    year = p["year"]
    category = p.get("category", "unknown")
    laureates = p.get("laureates", [])
    doc = {
        "year": int(year),
        "category": category,
        "laureates": laureates
    }
    key = f"prize:{year}:{category}:{len(laureates)}"
    pipe.execute_command("JSON.SET", key, "$", json.dumps(doc))
pipe.execute()

print(f" Loaded {len(filtered)} prize documents (2013–2023) into Redis.")
