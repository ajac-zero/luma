from redis_om import HashModel, Migrator


class DataRoom(HashModel):
    name: str
    collection: str
    storage: str


Migrator().run()
