import copy
import os
import datetime
import boto3

DYNAMO_DB = None
TABLE_NAME = 'happy-birthday'

CACHE = {}


class db:
    @staticmethod
    def init():
        global DYNAMO_DB

        if not DYNAMO_DB:
            DYNAMO_DB = boto3.resource(
                'dynamodb',
                endpoint_url=os.environ.get('YDB_ENDPOINT'),
                region_name='ru',
                aws_access_key_id=os.environ.get('YDB_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('YDB_ACCESS_KEY_SECRET')
            )

        table_names = [table.name for table in DYNAMO_DB.tables.all()]

        table = None

        if TABLE_NAME not in table_names:
            table = DYNAMO_DB.create_table(
                TableName=TABLE_NAME,
                KeySchema=[
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'step', 'AttributeType': 'S'},
                    {'AttributeName': 'errors', 'AttributeType': 'S'},
                    {'AttributeName': 'updated', 'AttributeType': 'S'},
                    {'AttributeName': 'questions', 'AttributeType': 'S'},
                    {'AttributeName': 'final', 'AttributeType': 'S'}
                ]
            )
        else:
            table = DYNAMO_DB.Table(TABLE_NAME)

        return table

    @staticmethod
    def save_user(id, data):
        id = str(id)

        table = db.init()

        data['id'] = id
        data['updated'] = datetime.datetime.now().isoformat()

        table.put_item(
            Item=data
        )
        CACHE[id] = copy.deepcopy(data)

        return data

    @staticmethod
    def get_user(id):
        id = str(id)

        if id in CACHE:
            return copy.deepcopy(CACHE[id])

        table = db.init()

        data = None

        try:
            response = table.get_item(Key={'id': id})
            data = response['Item']
            CACHE[id] = copy.deepcopy(data)
        except Exception as e:
            data = None

        return data
