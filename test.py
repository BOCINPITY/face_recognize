from database.Redis import cache_use_redis,get_face_data_from_redis


if __name__ == "__main__":
    cache_use_redis()
    ids, names, phones, accounts, encodings = get_face_data_from_redis()
    print("IDs:", ids)
    print("Names:", names)
    print("Phones:", phones)
    print("Accounts:", accounts)
    print("Encodings:", encodings)