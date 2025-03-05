# -*- coding: utf-8 -*-

"""This module contains the `Kafka` class, which provides a wrapper around the
aiokafka library for interacting with Apache Kafka.

Usage:
    - To create a Kafka instance, pass a `KafkaSettings` instance to the
      constructor.
    - To consume messages from a Kafka topic, use the `consume` method, passing
      the topic name, a dictionary of message handlers, and optional
      parameters.
    - To produce messages to a Kafka topic, use the `produce` method, passing
      the topic name, message key, and message value.

Example usage:

    from flowgate.config import KafkaSettings
    from flowgate.kafka import Kafka

    # Create a Kafka instance
    config = KafkaSettings(...)
    kafka = Kafka(config)

    # Consume messages from the "test.test.events" topic
    async def handle_test_event(event):
        ...
    kafka.consume("test.test.events", handlers={"TestEvent": handle_test_event})

    # Produce a message to the "test.test.events" topic
    from myapp.events import TestEvent
    message = TestEvent(id="123", name="test")
    kafka.produce("test.test.events", "123", message)
"""

import asyncio
import signal
import socket
import ssl
from typing import Any, Dict, Tuple, Union
from uuid import uuid4

import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from ddtrace import tracer
from pydantic import BaseModel

from flowgate.config import Handler, KafkaSettings
from flowgate.serializers import Avro
from flowgate.types import SerializerT
from flowgate.utils import Message

logger = structlog.get_logger(__name__)


