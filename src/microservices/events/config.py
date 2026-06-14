import os

PORT = int(os.getenv('PORT', '8082'))
KAFKA_BROKERS = os.environ['KAFKA_BROKERS']

CONSUMER_GROUP = 'events-service'
MOVIE_TOPIC = 'movie-events'
USER_TOPIC = 'user-events'
PAYMENT_TOPIC = 'payment-events'

TOPICS = (MOVIE_TOPIC, USER_TOPIC, PAYMENT_TOPIC)

TOPIC_BY_TYPE = {
    'movie': MOVIE_TOPIC,
    'user': USER_TOPIC,
    'payment': PAYMENT_TOPIC,
}

# Сколько раз пробовать подключиться к Kafka на старте и пауза между попытками.
KAFKA_START_RETRIES = int(os.getenv('KAFKA_START_RETRIES', '30'))
KAFKA_START_DELAY = float(os.getenv('KAFKA_START_DELAY', '2'))
