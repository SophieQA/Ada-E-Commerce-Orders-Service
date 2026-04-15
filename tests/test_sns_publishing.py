import json


# ─── Helpers ──────────────────────────────────────────────────────────────────

def receive_sns_message(sns_mock):
    """Pull one message off the test SQS queue and decode the SNS envelope."""
    sqs_client = sns_mock["sqs_client"]
    queue_url = sns_mock["queue_url"]
    resp = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    assert "Messages" in resp, "No SNS message was published to the topic."
    envelope = json.loads(resp["Messages"][0]["Body"])
    return json.loads(envelope["Message"])


SAMPLE_ITEMS = [
    {"product_id": "P001", "product_name": "Test Widget", "product_price": 9.99, "quantity": 2},
    {"product_id": "P002", "product_name": "Test Gadget", "product_price": 4.49, "quantity": 3},
]


# ─── SNS publishing ───────────────────────────────────────────────────────────

def test_create_order_publishes_sns_message_with_correct_event_type(client, sns_mock):
    # Act
    client.post("/orders/", json={"user_id": 1})
    message = receive_sns_message(sns_mock)

    # Assert
    assert message["event_type"] == "order.placed"


def test_create_order_sns_payload_matches_response(client, sns_mock):
    # Act
    response = client.post("/orders/", json={"user_id": 42})
    body = response.get_json()
    message = receive_sns_message(sns_mock)

    # Assert
    assert message["payload"]["user_id"] == 42
    assert message["payload"]["id"] == body["id"]


def test_create_order_missing_user_id_does_not_publish_sns(client, sns_mock):
    # Act
    client.post("/orders/", json={})
    sqs_resp = sns_mock["sqs_client"].receive_message(
        QueueUrl=sns_mock["queue_url"], MaxNumberOfMessages=1
    )

    # Assert
    assert "Messages" not in sqs_resp


def test_create_order_with_items_sns_payload_includes_items(client, sns_mock):
    # Act
    client.post("/orders/", json={"user_id": 1, "items": SAMPLE_ITEMS})
    message = receive_sns_message(sns_mock)

    # Assert
    assert message["event_type"] == "order.placed"
    assert {item["product_name"] for item in message["payload"]["items"]} == {"Test Widget", "Test Gadget"}
