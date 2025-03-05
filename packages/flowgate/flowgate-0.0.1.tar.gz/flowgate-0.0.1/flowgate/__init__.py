from flowgate.config import ConsumerSettings, Handler, KafkaSettings, ProducerSettings
from flowgate.dependency import Depends, inject
from flowgate.kafka import KafkaHandler
from flowgate.serializers import Avro
from flowgate.testing import KafkaMockHandler


class Kafka:
    @classmethod
    async def init(cls, config: KafkaSettings):
        if config.bootstrap_servers == "mock":
            return KafkaMockHandler()
        return await KafkaHandler().init(config)


__all__ = [
    "Kafka",
    "KafkaSettings",
    "Avro",
    "ConsumerSettings",
    "ProducerSettings",
    "Depends",
    "inject",
    "Handler",
]
