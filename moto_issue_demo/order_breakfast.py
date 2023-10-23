import boto3
from pprint import pprint
# from boto3.dynamodb.conditions import Key, Attr


def main():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    try:
        dynamodb.Table("meal-orders").update_item(
            Key={"customer": "mark", "mealtime": "breakfast"},
            UpdateExpression="set #lock = :lock",
            ExpressionAttributeNames={
                "#lock": "lock",
                "#acquired_at": "acquired_at",
            },
            ExpressionAttributeValues={":lock": { 'acquired_at': 123 }},
            ReturnValuesOnConditionCheckFailure="ALL_OLD",
            ConditionExpression="attribute_not_exists(#lock.#acquired_at)"
        )
    except BaseException as ex:
        pprint(ex.response)
        raise
    

if __name__ == "__main__":
    main()