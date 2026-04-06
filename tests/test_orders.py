# ─── POST /orders/ ────────────────────────────────────────────────────────────

def test_create_order_returns_201(client):
    response = client.post("/orders/", json={"user_id": 1})
    assert response.status_code == 201


def test_create_order_returns_order_data(client):
    response = client.post("/orders/", json={"user_id": 42})
    body = response.get_json()
    assert body["user_id"] == 42
    assert "id" in body
    assert body["items"] == []


def test_create_order_missing_user_id_returns_400(client):
    response = client.post("/orders/", json={})
    assert response.status_code == 400


# ─── GET /orders/ ─────────────────────────────────────────────────────────────

def test_get_all_orders_returns_empty_list(client):
    response = client.get("/orders/")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_all_orders_returns_all_orders(client, two_orders):
    response = client.get("/orders/")
    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 2


def test_get_all_orders_returns_correct_data(client, two_orders):
    response = client.get("/orders/")
    body = response.get_json()
    user_ids = {o["user_id"] for o in body}
    assert user_ids == {1, 2}


# ─── GET /orders/<id> ─────────────────────────────────────────────────────────

def test_get_single_order_returns_200(client, one_order):
    response = client.get(f"/orders/{one_order['id']}")
    assert response.status_code == 200


def test_get_single_order_returns_correct_data(client, one_order):
    response = client.get(f"/orders/{one_order['id']}")
    body = response.get_json()
    assert body["id"] == one_order["id"]
    assert body["user_id"] == one_order["user_id"]
    assert body["items"] == []


def test_get_single_order_not_found_returns_404(client):
    response = client.get("/orders/999999")
    assert response.status_code == 404


def test_get_single_order_invalid_id_returns_400(client):
    response = client.get("/orders/banana")
    assert response.status_code == 400


# ─── PUT /orders/<id> ─────────────────────────────────────────────────────────

def test_update_order_returns_204(client, one_order):
    response = client.put(f"/orders/{one_order['id']}", json={"user_id": 99})
    assert response.status_code == 204


def test_update_order_persists_changes(client, one_order):
    client.put(f"/orders/{one_order['id']}", json={"user_id": 99})
    fetched = client.get(f"/orders/{one_order['id']}").get_json()
    assert fetched["user_id"] == 99


def test_update_order_not_found_returns_404(client):
    response = client.put("/orders/999999", json={"user_id": 1})
    assert response.status_code == 404


def test_update_order_invalid_id_returns_400(client):
    response = client.put("/orders/banana", json={"user_id": 1})
    assert response.status_code == 400


# ─── DELETE /orders/<id> ──────────────────────────────────────────────────────

def test_delete_order_returns_204(client, one_order):
    response = client.delete(f"/orders/{one_order['id']}")
    assert response.status_code == 204


def test_delete_order_removes_order(client, one_order):
    client.delete(f"/orders/{one_order['id']}")
    response = client.get(f"/orders/{one_order['id']}")
    assert response.status_code == 404


def test_delete_order_not_found_returns_404(client):
    response = client.delete("/orders/999999")
    assert response.status_code == 404


def test_delete_order_invalid_id_returns_400(client):
    response = client.delete("/orders/banana")
    assert response.status_code == 400


# ─── Order items in responses ──────────────────────────────────────────────────

def test_get_single_order_includes_items_key(client, one_order_with_items):
    response = client.get(f"/orders/{one_order_with_items['id']}")
    body = response.get_json()
    assert "items" in body


def test_get_single_order_returns_correct_item_count(client, one_order_with_items):
    response = client.get(f"/orders/{one_order_with_items['id']}")
    body = response.get_json()
    assert len(body["items"]) == 2


def test_get_single_order_returns_correct_item_fields(client, one_order_with_items):
    response = client.get(f"/orders/{one_order_with_items['id']}")
    items = response.get_json()["items"]
    for item in items:
        assert "product_id" in item
        assert "product_name" in item
        assert "product_price" in item
        assert "quantity" in item


def test_get_single_order_returns_correct_item_data(client, one_order_with_items):
    response = client.get(f"/orders/{one_order_with_items['id']}")
    items = response.get_json()["items"]
    product_names = {item["product_name"] for item in items}
    assert product_names == {"Widget", "Gadget"}


def test_order_without_items_returns_empty_list(client, one_order):
    response = client.get(f"/orders/{one_order['id']}")
    body = response.get_json()
    assert body["items"] == []
