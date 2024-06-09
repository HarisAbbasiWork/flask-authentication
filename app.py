import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)
client = MongoClient('mongodb+srv://harisbakhabarpk:7GJ9p6xebjgQgtjE@cluster0.ybov0y1.mongodb.net/')
db = client.testflask
employees = [
 { 'id': 1, 'name': 'Ashley' },
 { 'id': 2, 'name': 'Kate' },
 { 'id': 3, 'name': 'Joe' }
]


def serialize_doc(doc):
    """Convert a MongoDB document to a JSON-serializable format."""
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return doc

@app.route('/employees', methods=['GET'])
def get_employees():
    employees_cursor = db.employees.find()  # This returns a cursor
    employees_list = list(employees_cursor)  # Convert cursor to a list
    print("employees_list ", employees_list)
    # Apply the serialization to each document
    serializable_employees = [serialize_doc(employee) for employee in employees_list]
    return jsonify(serializable_employees)

@app.route('/employees/<string:id>', methods=['GET'])
def get_employee_by_id(id):
 # Convert the string id to ObjectId
 oid = ObjectId(id)
 print("oid ",oid)
 employee = db.employees.find_one({"_id":oid})  # This returns a cursor
 print("employee ",employee)
 if employee is None:
   return jsonify({ 'error': 'Employee does not exist'}), 404
 employee=serialize_doc(employee)
 return jsonify(employee)


def employee_is_valid(employee):
    # Assuming valid employee must have only 'name' key
    return 'name' in employee and len(employee) == 1

@app.route('/employees', methods=['POST'])
def create_employee():
    try:
        # Decode JSON data from the request
        employee_data = request.get_json()  # This automatically parses JSON data
        print("employee_data ",employee_data)

        # Check if the employee data is valid
        if not employee_is_valid(employee_data):
            return jsonify({'error': 'Invalid employee properties.'}), 400

        # Insert the employee data into MongoDB
        db.employees.insert_one(employee_data)

        # Return a success message
        return jsonify({'message': 'Employee added'}), 201

    except Exception as e:
        # Handle exceptions and return an error message
        return jsonify({'error': str(e)}), 500



@app.route('/employees/<string:id>', methods=['PATCH'])
def update_employee(id):
    oid = ObjectId(id)
    print("oid ", oid)
    employee = db.employees.find_one({"_id": oid})  # This returns a document, not a cursor
    print("employee ", employee)

    if employee is None:
        return jsonify({'error': 'Employee does not exist.'}), 404

    try:
        updated_employee = request.get_json()  # directly using request.get_json() to parse JSON data
    except:
        return jsonify({'error': 'Invalid JSON format.'}), 400

    if not employee_is_valid(updated_employee):
        return jsonify({'error': 'Invalid employee properties.'}), 400
    print("updated_employee ",updated_employee)
    # Perform the update operation
    result = db.employees.update_one({"_id": oid}, {'$set': updated_employee})

    if result.matched_count == 0:
        return jsonify({'error': 'Employee not found'}), 404

    if result.modified_count == 0:
        return jsonify({'message': 'No changes made'}), 200

    # Fetch the updated employee information
    employee = db.employees.find_one({"_id": oid})
    employee=serialize_doc(employee)
    return jsonify(employee)

@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id: int):
 global employees
 employee = get_employee(id)
 if employee is None:
   return jsonify({ 'error': 'Employee does not exist.' }), 404

 employees = [e for e in employees if e['id'] != id]
 return jsonify(employee), 200

if __name__ == '__main__':
   app.run(port=5000)