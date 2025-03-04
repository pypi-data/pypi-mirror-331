from flask import Blueprint, request, jsonify, g, app
from . import FireWrap
import os

firewrap_api = Blueprint("firewrap_api", __name__)

def get_db():
    """Create a new database connection for each request."""
    if 'db' not in g:
        db_name = request.args.get("db", os.getenv("DEFAULT_DB", "firewrap.db"))
        g.db = FireWrap(db_name)
    return g.db

@firewrap_api.route("/collections/<collection>", methods=["GET"])
def get_all_docs(collection):
    db = get_db()
    limit = int(request.args.get("limit", -1))
    offset = int(request.args.get("offset", 0))
    sortBy = request.args.get("sortBy", None)
    order = request.args.get("order", "asc")
    searchKeywords = request.args.get("search", "")
    searchKeywords = searchKeywords.split(",")
    print(searchKeywords)
    docs = db.collection(collection).getDocs(sortBy=sortBy, limit=limit, offset=offset, order=order,searchKeywords=searchKeywords)
    return jsonify(docs)


@firewrap_api.route("/collections/<collection>", methods=["POST"])
def add_doc(collection):
    db = get_db()
    data = request.json
    try:
        doc = db.collection(collection).addDoc(data)
    except:
        doc = db.collection(collection).addDoc({})
        db.collection(collection).doc(doc.doc_id).updateDoc(data)
    if doc:
        return jsonify({"message": "Document added", "id": doc.doc_id})
    return jsonify({"error": "Document not found"}), 404



@firewrap_api.route("/collections/<collection>/<doc_id>", methods=["GET"])
def get_doc(collection, doc_id):
    db = get_db()
    doc = db.collection(collection).doc(doc_id).getDoc()
    if doc:
        return jsonify(doc)
    return jsonify({"error": "Document not found"}), 404

@firewrap_api.route("/collections/<collection>/<doc_id>", methods=["POST"])
def new_doc_with_id(collection, doc_id):
    db = get_db()
    data = request.json
    try:
        docId = db.collection(collection).addDoc(data, doc_id)
    except:
        docId = db.collection(collection).addDoc({}, doc_id)
        db.collection(collection).doc(doc_id).updateDoc(data)
    if docId:
        return jsonify({"message": "Document added", "id": doc_id})
    return jsonify({"error": "Document not found"}), 404

@firewrap_api.route("/collections/<collection>/<doc_id>", methods=["PATCH"])
def update_doc(collection, doc_id):
    db = get_db()
    data = request.json
    updated = False
    try:
        updated = db.collection(collection).doc(doc_id).updateDoc(data)
        if updated:
            return jsonify({"message": "Document updated"})
    except Exception as e:
        print(e)
    if not updated:
        db.collection(collection).addDoc({}, doc_id)
        updated = db.collection(collection).doc(doc_id).updateDoc(data)
        if updated:
            return jsonify({"message": "Document updated"})
    return jsonify({"error": "Document not found"}), 404


@firewrap_api.route("/collections/<collection>/<doc_id>", methods=["DELETE"])
def delete_doc(collection, doc_id):
    db = get_db()
    deleted = db.collection(collection).doc(doc_id).deleteDoc()
    if deleted:
        return jsonify({"message": "Document deleted"})
    return jsonify({"error": "Document not found"}), 404

@firewrap_api.route("/collections/<collection>/count", methods=["GET"])
def get_collection_count(collection):
    """Get the total number of documents in a collection."""
    db = get_db()
    count = db.collection(collection).countDocs()
    return jsonify({"count": count})

@firewrap_api.route("/query/<collection>", methods=["GET"])
def query_docs(collection):
    db = get_db()
    filters = request.args.to_dict()
    filters.pop('db', None)
    result = db.collection(collection).queryDocs(**filters)
    return jsonify(result)

@firewrap_api.route("/collections", methods=["GET"])
def get_collection_names():
    db = get_db()
    collections = db.getCollectionNames()  # Assuming this method exists in your FireWrap class
    return jsonify({"collections": collections})

@firewrap_api.route("/collections", methods=["POST"])
def create_collection():
    db = get_db()
    collection_name = request.args.get("name")
    success = db.createCollection(collection_name)
    if success:
        return jsonify({"message": "Collection created", "collection_name": collection_name}), 201
    return jsonify({"error": "Collection could not be created"}), 500

@firewrap_api.route("/collections/<collection>/<doc_id>/array", methods=["PATCH","DELETE"])
def update_array(collection, doc_id):  
    """Update or delete a value from an array in a document."""
    db = get_db()
    values = request.json.get("values", [])
    field = request.json.get("field", "data")

    if not values or not field:
        return jsonify({"error": "'values' or 'field' not provided"}), 400
    
    updated = db.collection(collection).doc(doc_id).updateArrayField(field, values, action='delete' if request.method == "DELETE" else 'add')
    return jsonify({"message": "Document updated"})
