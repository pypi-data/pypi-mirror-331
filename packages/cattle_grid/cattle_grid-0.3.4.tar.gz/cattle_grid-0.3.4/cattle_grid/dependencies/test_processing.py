from unittest.mock import MagicMock
from faststream.rabbit import RabbitBroker, TestRabbitBroker

from cattle_grid.model.common import WithActor

from cattle_grid.testing.fixtures import *  # noqa

from .processing import MessageActor, ActorProfile, FactoriesForActor


async def test_message_actor(test_actor):
    broker = RabbitBroker()
    subscriber = MagicMock()

    @broker.subscriber("test")
    async def test_subscriber(actor: MessageActor):
        subscriber(actor)

    async with TestRabbitBroker(broker) as br:
        await br.publish(WithActor(actor=test_actor.actor_id), "test")

    subscriber.assert_called_once_with(test_actor)


async def test_actor_profile(test_actor):
    broker = RabbitBroker()
    subscriber = MagicMock()

    @broker.subscriber("test")
    async def test_subscriber(actor: ActorProfile):
        subscriber(actor)

    async with TestRabbitBroker(broker) as br:
        await br.publish(WithActor(actor=test_actor.actor_id), "test")

    subscriber.assert_called_once()

    (profile,) = subscriber.call_args[0]

    assert isinstance(profile, dict)
    assert profile["id"] == test_actor.actor_id


async def test_factories(test_actor):
    broker = RabbitBroker()
    subscriber = MagicMock()

    @broker.subscriber("test")
    async def test_subscriber(factories: FactoriesForActor):
        subscriber(factories)

    async with TestRabbitBroker(broker) as br:
        await br.publish(WithActor(actor=test_actor.actor_id), "test")

    subscriber.assert_called_once()

    (factories,) = subscriber.call_args[0]

    assert len(factories) == 2
