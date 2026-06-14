import logging
import uuid
from datetime import datetime, timezone

from aiokafka import AIOKafkaProducer

import config
import kafka_client

logger = logging.getLogger(__name__)


async def publish_event(producer: AIOKafkaProducer, event_type: str, payload: dict) -> dict:
    event = {
        'id': f'{event_type}-{uuid.uuid4().hex}',
        'type': event_type,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'payload': payload,
    }
    topic = config.TOPIC_BY_TYPE[event_type]
    partition, offset = await kafka_client.send_event(producer, topic, event)
    logger.info('produced topic=%s partition=%s offset=%s', topic, partition, offset)
    return {'status': 'success', 'partition': partition, 'offset': offset, 'event': event}
