import logging
from typing import Optional

from ai_event_pubsub.producer import EventProducer

from ujcatapi import config, dto

logger = logging.getLogger(__name__)


_producer: Optional[EventProducer] = None


def get_producer() -> EventProducer:
    global _producer
    if _producer is None:
        _producer = EventProducer(environment_name=config.ENVIRONMENT, amqp_url=config.AMQP_URL)

    return _producer


def fire_event(event_name: str, data: dto.JSON) -> None:
    if not config.ENABLE_AMQP:
        return

    producer = get_producer()

    try:
        producer.produce(event_name, data)
    except Exception as e:
        logger.exception(f"Failed to create event {event_name} with payload {data} because of {e}")
