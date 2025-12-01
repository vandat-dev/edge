# app/core/kafka/producer_service.py
import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer


class KafkaProducer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, brokers: str = "localhost:9096"):
        self.brokers = brokers
        self.producer: AIOKafkaProducer | None = None
        self.started = False

    async def start(self):
        if self.started:
            return

        logging.info("Starting global Kafka producer...")

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.brokers,
            value_serializer=lambda x: json.dumps(x).encode("utf-8")
        )
        await self.producer.start()

        self.started = True
        logging.info("Kafka producer started.")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logging.info("Kafka producer stopped.")

    async def send_message(self, topic: str, message: dict):
        """Gửi message từ bất kỳ service nào."""
        if not self.started:
            raise RuntimeError("Kafka producer has not started!")
        await self.producer.send_and_wait(topic, message)


# Singleton instance
kafka_producer = KafkaProducer()
