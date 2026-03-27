"""
Handler: Order Created
SPDX-License-Identifier: LGPL-3.0-or-later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from typing import Dict, Any
import config
from db import get_sqlalchemy_session
from event_management.base_handler import EventHandler
from orders.commands.order_event_producer import OrderEventProducer
from stocks.commands.write_stock import check_out_items_from_stock, update_stock_redis


class OrderCreatedHandler(EventHandler):
    """Handles OrderCreated events"""
    
    def __init__(self):
        self.order_producer = OrderEventProducer()
        super().__init__()
    
    def get_event_type(self) -> str:
        """Get event type name"""
        return "OrderCreated"
    
    def handle(self, event_data: Dict[str, Any]) -> None:
        """Execute every time the event is published"""
        order_event_producer = OrderEventProducer()
        session = None
        try:
            session = get_sqlalchemy_session()
            check_out_items_from_stock(session, event_data['order_items'])
            session.commit()
            update_stock_redis(event_data['order_items'], '-')
            event_data['event'] = "StockDecreased"
        except Exception as e:
            if session is not None:
                session.rollback()
            event_data['event'] = "StockDecreaseFailed"
            event_data['error'] = str(e)
        finally:
            if session is not None:
                session.close()
            self.logger.debug(f"payment_link={event_data.get('payment_link', '')}")
            order_event_producer.get_instance().send(config.KAFKA_TOPIC, value=event_data)
