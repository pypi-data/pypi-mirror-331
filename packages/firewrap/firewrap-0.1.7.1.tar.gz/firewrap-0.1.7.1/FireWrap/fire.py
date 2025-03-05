import requests
from . import FireWrap

class FireWrapClient:
    def __init__(self, db_name):
        """
        Initialize the DatabaseClient with the given database name.
        Args:
            db_name (str): The name of the database.
        """
        self.db = FireWrap(db_name)

    def reference(self, collection_name, doc_id=None):
        return f"{collection_name}/{doc_id}" if doc_id else collection_name

    def get_docs(self, collection_name, limit=10, offset=0, sortingField=None, order="asc", searchKeywords=[]):
        return self.db.collection(collection_name).getDocs(sortBy=sortingField, order=order,limit=limit,offset=offset,searchKeywords=searchKeywords)

    def update_doc(self, collection_name, doc_id, data):
        return self.db.collection(collection_name).doc(doc_id).updateDoc(data)

    def add_doc(self, collection_name, data,id=None):
        return self.db.collection(collection_name).addDoc(data,id)

    def delete_doc(self, collection_name, doc_id):
        return self.db.collection(collection_name).doc(doc_id).deleteDoc()

    def append_to_array(self, collection_name, doc_id, array_name, values):
        return self.db.collection(collection_name).doc(doc_id).updateArrayField(array_name, values, action='add')

    def remove_from_array(self, collection_name, doc_id, array_name, values):
        return self.db.collection(collection_name).doc(doc_id).updateArrayField(array_name, values, action='delete')

    def create_collection(self, collection_name):
        """Create a new collection if it doesn't already exist."""
        return self.db.createCollection(collection_name)

    def get_collection_names(self):
        """Retrieve the names of all collections in the database."""
        return self.db.getCollectionNames()

    def query_and_count_docs(self, collection_name, filters):
        """
        Query documents based on filters and return the count of matching documents.

        Args:
            collection_name (str): The name of the collection to query.
            filters (dict): A dictionary of filters to apply to the query.

        Returns:
            tuple: A tuple containing a list of matching documents and their count.
        """
        docs = self.db.collection(collection_name).query(filters)  # Assuming a query method exists
        return docs

    def count_docs(self, collection_name):
        """
        Count the number of documents in a collection based on filters.

        Args:
            collection_name (str): The name of the collection to count documents from.  
        """
        return self.db.collection(collection_name).countDocs()
    

    def __del__(self):
        """
        Destroy the DatabaseClient instance.
        This method should handle any necessary cleanup.
        """
        self.db.close()
        del self.db


