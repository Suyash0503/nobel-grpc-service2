import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
)

# Drop old index
try:
    r.execute_command("FT.DROPINDEX", "nobel_index", "DD")
except redis.exceptions.ResponseError:
    pass

# JSON path
schema = [
    "ON", "JSON",
    "PREFIX", "1", "prize:",
    "SCHEMA",
    "$.year", "AS", "year", "NUMERIC",
    "$.category", "AS", "category", "TAG",
    "$.laureates[*].firstname", "AS", "firstname", "TEXT",
    "$.laureates[*].surname", "AS", "surname", "TEXT",
    "$.laureates[*].motivation", "AS", "motivation", "TEXT"
]

# Create the index
r.execute_command("FT.CREATE", "nobel_index", *schema)
print("Fixed RediSearch index 'nobel_index' created successfully!")
