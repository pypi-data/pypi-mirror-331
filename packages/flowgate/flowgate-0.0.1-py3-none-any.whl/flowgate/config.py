# -*- coding: utf-8 -*-

"""This module defines the `KafkaSettings` class, which is used to configure a
Kafka connection.

It includes the `ConsumerSettings` and `ProducerSettings` classes used to
configure the Kafka consumer and producer, respectively.
"""
from typing import List, Optional, Union

from pydantic import BaseModel, BaseSettings, root_validator

from flowgate.types import CallableT, SerializerT


class Handler(BaseModel):
    callable: CallableT
    serializer: SerializerT = None


class ConsumerSettings(BaseSettings):
    """A class for configuring the Kafka consumer settings.

    Parameters:
    - topics (List[str], optional): The topics to consume from. Defaults to an
      empty list.
    - auto_offset_reset (str, optional): The strategy to use when there is no
      initial offset in Kafka or if the current offset does not exist any more.
      Defaults to "latest".
    """

    topics: List[str] = []
    auto_offset_reset: str = "earliest"
    max_poll_records: Optional[int] = None
    max_poll_interval_ms: int = 300000
    session_timeout_ms: int = 45000

    # should be equal to session_timeout_ms in most cases
    rebalance_timeout_ms: int = 45000
    heartbeat_interval_ms: int = 3000
    fetch_max_wait_ms: int = 1000
    fetch_min_bytes: int = 1000


class ProducerSettings(BaseSettings):
    """A class for configuring the Kafka producer settings.

    Parameters:
    - topics (List[str], optional): The topics to produce to. Defaults to an empty list.
    """

    topics: List[str] = []
    linger_ms: int = 1000


class KafkaSettings(BaseSettings):
    """A class for configuring a Kafka connection.

    Parameters:
        - group_id (str): The group ID for the Kafka connection.

        - bootstrap_servers (str): The comma-separated list of broker hostnames and ports.

        - consumer (ConsumerSettings, optional): The consumer settings for the
          Kafka connection. Defaults to an empty `ConsumerSettings` object.

        - producer (ProducerSettings, optional): The producer settings for the
          Kafka connection. Defaults to an empty `ProducerSettings` object.

        - schema_registry_url (str): The URL for the Kafka schema registry.

        - security_protocol (str, optional): The security protocol to use for the
          Kafka connection. Defaults to "plaintext".

        - sasl_mechanisms (SASLMechanism, optional): The SASL mechanism to use for
          the Kafka connection. Defaults to `SASLMechanism.PLAIN`.

        - sasl_username (str, optional): The SASL username to use for the Kafka
          connection. Defaults to `None`.

        - sasl_password (str, optional): The SASL password to use for the Kafka
          connection. Defaults to `None`.

        - ssl_ca_location (str, optional): The path to the SSL CA certificate file
          to use for the Kafka connection. Defaults to `None`.

    Class Methods:
        - check_if_consumer_or_producer_exists(cls, values): A `root_validator`
          method to ensure that at least one of `consumer` or `producer` is
          set.
    """

    group_id: str
    bootstrap_servers: str
    consumer: ConsumerSettings = ConsumerSettings()
    producer: ProducerSettings = ProducerSettings()
    retry_interval: int = 5
    schema_registry_url: str
    security_protocol: str = "PLAINTEXT"
    sasl_mechanisms: str = "SCRAM-SHA-256"
    sasl_username: Union[str, None] = None
    sasl_password: Union[str, None] = None
    ssl_ca_location: Union[str, None] = None

    @root_validator
    def check_if_consumer_or_producer_exists(cls, values):
        consumer = values.get("consumer")
        producer = values.get("producer")
        if not consumer and not producer:
            raise ValueError("Either a consumer or a producer must be set")
        return values
