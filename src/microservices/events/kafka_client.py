import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

import config

logger = logging.getLogger(__name__)


def _serialize(value) -> bytes:
    return json.dumps(value).encode()


def _deserialize(value: bytes):
    return json.loads(value.decode())


async def _start_with_retries(component, name: str) -> None:
    for attempt in range(1, config.KAFKA_START_RETRIES + 1):
        try:
            await component.start()
            logger.info('%s connected to %s', name, config.KAFKA_BROKERS)
            return
        except Exception as exc:
            logger.warning('%s start failed (attempt %s): %s', name, attempt, exc)
            await asyncio.sleep(config.KAFKA_START_DELAY)
    raise RuntimeError(f'cannot connect {name} to kafka')


async def create_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=config.KAFKA_BROKERS, value_serializer=_serialize
    )
    await _start_with_retries(producer, 'producer')
    return producer


async def send_event(producer: AIOKafkaProducer, topic: str, event: dict) -> tuple[int, int]:
    metadata = await producer.send_and_wait(topic, event)
    return metadata.partition, metadata.offset


async def consume_loop() -> None:
    consumer = AIOKafkaConsumer(
        *config.TOPICS,
        bootstrap_servers=config.KAFKA_BROKERS,
        group_id=config.CONSUMER_GROUP,
        auto_offset_reset='latest',
        value_deserializer=_deserialize,
    )
    await _start_with_retries(consumer, 'consumer')
    logger.info('consumer subscribed to %s', config.TOPICS)
    try:
        async for msg in consumer:
            logger.info(
                'consumed topic=%s partition=%s offset=%s value=%s',
                msg.topic, msg.partition, msg.offset, msg.value,
            )
    finally:
        await consumer.stop()
