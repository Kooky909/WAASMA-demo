from flask import request, jsonify
import json
#from config import app, collection
from bson import json_util, ObjectId
from flask_cors import CORS, cross_origin

from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

client = MongoClient('localhost', 27017)

# This is a Mongodb database
db = client.flaskdb_mwah
collection = db.mycollection  # Collection name

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/contacts", methods=["GET"])
def get_contacts():
    contacts_cursor = collection.find()
    # Convert documents to JSON format using bson's json_util
    json_contacts = list(map(lambda x: json.loads(json_util.dumps(x)), contacts_cursor))
    return jsonify({"contacts": json_contacts})


@app.route("/create_contact", methods=["POST"])
def create_contact():
    data = request.json

    if not data:
        return (
            jsonify({"message": "You must include a first name, last name and email"}),
            400,
        )
    
    try:
        collection.insert_one(data)
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "User created!"}), 201


@app.route("/update_contact/<id>", methods=["PATCH"])
def update_contact(id):
    contact_id = {"_id": ObjectId(id)}  # Correctly format the user_id
    
    # Check if the contact exists
    existing_contact = collection.find_one(contact_id)
    if not existing_contact:
        return jsonify({"message": "User not found"}), 404

    data = request.json
    # Define the update operation
    update = {"$set": data}  # Use $set to update the specified fields
    collection.update_one(contact_id, update)

    return jsonify({"message": "User updated."}), 200


@app.route("/delete_contact/<id>", methods=["DELETE"])
def delete_contact(id):
    contact_id = {"_id": ObjectId(id)}  # Correctly format the user_id
    
    # Check if the contact exists
    existing_contact = collection.find_one(contact_id)
    if not existing_contact:
        return jsonify({"message": "User not found"}), 404

    result = collection.delete_one(contact_id)

    return jsonify({"message": "User deleted!"}), 200


if __name__ == "__main__":
    app.run(debug=True)