class KafkaHandler:
    @tracer.wrap()
    async def init(self, config: KafkaSettings):
        """Kafka handles the registration of topics, consumer and producer.

        On startup kafka will register all topics defined
        and pull corresponding schemas from the schema registry.

        E.g topic = `test.test.events`

        ```python
        key_schema = SchemaRegistryClient(schema_registry_url).get_schema(f"{topic}-key")
        value_schema = SchemaRegistryClient(schema_registry_url).get_schema(f"{topic}-value")
        ```
        These avro schemas are used to encode and decode messages.

        Args:
            config (KafkaSettings): config
        """

        self.connected = False
        self.connect_lock = asyncio.Lock()
        self.consumer = None
        self.producer = None
        self._config = config
        await self._register_topics()

        self._loop = asyncio.get_running_loop()

        self._shutdown_event = asyncio.Event()
        self._setup_signal_handling()

        await self._start_connection()

        return self

    def _setup_signal_handling(self):
        # Register signals for graceful termination
        self._loop.add_signal_handler(signal.SIGINT, self._signal_handler)
        self._loop.add_signal_handler(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self):
        logger.info("Received shutdown signal. Preparing to shut down...")
        self._shutdown_event.set()

    async def _start_connection(self):
        if not self.connected:
            await self.connect_lock.acquire()
            while not self.connected:
                try:
                    logger.info("Attempting to connect kafka client.")
                    if self._config.consumer.topics:
                        await self._create_consumer()
                        logger.info("Kafka client (consumer) connected successfully.")
                    if self._config.producer.topics:
                        await self._create_producer()
                        logger.info("Kafka client (producer) connected successfully.")
                    self.connected = True
                except KafkaError:
                    logger.exception(
                        "Failed to connect Kafka client, retrying in %d seconds.",
                        self._config.retry_interval,
                    )
                    await asyncio.sleep(self._config.retry_interval)
            self.connect_lock.release()

    async def stop(self):
        """Stops the kafka consumer/producer"""
        if self.consumer:
            try:
                logger.info("Attempting to stop kafka consumer.")
                await self.consumer.stop()
            except KafkaError:
                logger.exception("Failed to stop kafka consumer.")

        if self.producer:
            try:
                logger.info("Attempting to stop kafka producer.")
                await self.producer.stop()
            except KafkaError:
                logger.exception("Failed to stop kafka producer.")

    async def _create_consumer(self):
        self.consumer = AIOKafkaConsumer(
            *self._config.consumer.topics,
            client_id=socket.gethostname(),
            group_id=self._config.group_id,
            bootstrap_servers=self._config.bootstrap_servers,
            auto_offset_reset=self._config.consumer.auto_offset_reset,
            enable_auto_commit=False,
            security_protocol=self._config.security_protocol.upper(),
            sasl_mechanism=self._config.sasl_mechanisms.upper(),
            sasl_plain_username=self._config.sasl_username,
            sasl_plain_password=self._config.sasl_password,
            ssl_context=self._ssl_context,
            max_poll_records=self._config.consumer.max_poll_records,
            max_poll_interval_ms=self._config.consumer.max_poll_interval_ms,
            session_timeout_ms=self._config.consumer.session_timeout_ms,
            rebalance_timeout_ms=self._config.consumer.rebalance_timeout_ms,
            heartbeat_interval_ms=self._config.consumer.heartbeat_interval_ms,
            fetch_max_wait_ms=self._config.consumer.fetch_max_wait_ms,
            fetch_min_bytes=self._config.consumer.fetch_min_bytes,
        )

    async def _create_producer(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self._config.bootstrap_servers,
            client_id=f"{str(uuid4())}",
            security_protocol=self._config.security_protocol.upper(),
            sasl_mechanism=self._config.sasl_mechanisms.upper(),
            sasl_plain_username=self._config.sasl_username,
            sasl_plain_password=self._config.sasl_password,
            ssl_context=self._ssl_context,
            linger_ms=self._config.producer.linger_ms,
        )
        await self.producer.start()

    @tracer.wrap()
    async def _register_topics(self):
        """Method called on startup to register all topics defined in the config.

        Method sets the self._avro and self._topics dictionaries.

        E.g. we have a topic `test.test.events` defined in the config.

        """
        self._avro = {}
        topics = set(self._config.consumer.topics + self._config.producer.topics)
        for topic in topics:
            self._avro[topic] = await Avro().init(self._config.schema_registry_url, topic)

    @property
    def _ssl_context(self):
        if self._config.security_protocol.upper() == "SASL_SSL":
            return ssl.create_default_context(cafile=self._config.ssl_ca_location)

    @classmethod
    @tracer.wrap()
    def _deserialize(cls, message: BaseModel) -> Dict[str, Any]:
        """Method serializes a message of type Record to be sent to kafka, by
        converting to dict adding the class name to the message.

        E.g.
        ```
        class TestEvent(Record):
            id: str
            name: str

        message = TestEvent(id="123", name="test")
        Kafka._deserialize(message)

        >>> {"class": "TestEvent", "data": {"id": "123", "name": "test"}}
        ```
        """
        name = message.__class__.__name__
        data = message.dict()
        return {"class": name, "data": data}

    @classmethod
    @tracer.wrap()
    def _serialize(cls, data: dict, serializer: SerializerT = None) -> Union[Message, BaseModel]:
        """Method serializes a message of type dict to be consumed by kafka. If
        a serializer is provided the message will be serialized using the
        serializer.
        """
        if serializer:
            return serializer(**data)
        return Message(**data)

    @classmethod
    def _get_class_name_and_data(cls, message: dict) -> Tuple[str, Dict]:
        class_name = message["class"]
        data = message["data"]
        return class_name, data

    async def consume(
        self,
        handlers: Dict[str, Handler],
    ):
        await self.consumer.start()
        try:
            async for message in self.consumer:
                if self._shutdown_event.is_set():
                    logger.info("Shutdown event set. Stopping consumption.")
                    break

                avro = self._avro[message.topic]
                with tracer.trace("flowgate.kafka.consume.decode_key"):
                    key = await avro.decode(message.key)
                with tracer.trace("flowgate.kafka.consume.decode_value"):
                    value = await avro.decode(message.value)
                class_name, data = self._get_class_name_and_data(value)
                if handler := handlers.get(class_name):
                    serialized_value = self._serialize(data, handler.serializer)
                    logger.info(
                        f"Consuming {class_name}", key=key, topic=message.topic, value=value
                    )
                    with tracer.trace("flowgate.kafka.consume.handle"):
                        await handler.callable(serialized_value)

                with tracer.trace("flowgate.kafka.consume.commit"):
                    await self.consumer.commit()
        except KafkaError:
            self.connected = False
        finally:
            await self.stop()

    @tracer.wrap()
    async def produce(self, topic: str, key: str, value: BaseModel) -> None:
        """Method produces a message to a topic. Both key and message are
        encoded using the corresponding avro schema.
        """

        deserialized_value = self._deserialize(value)
        logger.info(
            f"Producing {deserialized_value['class']}",
            key=key,
            topic=topic,
            value=deserialized_value,
        )
        avro = self._avro[topic]
        with tracer.trace("flowgate.kafka.produce.encode"):
            encoded_key, encoded_value = await avro.encode(key, deserialized_value)
        try:
            with tracer.trace("flowgate.kafka.produce.send_and_wait"):
                await self.producer.send_and_wait(topic, key=encoded_key, value=encoded_value)
        except KafkaError:
            self.connected = False
