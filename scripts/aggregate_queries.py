import os
import redis
from dotenv import load_dotenv

def decode(val):
    return val.decode() if isinstance(val, (bytes, bytearray)) else val

def print_rows(title, res, limit=None):
    print(f"\n{title}")
    if not res or len(res) == 0:
        print("  (no rows)")
        return
    
    rows = res[1:]
    if limit is not None:
        rows = rows[:limit]
    for row in rows:
        # row is like [b'category', b'physics', b'num_prizes', b'11']
        it = iter(row)
        as_dict = {decode(k): decode(v) for k, v in zip(it, it)}
        print(" ", as_dict)


# 1. Load environment variables and connect to Redis
load_dotenv()
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,  
)

try:
    r.ping()
    print("Connected to Redis Cloud successfully (non-TLS).")
except Exception as e:
    print("Redis connection failed:", e)
    raise SystemExit(1)

print("\nRunning Aggregation Queries...")


# Count prizes per category (2013–2023)
res_cat = r.execute_command(
    "FT.AGGREGATE", "nobel_index", "@year:[2013 2023]",
    "GROUPBY", "1", "@category",
    "REDUCE", "COUNT", "0", "AS", "num_prizes",
    "SORTBY", "2", "@num_prizes", "DESC"
)
print_rows("Prizes per category (2013–2023), most to fewest:", res_cat)

# Count prizes per year 
res_year = r.execute_command(
    "FT.AGGREGATE", "nobel_index", "@year:[2013 2023]",
    "GROUPBY", "1", "@year",
    "REDUCE", "COUNT", "0", "AS", "num_prizes",
    "SORTBY", "2", "@year", "ASC"
)
print_rows("Prizes per year (2013–2023):", res_year)

# Top 3 categories by prize count
res_top3 = r.execute_command(
    "FT.AGGREGATE", "nobel_index", "*",
    "GROUPBY", "1", "@category",
    "REDUCE", "COUNT", "0", "AS", "num_prizes",
    "SORTBY", "2", "@num_prizes", "DESC",
    "LIMIT", "0", "3"
)
print_rows("Top 3 categories by number of prizes:", res_top3)

# Keyword search in motivation field
keyword = "quantum"  
query = f'@motivation:{keyword}'

try:
    res_keyword = r.execute_command(
        "FT.SEARCH", "nobel_index", query,
        "RETURN", "3", "$.year", "$.category", "$.laureates[*].motivation"
    )
    print(f"\nLaureates mentioning '{keyword}' in motivation:")
    if len(res_keyword) > 1:
        total = res_keyword[0]
        print(f"Found {total} matching records")
        for i in range(2, len(res_keyword), 2):
            doc = res_keyword[i]
            print(" ", decode(doc))
    else:
        print("No matching records found.")
except Exception as e:
    print("Error while running motivation keyword query:", e)

print("\nAggregation queries completed.")
