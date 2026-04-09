import json
from app.db import db
from app.models.order import Order
from app.models.line_item import OrderItem


# ─── POST /orders/ ────────────────────────────────────────────────────────────

def test_create_order_returns_201_and_persists(client):
    # Act
    response = client.post("/orders/", json={"user_id": 1})
    order_id = response.get_json()["id"]
    order = db.session.get(Order, order_id)

    # Assert
    assert response.status_code == 201
    assert order is not None
    assert order.user_id == 1


def test_create_order_returns_correct_response_body(client):
    # Act
    response = client.post("/orders/", json={"user_id": 42})
    body = response.get_json()

    # Assert
    assert body["user_id"] == 42
    assert "id" in body
    assert body["items"] == []


def test_create_order_missing_user_id_returns_400(client):
    # Act
    response = client.post("/orders/", json={})

    # Assert
    assert response.status_code == 400


def test_create_order_with_items_returns_201_and_persists(client):
    # Act
    response = client.post("/orders/", json={"user_id": 1, "items": SAMPLE_ITEMS})
    body = response.get_json()
    order = db.session.get(Order, body["id"])

    # Assert
    assert response.status_code == 201
    assert len(body["items"]) == 2
    assert {item["product_name"] for item in body["items"]} == {"Test Widget", "Test Gadget"}
    assert order is not None
    assert len(order.items) == 2
    assert {item.product_name for item in order.items} == {"Test Widget", "Test Gadget"}


# ─── GET /orders/ ─────────────────────────────────────────────────────────────

def test_get_all_orders_returns_empty_list(client):
    # Act
    response = client.get("/orders/")

    # Assert
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_all_orders_returns_all_orders(client, two_orders_with_items):
    # Act
    response = client.get("/orders/")

    # Assert
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_all_orders_returns_correct_data(client, two_orders_with_items):
    # Act
    body = client.get("/orders/").get_json()

    # Assert
    assert {o["user_id"] for o in body} == {1, 2}


# ─── GET /orders/<id> ─────────────────────────────────────────────────────────

def test_get_single_order_returns_200(client, one_order_with_items):
    # Act
    response = client.get(f"/orders/{one_order_with_items['id']}")

    # Assert
    assert response.status_code == 200


def test_get_single_order_returns_correct_data(client, one_order_with_items):
    # Act
    response = client.get(f"/orders/{one_order_with_items['id']}")
    body = response.get_json()

    # Assert
    assert body["id"] == one_order_with_items["id"]
    assert body["user_id"] == one_order_with_items["user_id"]
    assert len(body["items"]) == 2
    for item in body["items"]:
        assert "product_id" in item
        assert "product_name" in item
        assert "product_price" in item
        assert "quantity" in item


def test_get_single_order_not_found_returns_404(client):
    # Act
    response = client.get("/orders/999999")

    # Assert
    assert response.status_code == 404


def test_get_single_order_invalid_id_returns_400(client):
    # Act
    response = client.get("/orders/banana")

    # Assert
    assert response.status_code == 400


# ─── PUT /orders/<id> ─────────────────────────────────────────────────────────

def test_update_order_returns_204_and_persists(client, one_order_with_items):
    # Arrange
    order_id = one_order_with_items["id"]

    # Act
    response = client.put(f"/orders/{order_id}", json={"user_id": 99})
    order = db.session.get(Order, order_id)

    # Assert
    assert response.status_code == 204
    assert order.user_id == 99


def test_update_order_not_found_returns_404(client):
    # Act
    response = client.put("/orders/999999", json={"user_id": 1})

    # Assert
    assert response.status_code == 404


def test_update_order_invalid_id_returns_400(client):
    # Act
    response = client.put("/orders/banana", json={"user_id": 1})

    # Assert
    assert response.status_code == 400


# ─── DELETE /orders/<id> ──────────────────────────────────────────────────────

def test_delete_order_returns_204_and_removes_order_and_items(client, one_order_with_items):
    # Arrange
    order_id = one_order_with_items["id"]

    # Act
    response = client.delete(f"/orders/{order_id}")
    order = db.session.get(Order, order_id)
    orphaned_items = db.session.scalars(
        db.select(OrderItem).where(OrderItem.order_id == order_id)
    ).all()

    # Assert
    assert response.status_code == 204
    assert order is None
    assert orphaned_items == []


def test_delete_order_not_found_returns_404(client):
    # Act
    response = client.delete("/orders/999999")

    # Assert
    assert response.status_code == 404


def test_delete_order_invalid_id_returns_400(client):
    # Act
    response = client.delete("/orders/banana")

    # Assert
    assert response.status_code == 400


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
    assert message["event-type"] == "order.placed"


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
    assert message["event-type"] == "order.placed"
    assert {item["product_name"] for item in message["payload"]["items"]} == {"Test Widget", "Test Gadget"}
