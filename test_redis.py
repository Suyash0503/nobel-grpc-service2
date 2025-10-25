import redis

# --------------------------------------------
#  Test connection to Redis Cloud (non-TLS)
# --------------------------------------------
r = redis.Redis(
    host="redis-15665.crce174.ca-central-1-1.ec2.redns.redis-cloud.com",
    port=15665,
    username="suyash",
    password="Sweetmemories@0503",
    ssl=False  # ❌ must be False for your free-tier database
)

try:
    r.ping()
    print("✅ Connected to Redis Cloud successfully (non-TLS)!")
except Exception as e:
    print("❌ Redis connection failed:", e)
