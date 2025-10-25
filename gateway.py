import os
import json
import grpc
import redis
from concurrent import futures
from dotenv import load_dotenv

import noble_pb2
import noble_pb2_grpc


# Load environment and connect to Redis 
load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=False,
    decode_responses=True
)

INDEX = "nobel_index"


def _safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


class NobelService(noble_pb2_grpc.NobelQueryServicer):

    #  Count prizes by Category 
    def CountByCategory(self, request, context):
        try:
            category = request.category.lower()
            query = f'@category:{{{category}}} @year:[{request.year_start} {request.year_end}]'
            res = r.execute_command(
                "FT.AGGREGATE", INDEX, query,
                "GROUPBY", "1", "@category",
                "REDUCE", "COUNT", "0", "AS", "num_prizes"
            )

            total = 0
            if isinstance(res, list) and len(res) > 1:
                row = res[1]
                if isinstance(row, list) and "num_prizes" in row:
                    idx = row.index("num_prizes") + 1
                    total = _safe_int(row[idx], 0)
            return noble_pb2.CountResponse(total=total)

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return noble_pb2.CountResponse(total=0)

      #  Count prizes by Year 
    def CountByYear(self, request, context):
        try:
            query = f'@year:[{request.year} {request.year}]'
            res = r.execute_command("FT.SEARCH", INDEX, query, "LIMIT", "0", "0")
            total = _safe_int(res[0], 0) if isinstance(res, list) and res else 0
            return noble_pb2.CountResponse(total=total)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return noble_pb2.CountResponse(total=0)

         # Search laureates by Firstname 
    def SearchByFirstname(self, request, context):
        try:
            firstname = request.firstname.strip()
            if not firstname:
                return noble_pb2.SearchResults(hits=[])

            #  Use TEXT query syntax 
            query = f'@firstname:{firstname.lower()}*'
            res = r.execute_command(
                "FT.SEARCH", INDEX, query,
                "RETURN", "6",
                "$.year", "$.category", "$.laureates[*].firstname",
                "$.laureates[*].surname", "$.laureates[*].motivation", "$.laureates"
            )

            hits = []
            for i in range(1, len(res), 2):
                if i + 1 >= len(res):
                    break
                fields = res[i + 1]
                d = {fields[j]: fields[j + 1] for j in range(0, len(fields), 2)}

                year = _safe_int(d.get("$.year", 0))
                category = d.get("$.category", "")
                laureates_json = d.get("$.laureates", "[]")

                try:
                    laureates = json.loads(laureates_json)
                except Exception:
                    laureates = []

                for L in laureates:
                    fn = str(L.get("firstname", ""))
                    sn = str(L.get("surname", ""))
                    if fn.lower().startswith(firstname.lower()):
                        hits.append(
                            noble_pb2.Hit(
                                year=year,
                                category=category,
                                firstname=fn,
                                surname=sn
                            )
                        )

            return noble_pb2.SearchResults(hits=hits)

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return noble_pb2.SearchResults(hits=[])

    #  Count laureates by Motivation keyword 
    def CountByMotivation(self, request, context):
        try:
            kw = request.keyword.strip().lower()
            if not kw:
                return noble_pb2.CountResponse(total=0)

            query = f'@motivation:({kw}*)'
            res = r.execute_command(
                "FT.SEARCH", INDEX, query,
                "RETURN", "1", "$.laureates"
            )

            total = 0
            for i in range(1, len(res), 2):
                if i + 1 >= len(res):
                    break
                fields = res[i + 1]
                d = {fields[j]: fields[j + 1] for j in range(0, len(fields), 2)}
                laureates_json = d.get("$.laureates", "[]")

                try:
                    laureates = json.loads(laureates_json)
                except Exception:
                    laureates = []

                for L in laureates:
                    mot = str(L.get("motivation", "")).lower()
                    if kw in mot:
                        total += 1

            return noble_pb2.CountResponse(total=total)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return noble_pb2.CountResponse(total=0)

        # Get laureates by Full Name 
    def GetByFullName(self, request, context):
        try:
            fn = request.firstname.strip().lower()
            sn = request.surname.strip().lower()
            if not fn or not sn:
                return noble_pb2.FullNameResults(hits=[])

            query = f'@firstname:{fn}* @surname:{sn}*'
            res = r.execute_command(
                "FT.SEARCH", INDEX, query,
                "RETURN", "3",
                "$.year", "$.category", "$.laureates"
            )

            hits = []
            for i in range(1, len(res), 2):
                if i + 1 >= len(res):
                    break
                fields = res[i + 1]
                d = {fields[j]: fields[j + 1] for j in range(0, len(fields), 2)}

                year = _safe_int(d.get("$.year", 0))
                category = d.get("$.category", "")
                laureates_json = d.get("$.laureates", "[]")

                try:
                    laureates = json.loads(laureates_json)
                except Exception:
                    laureates = []

                for L in laureates:
                    f = str(L.get("firstname", "")).lower()
                    s = str(L.get("surname", "")).lower()
                    if f.startswith(fn) and s.startswith(sn):
                        motivation = str(L.get("motivation", ""))
                        hits.append(
                            noble_pb2.FullNameHit(
                                year=year,
                                category=category,
                                motivation=motivation
                            )
                        )

            return noble_pb2.FullNameResults(hits=hits)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return noble_pb2.FullNameResults(hits=[])


# ---------- Start gRPC Server ----------
def serve():
    try:
        r.ping()
        print("Connected to Redis Cloud successfully (non-TLS)!")
    except Exception as e:
        print("Redis connection failed:", e)
        return

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    noble_pb2_grpc.add_NobelQueryServicer_to_server(NobelService(), server)

    server.add_insecure_port("127.0.0.1:50051")
    print("gRPC server running on 127.0.0.1:50051")

    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    serve()
