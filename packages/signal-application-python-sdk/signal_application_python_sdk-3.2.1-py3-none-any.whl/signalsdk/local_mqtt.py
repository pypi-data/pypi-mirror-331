import logging
import collections
from paho.mqtt.client import Client, MQTT_ERR_SUCCESS
from signalsdk.signal_exception import (
    SignalAppLocalMqttOnConnectionCallBackError,
    SignalAppLocalMqttOConnectionError,
    SignalAppLocalMqttPublishError,
    SignalAppLocalMqttSubscribeError,
)

LOCAL_MQTT_URL = "localhost"
LOCAL_MQTT_PORT = 1883


class LocalMqtt:
    def __init__(self, client_id=""):
        self.mqtt_client = Client("localmqtt" + client_id)
        # topic -> set of callbacks
        self.event_call_backs = collections.defaultdict(set)
        self.subscribed_topic = None
        self.connected_callback = None

    def set_on_event_received(self, topic, callback):
        # add a callback for a topic
        self.event_call_backs[topic].add(callback)
        logging.debug(f"set_on_event_received=> topic: {topic}, callback: {callback}")

    def remove_event_callbacks(self, topic):
        # remove all callbacks for a topic
        if topic in self.event_call_backs:
            self.event_call_backs.pop(topic)

    def set_on_connected(self, callback):
        self.connected_callback = callback

    def on_message_received(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        topic = message.topic
        logging.debug(
            f"{__name__}: signalsdk: message received topic:{topic} payload:{payload}"
        )
        try:
            if topic in self.event_call_backs:
                for callback in self.event_call_backs[topic]:
                    logging.debug(
                        f"{__name__}: signalsdk: calling event "
                        f"callback: {callback} and payload: {payload}"
                    )
                    callback(payload)
            else:
                logging.info(f"{__name__}: signalsdk: no callback for topic:{topic}")
        except Exception as e:
            logging.info(
                f"{__name__}: signalsdk: on_message_received callback error: {e}"
            )
            raise e

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"{__name__}: signalsdk::Local MQTT connection established")
        try:
            self.connected_callback()
        except Exception as e:
            logging.error(f"{__name__}: signalsdk::on_connect callback error: {e}")
            raise SignalAppLocalMqttOnConnectionCallBackError from e

    def on_disconnect(self, client, userdata, rc):
        logging.warning(
            f"{__name__}: signalsdk::local mqtt disconnecting reason: {str(rc)}"
        )

    def get_client(self):
        return self.mqtt_client

    def connect(self):
        self.mqtt_client.on_message = self.on_message_received
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_connect = self.on_connect
        try:
            self.mqtt_client.connect(LOCAL_MQTT_URL, LOCAL_MQTT_PORT)
            self.mqtt_client.loop_start()
        except Exception as e:
            logging.error(f"{__name__}: signalsdk::localmqtt connection error: {e}")
            raise SignalAppLocalMqttOConnectionError from e

    def publish(self, topic, payload=""):
        if topic:
            result, _ = self.mqtt_client.publish(topic, payload)
            if result == MQTT_ERR_SUCCESS:
                logging.info(
                    f"{__name__}: signalsdk::localmqtt published topic: {topic}"
                )
            else:
                logging.error(
                    f"{__name__}: signalsdk::localmqtt Failed to publish topic: {topic}"
                )
                raise SignalAppLocalMqttPublishError
        else:
            logging.error(
                f"{__name__}: signalsdk::localmqtt Failed to publish undefined topic"
            )

    def subscribe(self, topic, is_event_topic):
        if topic:
            result, _ = self.mqtt_client.subscribe(topic)
            if result == MQTT_ERR_SUCCESS:
                logging.info(
                    f"{__name__}: signalsdk::localmqtt subscribed topic: {topic}"
                )
            else:
                logging.error(
                    f"{__name__}: signalsdk::localmqtt "
                    f"Failed to subscribe topic: {topic}"
                )
                raise SignalAppLocalMqttSubscribeError
            if is_event_topic:
                self.subscribed_topic = topic
        else:
            logging.error(
                f"{__name__}: signalsdk::localmqtt "
                f"Unable to subscribe to undefined topic"
            )

    def unsubscribe(self):
        if self.subscribed_topic:
            result, _ = self.mqtt_client.unsubscribe(self.subscribed_topic)
            if result == MQTT_ERR_SUCCESS:
                logging.info(
                    f"{__name__}: signalsdk::localmqtt "
                    f"unsubscribed topic: {self.subscribed_topic}"
                )
            else:
                logging.error(
                    f"{__name__}: signalsdk::localmqtt "
                    f"Failed to unsubscribe topic: {self.subscribed_topic}"
                )
                raise SignalAppLocalMqttSubscribeError
            self.subscribed_topic = None

    def get_subscribed_topic(self):
        return self.subscribed_topic
