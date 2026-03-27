"""
Tests for store manager, choreographed saga
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import time
import json
from logger import Logger
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_saga(client):
    """Smoke test for complete saga"""
    logger = Logger.get_instance("test")
    
    # 1. Run order saga
    product_data = {
        "user_id": 1,
        "items": [{"product_id": 2, "quantity": 1}, {"product_id": 3, "quantity": 2}]
    }
    response = client.post('/orders',
                          data=json.dumps(product_data),
                          content_type='application/json')
    
    assert response.status_code == 201, f"Failed to create order: {response.get_json()}"
    order_id = response.get_json()['order_id']
    assert order_id > 0
    logger.debug(f"Created order with ID: {order_id}")

    # La saga est asynchrone (Kafka + handlers) : 3 s ne suffisent souvent pas (voir énoncé labo ~15–30 s).
    deadline = time.time() + 60
    response_json = None
    while time.time() < deadline:
        time.sleep(2)
        response = client.get(f"/orders/{order_id}")
        assert response.status_code == 201, f"Failed to get order: {response.get_json()}"
        response_json = response.get_json()
        pl = response_json.get("payment_link") or ""
        if "http" in pl:
            break
    else:
        pytest.fail(
            "La saga n'a pas mis à jour payment_link dans Redis dans les 60 s "
            f"(dernier état : {response_json})"
        )

    logger.debug(response_json)
    assert response_json["items"] is not None
    assert int(response_json["user_id"]) > 0
    assert float(response_json["total_amount"]) > 0
    assert "http" in (response_json.get("payment_link") or "")
    logger.debug(f"Order data is correct")
    
    # NOTE: si nous le voulions, nous pourrions également écrire des tests pour vérifier si l'enregistrement Outbox a été créé