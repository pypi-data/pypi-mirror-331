from .db import create_connection

class BaseMongoModel:
    """
    A base model for mongodb models.

    Attributes:
        collection_name (str): The name of the collection. Must be specified by subclasses.
    """

    collection_name = None
    """
    Can be overriden by subclasses to specify the collection name.
    """

    __pipeline : list = []

    def __new__(cls):
        if cls.collection_name is None:
            raise ValueError('collection_name is not specified.')
        
        return super().__new__(cls)

    def __init__(self):
        if self.collection_name is None:
            raise ValueError('collection_name is not specified.')

        # Initialize the collection
        self.collection = create_connection()[self.collection_name] 

    def save(self, **data):
        """
        Save a document to the collection.

        Args:
            **data: The data to be saved.
        """
        inserted = self.collection.insert_one(data)
        return inserted.inserted_id
    
    @classmethod
    def find_by_id(cls, id):
        """
        Find a document by id.

        Args:
            id: The id of the document to find.
        """
        return cls.collection.find_one({'_id': id})
    
    @classmethod
    def join(cls, collection, local_field, foreign_field, as_field):
        """
        Perform a join operation with another collection.

        Args:
            collection: The collection to join with.
            local_field: The field in the local collection.
            foreign_field: The field in the foreign collection.
            as_field: The field to store the joined data.
        """

        cls.__pipeline.append({
            '$lookup': {
                'from': collection,
                'localField': local_field,
                'foreignField': foreign_field,
                'as': as_field
            }
        })

        return cls
    
    @classmethod
    def match(cls, query):
        """
        Perform a match operation.

        Args:
            query: The query to match.
        """
        cls.__pipeline.append({
            '$match': query
        })

        return cls
    
    @classmethod
    def aggregate(cls):
        """
        Perform an aggregation operation.
        """
        return cls.collection.aggregate(cls.__pipeline)