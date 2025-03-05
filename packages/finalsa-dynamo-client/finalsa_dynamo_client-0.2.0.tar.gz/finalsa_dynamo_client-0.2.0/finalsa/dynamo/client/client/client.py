from finalsa.dynamo.client.interface import SyncDynamoClient as Interface
from .implementation import DynamoClientImpl as Impl
from typing import List, Dict, Optional


class SyncDynamoClient(Interface):

    def __init__(self):
        self.__client__ = Impl()

    def write_transaction(self, transactions: List, max_num_transactions: Optional[int] = 99):
        self.__client__.write_transaction(transactions, max_num_transactions)

    def query(self, TableName: str, **kwargs):
        return self.__client__.query(TableName, **kwargs)

    def put(self, TableName: str, item: Dict):
        self.__client__.put(TableName, item)

    def delete(self, TableName: str, key: Dict):
        self.__client__.delete(TableName, key)

    def get(self, table_name: str, key: Dict) -> Dict:
        return self.__client__.get(table_name, key)

    def scan(self, TableName: str, **kwargs):
        return self.__client__.scan(TableName, **kwargs)

    def update(self, TableName: str, key: Dict, item: Dict):
        return self.__client__.update(TableName, key, item)
