# -*- coding: utf-8 -*-

"""This module provides an Avro class for handling the encoding and
decoding of Kafka events/commands using the schema registry service.

The Avro class takes the URL of the schema registry service and the
name of the Kafka topic as input, and provides methods for encoding and
decoding messages to/from Kafka.

Example usage:
    avro = Avro("http://localhost:8081", "test.test.events")
    encoded_key, encoded_message = avro.encode("key", {"field1": "value1", "field2": 42})
    decoded_message = avro.decode(encoded_message)

"""
from typing import Any, Dict, Tuple

import structlog
from schema_registry.client import AsyncSchemaRegistryClient  # type: ignore
from schema_registry.serializers import AsyncAvroMessageSerializer  # type: ignore

logger = structlog.get_logger(__name__)


class Avro:
    async def init(self, schema_registry_url: str, topic: str):
        """Avro handles the encoding and decoding of kafka events/commands.

        Args:
            schema_registry_url (str): schema_registry_url
            topic (str): topic name e.g. "test.test.events"

        On startup the Avro will pull the schemas for the key and
        value by using topic name as the subject name.

        E.g. topic = "test.test.events" will pull schemas for "test.test.events-key" and
        "test.test.events-value".
        """
        self._topic = topic
        self._subject_key = f"{topic}-key"
        self._subject_value = f"{topic}-value"
        self._schema_registry_client = AsyncSchemaRegistryClient(schema_registry_url)
        self._avro = AsyncAvroMessageSerializer(self._schema_registry_client)
        self._key_schema, self._value_schema = await self._get_schema()

        return self

    async def _get_schema(self):
        """Methods gets the schemas for kafka message key and value from the schema registry.
        Returns:
            tuple: key schema and value schema
        """
        value = await self._schema_registry_client.get_schema(self._subject_value)
        key = await self._schema_registry_client.get_schema(self._subject_key)
        if not key:
            raise ValueError(f"Schema not found {self._subject_key}")
        if not value:
            raise ValueError(f"Schema not found {self._subject_value}")
        return key, value

    async def decode(self, message: bytes) -> Dict[str, Any]:
        """Decodes messages being consumed from kafka.

        Args:
            message (bytes): message

        Returns:
            dict | None: decoded message
        """
        if decoded_message := await self._avro.decode_message(message):
            return decoded_message
        raise ValueError("Message could not be decoded")

    async def encode(self, key: str, value: dict) -> Tuple[bytes, bytes]:
        """Encodes keys and values for messages being produced to kafka.

        Args:
            key (str): message key
            value (dict): message value

        Returns:
            tuple[bytes, bytes]: encoded key and value
        """
        encoded_key = await self._avro.encode_record_with_schema_id(self._key_schema.schema_id, key)  # type: ignore
        encoded_value = await self._avro.encode_record_with_schema_id(
            self._value_schema.schema_id, value
        )
        return encoded_key, encoded_value
