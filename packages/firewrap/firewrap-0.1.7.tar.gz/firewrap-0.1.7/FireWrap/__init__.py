import dataset
import json
import uuid
from dotty_dict import dotty
from .utils import recursive_json_decode



class FireWrap:
    """ FireWrap: Firebase Firestore-like SQL wrapper for SQLite & Dataset """

    COLUMN_MAPPING = {
         "-": "$DASH$",
         " ": "$SPACE$",
         ".": "$DOT$",
         "/": "$SLASH$",
         "&": "$AMP$"
      }
    
    @staticmethod
    def encode_column_name(name):
        """Replace special characters with mapped values for SQLite compatibility."""
        for key, value in FireWrap.COLUMN_MAPPING.items():
            name = name.replace(key, value)
        return name

    @staticmethod
    def decode_column_name(name):
        """Revert encoded column names back to their original values."""
        for key, value in FireWrap.COLUMN_MAPPING.items():
            name = name.replace(value, key)
        return name

    def __init__(self, db_path='firewrap.db'):
        """Initialize FireWrap with a database connection."""
        self.db = dataset.connect(f"sqlite:///{db_path}")

    def collection(self, collection_name) :
        """Get a reference to a collection (Firestore-like)."""
        return FireWrapCollection(self.db, collection_name)

    def close(self):
        """Close the database connection."""
        self.db.close()

    def getCollectionNames(self):
        """Retrieve the names of all collections in the database."""
        return list(self.db.tables)  # This retrieves the names of all tables (collections)

    def createCollection(self, collection_name):
        """Create a new collection if it doesn't already exist."""
        print(list(self.db.tables))  # Debug: print existing tables
        try:
            if collection_name not in list(self.db.tables):  # Check if the collection exists
                self.table = self.db.create_table(collection_name, primary_id="id", primary_type=self.db.types.string)
                print(self.table)
                return True
            else:
                print(f"Collection '{collection_name}' already exists.")  # Debug: collection exists
        except Exception as e:
            print(f"Error creating collection '{collection_name}': {e}")  # Debug: print error
        return False




class FireWrapCollection:
    """ Represents a Firestore-like Collection """

    def __init__(self, db, collection_name):
        """Initialize a Firestore-like collection."""
        self.db = db
        self.collection_name = collection_name

        # ✅ Ensure ID is a STRING PRIMARY KEY
        if collection_name not in db:
            self.table = db.create_table(collection_name, primary_id="id", primary_type=db.types.string)
        else:
            self.table = db[collection_name]

    def doc(self, doc_id):
        """Get a Firestore-like Document reference inside a collection."""
        return FireWrapDocument(self.db, self.collection_name, doc_id)

    def addDoc(self, data , id = str(uuid.uuid4()) ):
        """Auto-generate an ID and insert a new document (like Firebase's `addDoc`)."""
        if not id:
            id = str(uuid.uuid4())
        data["id"] = id # Generate a unique ID
        self.table.insert(data)
        return self.doc(data["id"])

    def getDocs(self, sortBy=None, limit=-1, offset=0, order="asc", searchKeywords=[]):
        """
        Retrieve documents with optional sorting, filtering by keywords, limit, and offset.

        Parameters:
        - sortBy (str, optional): Field name to sort by.
        - limit (int, optional): Number of records to return (-1 for all).
        - offset (int, optional): Number of records to skip before returning results.
        - order (str, optional): "asc" for ascending, "desc" for descending.
        - searchKeywords (list, optional): List of keywords to filter documents.

        Returns:
        - List of documents with `id` and `data` fields.
        """
        docs = list(self.table.all())  # Fetch all documents
        decoded_docs = []

        # Decode and format documents
        for doc in docs:
            decoded_doc = {}
            for key, value in doc.items():
                decoded_key = FireWrap.decode_column_name(key)
                
                # Attempt to decode JSON strings back to Python objects
                if isinstance(value, str) and decoded_key != "id":
                    try:
                        decoded_value = json.loads(value)
                        if isinstance(decoded_value, (dict, list)):
                            decoded_doc[decoded_key] = decoded_value
                            continue
                    except json.JSONDecodeError:
                        pass
                
                decoded_doc[decoded_key] = value

            decoded_docs.append({"id": decoded_doc["id"], "data": decoded_doc})


        # 🔀 **Sorting**
        if sortBy and decoded_docs and sortBy in decoded_docs[0]["data"]:  
            decoded_docs.sort(key=lambda x: x["data"].get(sortBy, ""), reverse=(order == "desc"))

        # 🔢 **Apply Offset & Limit**
        if limit != -1:
            decoded_docs = decoded_docs[offset:offset + limit]

        if searchKeywords:
            def contains_keyword(doc):
                """Convert entire document to a string and check if any keyword is present."""
                doc_str = str(json.dumps(doc["data"])).lower()  # Convert doc to a lowercase string
                return all(keyword.lower() in doc_str for keyword in searchKeywords)

            decoded_docs = [doc for doc in decoded_docs if contains_keyword(doc)]

        return decoded_docs

    def query(self, **filters):
        """Find documents using Firebase-like query filters (Firestore `where`)."""
        return list(self.table.find(**filters))

    def countDocs(self):
        """Return the total number of documents in the collection."""
        return self.table.count()

    def queryDocs(self, **filters):
        """
        Query documents based on Firestore-like filters.
        
        Example:
        queryDocs(**{"range.200K-100K": 50})  # Matches documents where range.200K-100K == 50
        """
        encoded_filters = {}
        for key, value in filters.items():
            encoded_key = FireWrap.encode_column_name(key)
            encoded_filters[encoded_key] = value

        docs = list(self.table.find(**encoded_filters))

        print(docs,encoded_filters)

        result = []
        for doc in docs:
            decoded_doc = {}
            for key, value in doc.items():
                decoded_key = FireWrap.decode_column_name(key)
                
                if isinstance(value, str):
                    try:
                        decoded_value = json.loads(value)
                        decoded_doc[decoded_key] = decoded_value
                        continue
                    except json.JSONDecodeError:
                        pass
                
                decoded_doc[decoded_key] = value
            
                dotty_doc = dotty(decoded_doc)
            result.append({"id": doc["id"], "data": dotty_doc.to_dict()})
        
        return result

    
