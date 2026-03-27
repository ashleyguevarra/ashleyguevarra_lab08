"""
Handler: Payment Created
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from db import get_redis_conn
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer
from orders.commands.write_order import sync_order_payment_link_redis


class PaymentCreatedHandler(EventHandler):
    """Handles PaymentCreated events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "PaymentCreated"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        r = get_redis_conn()
        dedupe_key = f"saga:payment_created:{event_data['order_id']}"
        if not r.set(dedupe_key, "1", nx=True, ex=3600):
            return
        try:
            payment_link = event_data.get('payment_link', 'no-link')
            sync_order_payment_link_redis(event_data['order_id'], payment_link, is_paid=True)
            event_data['event'] = "SagaCompleted"
            self.logger.debug(f"payment_link={payment_link}")
            OrderEventProducer().get_instance().send(config.KAFKA_TOPIC, value=event_data)
        except Exception as e:
            r.delete(dedupe_key)
            event_data['error'] = str(e)
