import grpc
import noble_pb2
import noble_pb2_grpc


def run():
    # Connect to the gRPC server
    channel = grpc.insecure_channel("127.0.0.1:50051")
    stub = noble_pb2_grpc.NobelQueryStub(channel)

    print("\nRunning gRPC Client Queries...\n")

    try:
        #Count prizes for category "physics" between 2013–2023
        req_cat = noble_pb2.CountByCategoryRequest(
            category="physics",
            year_start=2013,
            year_end=2023
        )
        res_cat = stub.CountByCategory(req_cat)
        print(f"Physics prizes (2013–2023): {res_cat.total}")
        # Count total prizes in a specific year (2020)
        req_year = noble_pb2.CountByYearRequest(year=2020)
        res_year = stub.CountByYear(req_year)
        print(f"Prizes in year 2020: {res_year.total}")
       # Search laureates by FIRST NAME (for testing)
        req_first = noble_pb2.SearchByFirstnameRequest(firstname="Roger")
        res_first = stub.SearchByFirstname(req_first)
        print("\nLaureates with firstname 'Roger':")
        if not res_first.hits:
            print("  No laureates found.")
        else:
            for hit in res_first.hits:
                print(f"  {hit.firstname} {hit.surname}, Category: {hit.category}, Year: {hit.year}")

        #  Count laureates whose MOTIVATION contains a keyword
        req_mot = noble_pb2.CountByMotivationRequest(keyword="regulation")
        res_mot = stub.CountByMotivation(req_mot)
        print(f"\nLaureates mentioning 'regulation' in motivation: {res_mot.total}")
        #  Get laureates by FULL NAME (firstname + surname)
        req_full = noble_pb2.FullNameRequest(firstname="Roger", surname="Penrose")
        res_full = stub.GetByFullName(req_full)
        print("\nLaureate details for full name 'Roger Penrose':")
        if not res_full.hits:
            print("  No laureates found.")
        else:
            for hit in res_full.hits:
                print(f"  Year: {hit.year}, Category: {hit.category}")
                print(f"  Motivation: {hit.motivation}\n")

    except grpc.RpcError as e:
        print(f"\ngRPC Error: {e.code().name} — {e.details()}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    run()
