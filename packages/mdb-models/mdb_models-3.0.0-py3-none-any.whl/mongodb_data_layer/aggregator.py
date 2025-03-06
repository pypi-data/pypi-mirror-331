
class Aggregator:
    def __init__(self, collection):
        self.collection = collection

    def join(self):
        pass

    def aggregate(self, pipeline):
        return self.db.aggregate(pipeline)