class FireWrapDocument:
    """ Represents a Firestore-like Document """

    def __init__(self, db, collection_name, doc_id):
        """Initialize a Firestore-like document."""
        self.db = db
        self.collection_name = collection_name
        self.doc_id = str(doc_id)
        self.table = db[collection_name]

    def setDoc(self, data):
        """Set (create/update) the document using encoded column names & JSON encoding."""
        encoded_data = {}

        for key, value in data.items():
            encoded_key = FireWrap.encode_column_name(key)  # ✅ Encode column names
            
            # ✅ Convert lists & dicts to JSON before storing
            if isinstance(value, (list, dict)):
                encoded_data[encoded_key] = json.dumps(value)  
            else:
                encoded_data[encoded_key] = value  # Store normally if not a list/dict

        encoded_data["id"] = self.doc_id  # Ensure ID is stored correctly
        self.table.upsert(encoded_data, ["id"])  # ✅ Store encoded field names
        return True


    def getDoc(self):
        """Retrieve the document and recursively decode JSON strings."""
        doc = self.table.find_one(id=self.doc_id)
        if doc:
            decoded_data = {}

            for key, value in doc.items():
                decoded_key = FireWrap.decode_column_name(key)
                if isinstance(value, str):
                    try:
                        decoded_value = json.loads(value)  # Convert back to Python object
                        decoded_data[decoded_key] = recursive_json_decode(decoded_value)  # Recursively decode
                        continue
                    except json.JSONDecodeError:
                        pass  # If not a JSON, keep as is
                decoded_data[decoded_key] = value  # Keep other types unchanged

            return {"id": self.doc_id, "data": decoded_data}
        return None  # Document not found

        

    def updateDoc(self, data):
        """Update specific fields in the document (Firestore `updateDoc`) without overwriting other properties."""
        existing = self.getDoc()  # Retrieve the existing document
        if existing:
            dotty_existing = dotty(existing["data"])  # ✅ Convert existing data into dotty_dict
            
            # ✅ Apply updates using dotty syntax (ensures correct nested updates)
            for key, value in data.items():
                # ✅ Encode the key before using it
                encoded_key = FireWrap.encode_column_name(key) if "." not in str(key) else key

                # ✅ Convert lists & dicts to JSON before storing (Fixes SQLite Error)
                if isinstance(value, list) or isinstance(value, dict):
                    dotty_existing[encoded_key] = json.dumps(value)  # ✅ Store lists & dicts as JSON strings
                else:
                    dotty_existing[encoded_key] = value  # ✅ Store other types normally

            # ✅ Convert back to dictionary before storing
            updated_data = dotty_existing.to_dict()

            # ✅ Ensure the ID remains the same
            updated_data["id"] = existing["id"]  

            # ✅ Encode column names and ensure lists/dicts are stored as JSON strings
            encoded_updated_data = {
                FireWrap.encode_column_name(k): (json.dumps(v) if isinstance(v, (list, dict)) else v)
                for k, v in updated_data.items()
            }

            # ✅ Update only the affected fields in the database
            self.table.update(encoded_updated_data, ["id"])  
            return True

        return False  # Document not found

    def deleteDoc(self):
        """Delete the document (Firestore `deleteDoc`)."""
        self.table.delete(id=self.doc_id)
        return True

    def updateArrayField(self, field_name, values, action='add'):
        """
        Update an array field by adding or deleting a value.

        Parameters:
        - field_name (str): The name of the array field to update.
        - value: The value to add or delete.
        - action (str): 'add' to add the value, 'delete' to remove it.
        """
        existing = self.getDoc()  # Retrieve the existing document
        if existing:
            array_field = existing["data"].get(field_name, [])
            
            if action == 'add':
                for value in values:
                    if value not in array_field:  # Avoid duplicates
                        array_field.append(value)
            elif action == 'delete':
                for value in values:
                    if value in array_field:
                        array_field.remove(value)

            # Update the document with the modified array
            self.setDoc({field_name: array_field})  # Update the array field
            return True

        return False  # Document not found
    