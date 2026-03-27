"""
Locust — test de charge POST /orders (Labo 8)
Lancer depuis la machine hôte avec Store Manager joignable (ex. http://localhost:5001).
"""
from locust import HttpUser, task, between


class OrderLoadUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def create_order(self):
        self.client.post(
            "/orders",
            json={
                "user_id": 1,
                "items": [
                    {"product_id": 2, "quantity": 1},
                    {"product_id": 3, "quantity": 2},
                ],
            },
            headers={"Content-Type": "application/json"},
            name="POST /orders",
        )
