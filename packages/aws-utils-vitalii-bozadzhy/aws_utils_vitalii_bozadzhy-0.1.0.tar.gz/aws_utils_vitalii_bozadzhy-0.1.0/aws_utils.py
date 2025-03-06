import boto3
import logging

class DynamoDBDependency:
    def __init__(self, aws_region, aws_access_key_id, aws_secret_access_key, table_name):
        self.client = boto3.client(
            "dynamodb",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.table_name = table_name
        logging.info("Connected to DynamoDB.")

    def close_connection(self):
        del self.client
        logging.info("Connection to DynamoDB closed.")

    def get_user(self, user_id):
        """ Получает пользователя по user_id """
        try:
            response = self.client.get_item(TableName=self.table_name, Key={"user_id": {"S": user_id}})
            if "Item" in response:
                return {"status": "success", "data": response["Item"]}
            return {"status": "error", "message": "User not found"}
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            return {"status": "error", "message": str(e)}

    def add_user(self, user_data):
        try:
            self.client.put_item(TableName=self.table_name, Item=user_data)
            return {"status": "success", "message": "User added"}
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            return {"status": "error", "message": str(e)}

    def delete_user(self, user_id):
        try:
            self.client.delete_item(
                TableName=self.table_name,
                Key={"user_id": {"S": user_id}},
                ConditionExpression="attribute_exists(user_id)"
            )
            return {"status": "success", "message": f"User {user_id} deleted."}
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")
            return {"status": "error", "message": str(e)}

    def update_user(self, user_id, update_data):
        try:
            update_expression = "SET " + ", ".join(f"{key} = :{key}" for key in update_data.keys())
            expression_values = {f":{key}": {"S": value} for key, value in update_data.items()}

            response = self.client.update_item(
                TableName=self.table_name,
                Key={"user_id": {"S": user_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW"
            )
            return {"status": "success", "message": "User updated", "updated_attributes": response["Attributes"]}
        except Exception as e:
            logging.error(f"Error updating user {user_id}: {e}")
            return {"status": "error", "message": str(e)}

    def list_users(self):
        try:
            response = self.client.scan(TableName=self.table_name)
            users = response.get("Items", [])
            return {"status": "success", "data": users}
        except Exception as e:
            logging.error(f"Error fetching list of users: {e}")
            return {"status": "error", "message": str(e)}
