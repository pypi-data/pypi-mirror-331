from unittest.mock import patch, MagicMock
from unittest import TestCase
import pytest
from signalsdk.local_mqtt import LocalMqtt


class MockMessage:
    class MockPayload:
        def __init__(self, payload):
            self.payload = payload

        def decode(self, param):
            return "payload"

    def __init__(self, topic, payload: MockPayload):
        self.topic = topic
        self.payload = payload

    def __str__(self):
        return f"MockMessage: topic: {self.topic} payload: {self.payload}"


@patch("signalsdk.local_mqtt.Client.loop_start")
@patch("signalsdk.local_mqtt.Client.connect")
class TestLocalMqtt(TestCase):
    def test_local_mqtt_connect(self, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        localMqtt.connect()
        mock_connect.assert_called_with("localhost", 1883)
        mock_start.assert_called()

    def test_local_mqtt_on_connect_exception(self, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        mock_connect.side_effect = Exception
        with pytest.raises(BaseException):
            localMqtt.connect()
            mock_connect.assert_not_called()
            mock_start.assert_not_called()

    def test_local_mqtt_on_message_received(self, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        mock_cb = MagicMock()
        localMqtt.set_on_event_received("topic", mock_cb)
        mock_message = MockMessage("topic", MockMessage.MockPayload("payload"))
        localMqtt.on_message_received(None, None, mock_message)
        mock_cb.assert_called_once_with("payload")

    def test_local_mqtt_on_message_received_no_callback(self, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        mock_cb = MagicMock()
        localMqtt.set_on_event_received("topic2", mock_cb)
        mock_message = MockMessage("topic", MockMessage.MockPayload("payload"))
        localMqtt.on_message_received(None, None, mock_message)
        mock_cb.assert_not_called()

    def test_local_mqtt_on_message_received_callback_exception(
        self, mock_connect, mock_start
    ):
        localMqtt = LocalMqtt()
        mock_cb = MagicMock(side_effect=Exception)
        localMqtt.set_on_event_received("topic", mock_cb)
        mock_message = MockMessage("topic", MockMessage.MockPayload("payload"))
        with pytest.raises(BaseException):
            localMqtt.on_message_received(None, None, mock_message)
            mock_cb.assert_called_once_with("payload")

    @patch("signalsdk.local_mqtt.Client.publish")
    def test_local_mqtt_publish(self, mock_publish, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        mock_publish.return_value = (0, 1)
        localMqtt.publish("topic", "payload")
        mock_publish.assert_called_once_with("topic", "payload")

    @patch("signalsdk.local_mqtt.Client.publish")
    def test_local_mqtt_publish_failure(self, mock_publish, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        mock_publish.return_value = (1, 1)
        with pytest.raises(BaseException):
            localMqtt.publish("topic", "payload")
            mock_publish.assert_called_once_with("topic", "payload")

    @patch("signalsdk.local_mqtt.Client.subscribe")
    def test_local_mqtt_subscribe(self, mock_subscribe, mock_connect, mock_start):
        localMqtt = LocalMqtt()
        mock_subscribe.return_value = (0, 1)
        localMqtt.subscribe("topic", True)
        mock_subscribe.assert_called_once_with("topic")
        assert localMqtt.get_subscribed_topic() == "topic"

    @patch("signalsdk.local_mqtt.Client.subscribe")
    def test_local_mqtt_subscribe_non_local_event(
        self, mock_subscribe, mock_connect, mock_start
    ):
        localMqtt = LocalMqtt()
        mock_subscribe.return_value = (0, 1)
        localMqtt.subscribe("topic", False)
        mock_subscribe.assert_called_once_with("topic")
        assert localMqtt.get_subscribed_topic() != "topic"

    @patch("signalsdk.local_mqtt.Client.subscribe")
    def test_local_mqtt_subscribe_empty_topic(
        self, mock_subscribe, mock_connect, mock_start
    ):
        localMqtt = LocalMqtt()
        mock_subscribe.return_value = (0, 1)
        localMqtt.subscribe("", False)
        mock_subscribe.assert_not_called()

    @patch("signalsdk.local_mqtt.Client.subscribe")
    def test_local_mqtt_subscribe_failure(
        self, mock_subscribe, mock_connect, mock_start
    ):
        localMqtt = LocalMqtt()
        mock_subscribe.return_value = (1, 1)
        with pytest.raises(BaseException):
            localMqtt.subscribe("topic", True)
            mock_subscribe.assert_called_once_with("topic")
        assert localMqtt.get_subscribed_topic() != "topic"

    @patch("signalsdk.local_mqtt.Client.unsubscribe")
    @patch("signalsdk.local_mqtt.Client.subscribe")
    def test_local_mqtt_unsubscribe(
        self, mock_subscribe, mock_unsubscribe, mock_connect, mock_start
    ):
        localMqtt = LocalMqtt()
        mock_subscribe.return_value = (0, 1)
        localMqtt.subscribe("topic", True)
        mock_subscribe.assert_called_once_with("topic")
        assert localMqtt.get_subscribed_topic() == "topic"
        mock_unsubscribe.return_value = (0, 1)
        localMqtt.unsubscribe()
        mock_unsubscribe.assert_called_once_with("topic")
        assert localMqtt.get_subscribed_topic() is None
