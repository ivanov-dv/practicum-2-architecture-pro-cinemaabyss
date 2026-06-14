import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from aiokafka import AIOKafkaProducer
from fastapi import Depends, FastAPI, Request

import kafka_client
from events import publish_event
from logging_config import setup_logging
from models import MovieEvent, PaymentEvent, UserEvent

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.producer = await kafka_client.create_producer()
    consumer_task = asyncio.create_task(kafka_client.consume_loop())
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await app.state.producer.stop()


app = FastAPI(lifespan=lifespan)


def get_producer(request: Request) -> AIOKafkaProducer:
    return request.app.state.producer


ProducerDep = Annotated[AIOKafkaProducer, Depends(get_producer)]


@app.get('/api/events/health')
async def health() -> dict:
    return {'status': True}


@app.post('/api/events/movie', status_code=201)
async def create_movie_event(body: MovieEvent, producer: ProducerDep) -> dict:
    return await publish_event(producer, 'movie', body.model_dump())


@app.post('/api/events/user', status_code=201)
async def create_user_event(body: UserEvent, producer: ProducerDep) -> dict:
    return await publish_event(producer, 'user', body.model_dump())


@app.post('/api/events/payment', status_code=201)
async def create_payment_event(body: PaymentEvent, producer: ProducerDep) -> dict:
    return await publish_event(producer, 'payment', body.model_dump())
