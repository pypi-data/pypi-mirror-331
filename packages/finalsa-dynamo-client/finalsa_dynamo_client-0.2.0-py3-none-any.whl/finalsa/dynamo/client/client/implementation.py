import boto3
from finalsa.dynamo.client.interface import SyncDynamoClient
from typing import List, Dict, Optional


class DynamoClientImpl(SyncDynamoClient):

    def __init__(self):
        self.client = boto3.client("dynamodb")

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
            self.client.transact_write_items(TransactItems=group)

    def query(self, TableName: str, **kwargs):
        return self.client.query(TableName=TableName, **kwargs)

    def put(self, TableName: str, item: Dict):
        self.client.put_item(TableName=TableName, Item=item)

    def get(self, TableName: str, key: Dict):
        return self.client.get_item(TableName=TableName, Key=key)

    def delete(self, TableName: str, key: Dict):
        self.client.delete_item(TableName=TableName, Key=key)

    def scan(self, TableName: str, **kwargs):
        return self.client.scan(TableName=TableName, **kwargs)

    def update(self, TableName: str, key: Dict, item: Dict):
        self.client.update_item(TableName=TableName, Key=key, AttributeUpdates=item)
