class BaseEntity:
    @classmethod
    def all(cls, filter_query=None, sort_query=None):
        cursor = cls.collection.find(filter_query or {})
        if sort_query:
            cursor = cursor.sort(sort_query)
        return list(cursor)

    @classmethod
    def find_by_id(cls, entity_id):
        return cls.collection.find_one({"_id": entity_id})

    @classmethod
    def insert(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def update(cls, entity_id, data):
        return cls.collection.update_one({"_id": entity_id}, {"$set": data})

    @classmethod
    def delete(cls, entity_id):
        return cls.collection.delete_one({"_id": entity_id})