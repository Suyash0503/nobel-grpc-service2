import redis
import os
from dotenv import load_dotenv


# Load environment variables

load_dotenv()

# Connect to Redis Cloud (non-TLS)

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False
)

try:
    r.ping()
    print(" Connected to Redis Cloud successfully (non-TLS)!")
except Exception as e:
    print(" Redis connection failed:", e)
    exit(1)


print(" Running RediSearch Queries")


# Search all Nobel Prizes in Physics (2013–2023)

query1 = "@category:{physics}"
results1 = r.execute_command("FT.SEARCH", "nobel_index", query1, "RETURN", "3", "year", "category", "laureates")
print(f"🔹 Physics prizes (2013–2023): {results1[0]} results found.\n")


#  Search prizes from the year 2020

query2 = "@year:[2020 2020]"
results2 = r.execute_command("FT.SEARCH", "nobel_index", query2, "RETURN", "3", "year", "category", "laureates")
print(f"🔹 Prizes from the year 2020: {results2[0]} results found.\n")


query3 = "@firstname:Roger"
results3 = r.execute_command("FT.SEARCH", "nobel_index", query3, "RETURN", "3", "year", "category", "laureates")
print(f"🔹 Laureates with firstname 'Roger': {results3[0]} results found.\n")


print(" Example Physics Prize Record:")
for i in range(1, min(len(results1), 5), 2):
    key = results1[i].decode() if isinstance(results1[i], bytes) else results1[i]
    fields = [v.decode() if isinstance(v, bytes) else v for v in results1[i+1]]
    print(f"{key} → {fields}")

