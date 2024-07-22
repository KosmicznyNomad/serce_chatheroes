from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

db = client['chatheroes-testy']

collection = db['uzytkownicy']

document = {"imie": "Adam", "wiek": 11}
result = collection.insert_one(document)
print(f"Inserted document ID: {result.inserted_id}")

for doc in collection.find():
    print(doc)

query = {"name": "Adam"}
new_values = {"$set": {"age": 10}}
collection.update_one(query, new_values)

client.close()