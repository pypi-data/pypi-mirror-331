from typing import List, Dict, Optional
from finalsa.dynamo.client.interface import SyncDynamoClient as Interface
from .implementation import DynamoClientTestImpl as Impl


class SyncDynamoClientTestImpl(Interface):

    def __init__(self):
        self.__impl__ = Impl()

    def write_transaction(self, transactions: List, max_num_transactions: Optional[int] = 99):
        grouped_transactions = []
        group = []
        count = 0
        while len(transactions) > 0:
            group.append(transactions.pop(0))
            count += 1
            if count == max_num_transactions:
                grouped_transactions.append(group.copy())
                group = []
                count = 0
        if len(group) > 0:
            grouped_transactions.append(group)
        for group in grouped_transactions:
            self.__impl__.write_transaction(group)

    def query(self, TableName: str, **kwargs):
        return self.__impl__.query(TableName, **kwargs)

    def get(self, TableName: str, item: Dict):
        return self.__impl__.get(TableName, item)

    def put(self, TableName: str, item: Dict):
        self.__impl__.put(TableName, item)

    def delete(self, TableName: str, key: Dict):
        self.__impl__.delete(TableName, key)

    def scan(self, TableName: str, **kwargs):
        return self.__impl__.scan(TableName, **kwargs)

    def update(self, TableName: str, key: Dict, item: Dict):
        return self.__impl__.update(TableName, key, item)
    
    def clear(self):
        self.__impl__.clear()

def seed(table: str, items: List[Dict], client: SyncDynamoClientTestImpl = SyncDynamoClientTestImpl()):
    for item in items:
        client.__impl__.put(TableName=table, item=item)
