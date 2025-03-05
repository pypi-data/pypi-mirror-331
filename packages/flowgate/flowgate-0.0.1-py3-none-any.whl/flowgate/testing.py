# -*- coding: utf-8 -*-

"""This module contains the `KafkaMock` class, which provides a wrapper around the
AIOKafka library for interacting with Apache Kafka for testing.

"""
from typing import Dict, NamedTuple

import structlog
from pydantic import BaseModel

from flowgate.config import Handler
from flowgate.kafka import KafkaHandler

logger = structlog.get_logger(__name__)


class TestMessage(NamedTuple):
    key: str
    value: dict


class MockMessageBus:
    def __init__(self):
        self.messages: list = []
        self.__message = TestMessage

    async def add(self, key, value: dict):
        self.messages.append(self.__message(key=key, value=value))

    @property
    def last_message(self):
        return self.messages[-1]

    @property
    def first_message(self):
        return self.messages[0]

    def assert_no_messages_produced(self):
        assert len(self.messages) == 0

    def assert_one_message_produced(self) -> None:
        assert len(self.messages) == 1

    def assert_last_message_produced_with(self, key, value):
        assert self.last_message.key == key, f"{self.last_message.key} != {key}"
        assert self.last_message.value == value, f"{self.last_message.value} != {value}"

    def assert_message_produced_with(self, key, value):
        assert (
            TestMessage(key=key, value=value) in self.messages
        ), f"{TestMessage(key=key, value=value)} not in {self.messages}"

    def assert_multiple_messages_produced_with(self, messages: list) -> None:
        assert len(self.messages) == len(messages)
        for message in messages:
            self.assert_message_produced_with(**message)


class KafkaMockHandler(KafkaHandler):
    def __init__(self):
        self.messagebus = MockMessageBus()

    async def consume(
        self,
        handlers: Dict[str, Handler],
    ):
        for message in self.messagebus.messages:
            class_name, data = self._get_class_name_and_data(message.value)
            if handler := handlers.get(class_name):
                serialized_value = self._serialize(data, handler.serializer)
                logger.info(
                    f"Consuming {class_name}",
                    key=message.key,
                    **message.value,
                )
                await handler.callable(serialized_value)

    async def produce(self, topic: str, key: str, value: BaseModel):
        deserialized_value = self._deserialize(value)
        logger.info(
            "Producing",
            key=key,
            **value.dict(),
        )
        await self.messagebus.add(key=key, value=deserialized_value)

    async def stop(self):
        logger.info("Stopping kafka")
