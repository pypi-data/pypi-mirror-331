# FireWrap

FireWrap is a Python library that provides a Firebase Firestore-like interface for SQLite databases. It allows you to perform CRUD operations on collections and documents, making it easier to work with SQLite in a way that resembles Firebase Firestore.

## Features

- Encode and decode column names for SQLite compatibility.
- Migrate data from Firebase to SQLite.
- Perform CRUD operations on collections and documents.
- Support for JSON data storage and retrieval.
- **FireWrapClient**: A client class that simplifies database operations with methods for adding, updating, deleting, and querying documents.

## Installation

To install FireWrap, install the module:

```bash
pip install FireWrap
```

## Usage

### Initialize FireWrap

To use FireWrap, you need to create an instance of the `FireWrap` class, specifying the database path:

```python
from firewrap import FireWrap

db = FireWrap('path/to/your/database.db')
```

### Working with Collections

You can get a reference to a collection and perform operations like adding documents, retrieving documents, and counting documents.

#### Add a Document

```python
data = {"name": "John Doe", "age": 30}
doc = db.collection("users").addDoc(data)
```

#### Get All Documents

```python
docs = db.collection("users").getDocs()
```

#### Get a Document by ID

```python
doc = db.collection("users").doc("document_id").getDoc()
```

#### Update a Document

```python
update_data = {"age": 31}
db.collection("users").doc("document_id").updateDoc(update_data)
```

#### Delete a Document

```python
db.collection("users").doc("document_id").deleteDoc()
```

### FireWrapClient

The `FireWrapClient` class provides a convenient interface for interacting with the FireWrap database. Here are some of the key methods:

- **get_docs(collection_name, limit=10, offset=0, sortingField=None, order="asc", searchKeywords=[])**: Retrieve documents from a specified collection with optional pagination and sorting.
- **add_doc(collection_name, data, id=None)**: Add a new document to a collection.
- **update_doc(collection_name, doc_id, data)**: Update an existing document in a collection.
- **delete_doc(collection_name, doc_id)**: Delete a document from a collection.
- **append_to_array(collection_name, doc_id, array_name, values)**: Append values to an array field in a document.
- **remove_from_array(collection_name, doc_id, array_name, values)**: Remove values from an array field in a document.
- **create_collection(collection_name)**: Create a new collection if it doesn't already exist.
- **get_collection_names()**: Retrieve the names of all collections in the database.

### API Endpoints

FireWrap also provides a Flask-based API for interacting with the database over HTTP.

- **GET /collections/<collection>**: Retrieve all documents in a collection.
- **POST /collections/<collection>**: Add a new document to a collection.
- **GET /collections/<collection>/<doc_id>**: Retrieve a specific document by ID.
- **POST /collections/<collection>/<doc_id>**: Create a new document with a specific ID.
- **PATCH /collections/<collection>/<doc_id>**: Update a specific document.
- **DELETE /collections/<collection>/<doc_id>**: Delete a specific document.
- **GET /collections/<collection>/count**: Get the total number of documents in a collection.
- **GET /collections**: Retrieve the names of all collections.
- **POST /collections**: Create a new collection.
- **POST /collections/<collection>/<doc_id>/array**: Append values to an array field in a document.
- **DELETE /collections/<collection>/<doc_id>/array**: Remove values from an array field in a document.

## Migration from Firebase

To migrate data from Firebase to FireWrap, use the `migrate_firebase_to_local_sql` function:

```python
from port import migrate_firebase_to_local_sql

migrate_firebase_to_local_sql('path/to/firebase/credentials.json', 'firesql.db')
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
