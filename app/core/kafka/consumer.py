# app/core/kafka/consumer_service.py
import asyncio
import json
import logging
import time

from aiokafka import AIOKafkaConsumer


class KafkaConsumer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, brokers: str = "localhost:9096", topic: str = "demo"):
        self.brokers = brokers
        self.topic = topic
        # self.group_id = group_id
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False
        self.task: asyncio.Task | None = None

        # Callback (service khác sẽ override)
        self.on_message_callback = None

    async def start(self):
        if self.running:
            return

        logging.info(f"Starting global Kafka consumer on topic '{self.topic}'")

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.brokers,
            # group_id=self.group_id,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8"))
        )

        await self.consumer.start()
        self.running = True

        # Create background task
        self.task = asyncio.create_task(self._consume_loop())

        logging.info("Kafka consumer started.")

    async def stop(self):
        self.running = False

        if self.task:
            self.task.cancel()

        if self.consumer:
            await self.consumer.stop()
            logging.info("Kafka consumer stopped.")

    async def _consume_loop(self):
        try:
            async for msg in self.consumer:
                # logging.info(
                #     f"[KAFKA] partition={msg.partition} offset={msg.offset} value={msg.value}"
                # )
                # Trigger callback nếu có
                if self.on_message_callback:
                    try:
                        await self.on_message_callback(msg.value)
                    except Exception as e:
                        logging.error(f"Consumer callback error: {e}")

        except asyncio.CancelledError:
            pass

    # Cho phép service khác đăng ký callback
    def on_message(self, func):
        """
        Ví dụ:
            consumer.on_message(handle_event)
        """
        self.on_message_callback = func


# Singleton Instance
kafka_consumer = KafkaConsumer()
