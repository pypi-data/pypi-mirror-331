from beanie import Document
from beanie.odm.queries.find import FindMany


class DummyDocument(Document):
    @classmethod
    def get_bson_encoders(cls):
        return {}


class DummyFindMany(FindMany):
    def __init__(self):
        super().__init__(DummyDocument)
