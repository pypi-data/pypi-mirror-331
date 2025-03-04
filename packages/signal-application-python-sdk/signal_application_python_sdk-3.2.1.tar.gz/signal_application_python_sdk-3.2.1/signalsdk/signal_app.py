import os
import logging

from typing import Callable
from signalsdk.local_mqtt import LocalMqtt
from signalsdk.api import get_app_config_api, get_device_config_api
from signalsdk.config import (
    LOCALMQTT_SDK_APPLICATION_COMMAND_NOTIFICATION_TOPIC,
    LOCALMQTT_SDK_TOPIC_PREFIX,
    LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC,
)
from signalsdk.signal_exception import (
    SignalAppLocalMqttEventCallBackError,
    SignalAppConfigEnvError,
    SignalAppOnConfigChangedCallBackError,
)

from .validator import throw_if_parameter_not_found_in

OnConfigUpdated = Callable[[dict], None]
OnCommandReceived = Callable[[str], None]
OnEventReceived = Callable[[str], None]


class SignalApp:
    def __init__(self):
        self.local_mqtt = None
        self.app_id = ""
        self.account_id = ""
        self.on_config_updated_callback = None
        self.on_command_received_callback = None
        self.on_event_received_callback = None
        self.local_pub_topic = None
        self.device_config = None

    def __get_application_config(self):
        app_settings = get_app_config_api(self.app_id)
        current_subtopic = self.local_mqtt.get_subscribed_topic()
        if not app_settings:
            logging.info(
                f"{__name__}: signalsdk: " f"failed to get application config. Ignore"
            )
            return

        logging.debug(f"{__name__}: APP SETTING: {app_settings}")
        if "settingsForSDK" in app_settings:
            sdk_settings = app_settings["settingsForSDK"]
            if "sdkSubTopic" in sdk_settings and sdk_settings["sdkSubTopic"]:
                desired_subtopic = (
                    LOCALMQTT_SDK_TOPIC_PREFIX + sdk_settings["sdkSubTopic"]
                )
                self.__renew_topic_subscription(current_subtopic, desired_subtopic)
            if "sdkPubTopic" in sdk_settings and sdk_settings["sdkPubTopic"]:
                self.local_pub_topic = (
                    LOCALMQTT_SDK_TOPIC_PREFIX + sdk_settings["sdkPubTopic"]
                )
                logging.debug(
                    f"{__name__}: signalsdk:local_pub_topic: {self.local_pub_topic}"
                )

        if "settingsForApp" in app_settings and app_settings["settingsForApp"]:
            # declare app setting dictionary
            settings_for_app_dict = {}
            # convert settingsForApp to json string
            for each_setting in app_settings["settingsForApp"]:
                if each_setting["key"] and each_setting["value"]:
                    settings_for_app_dict[each_setting["key"]] = each_setting["value"]
            logging.debug(f"{__name__}: APP SETTING FOR APP: {settings_for_app_dict}")
            try:
                logging.debug(
                    f"{__name__}: signalsdk:calling configurationChangedCallback"
                )
                self.on_config_updated_callback(settings_for_app_dict)
            except Exception as err:
                logging.info(
                    f"{__name__}: signalsdk:__get_application_config "
                    f"function threw an error: {err}"
                )
                raise SignalAppLocalMqttEventCallBackError from err
        else:
            logging.info(
                f"{__name__}: signalsdk:__get_application_config "
                f"settingsForApp not found in appSettings"
            )

    def __on_command_received_handler(self, command):
        if self.on_command_received_callback:
            try:
                logging.debug(
                    f"{__name__}: signalsdk:command notification received: {command}"
                )
                self.on_command_received_callback(command)
            except Exception as err:
                logging.info(
                    f"{__name__}: signalsdk:__on_command_received_handler "
                    f"function threw an error: {err}"
                )

    def __on_event_received_handler(self, event):
        try:
            if self.on_event_received_callback:
                logging.debug(
                    f"{__name__}: signalsdk:on_event_received_callback "
                    f"received event: {event}"
                )
                self.on_event_received_callback(event)
        except Exception as error:
            logging.debug(
                f"{__name__}: signalsdk: event:__on_event_received_handler"
                f" function threw an error: {error}"
            )
            raise SignalAppLocalMqttEventCallBackError from error

    def __on_config_updated_handler(self, event):
        try:
            logging.debug(
                f"{__name__}: signalsdk:on_config_change_requested"
                f" received event: {event}"
            )
            self.__get_application_config()
        except Exception as err:
            logging.info(
                f"{__name__}: Ignore event in config change callback. Error: {err}"
            )
            raise SignalAppOnConfigChangedCallBackError from err

    def __start_listening_app_config_updates(self):
        # get application from device agent
        self.__get_application_config()
        app_config_update_topic = (
            LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC.replace(
                "${appId}", self.app_id
            )
        )
        self.local_mqtt.set_on_event_received(
            app_config_update_topic, self.__on_config_updated_handler
        )
        self.local_mqtt.subscribe(app_config_update_topic, False)
        app_command_notification_topic = (
            LOCALMQTT_SDK_APPLICATION_COMMAND_NOTIFICATION_TOPIC.replace(
                "${appId}", self.app_id
            )
        )
        self.local_mqtt.set_on_event_received(
            app_command_notification_topic, self.__on_command_received_handler
        )
        self.local_mqtt.subscribe(app_command_notification_topic, False)
        app_local_event_topic = LOCALMQTT_SDK_TOPIC_PREFIX + self.app_id
        app_broadcast_event_topic = LOCALMQTT_SDK_TOPIC_PREFIX + "broadcast"
        app_out_event_topic = LOCALMQTT_SDK_TOPIC_PREFIX + self.app_id + "_out"
        self.local_mqtt.set_on_event_received(
            app_local_event_topic, self.__on_event_received_handler
        )
        self.local_mqtt.set_on_event_received(
            app_broadcast_event_topic, self.__on_event_received_handler
        )
        self.local_mqtt.set_on_event_received(
            app_out_event_topic, self.__on_event_received_handler
        )
        self.local_mqtt.subscribe(app_local_event_topic, False)
        self.local_mqtt.subscribe(app_broadcast_event_topic, False)
        self.local_mqtt.subscribe(app_out_event_topic, False)

    def __renew_topic_subscription(self, current_topic, desired_topic):
        logging.debug(
            f"{__name__}: signalsdk:__renew_topic_subscription "
            f"current_topic: {current_topic} "
            f"desired_topic: {desired_topic}"
        )
        if current_topic and current_topic != desired_topic:
            self.local_mqtt.remove_event_callbacks(current_topic)
            self.local_mqtt.unsubscribe()
        if desired_topic and current_topic != desired_topic:
            self.local_mqtt.subscribe(desired_topic, True)
            self.local_mqtt.set_on_event_received(
                desired_topic, self.__on_event_received_handler
            )

    def initialize(
        self,
        on_config_updated_callback: OnConfigUpdated,
        on_event_received_callback: OnEventReceived = None,
        on_command_received_callback: OnCommandReceived = None,
    ):
        """Signal Application Initialize
        Following objects are created
        localMqtt: it is used to subscribe or publish to local MQTT broker
        served as local event bus
        :param on_configuration_changed_callback: call back function provided by
        signal application for configuration change
        :param on_event_received_callback: call back function provided by signal
        application for events handling
        """
        logging.info(f"{__name__}: signalsdk::Starting signal app initialize.")
        self.on_config_updated_callback = on_config_updated_callback
        self.on_event_received_callback = on_event_received_callback
        self.on_command_received_callback = on_command_received_callback
        self.app_id = os.getenv("APPLICATION_ID")
        throw_if_parameter_not_found_in(
            self.app_id,
            "application id",
            "environment variables",
            SignalAppConfigEnvError,
        )
        # generate local mqtt client id
        local_mqtt_client_id = "edgesignaSdk_" + self.app_id
        self.local_mqtt = LocalMqtt(local_mqtt_client_id)
        self.local_mqtt.set_on_connected(self.__start_listening_app_config_updates)
        self.local_mqtt.connect()

    def get_device_config(self):
        if self.device_config is None:
            self.device_config = get_device_config_api()
        return self.device_config

    def next(self, event, next_app_id=""):
        """Publish the event
        :param event: event received on local event bus
        :             nexe_app_id: next application to receive the event
        :return:
        """
        if next_app_id:
            topic = LOCALMQTT_SDK_TOPIC_PREFIX + next_app_id
            logging.debug(
                f"{__name__}: signalsdk next() publishing to "
                f"applicationId topic: {topic}"
            )
            self.local_mqtt.publish(topic, event)
        else:
            if self.local_pub_topic:
                logging.debug(
                    f"{__name__}: signalsdk next() publishing to sdk topic: "
                    f"{self.local_pub_topic}"
                )
                self.local_mqtt.publish(self.local_pub_topic, event)
            else:
                logging.warning(
                    f"{__name__}: signalsdk next() no topic to publish event: "
                    f"{event}"
                )

    def broadcast(self, event):
        broadcast_topic = LOCALMQTT_SDK_TOPIC_PREFIX + "broadcast"
        logging.debug(
            f"{__name__}: signalsdk next() publishing to "
            f"broadcast topic: {broadcast_topic}"
        )
        self.local_mqtt.publish(broadcast_topic, event)

    def nextNode(self, event):
        """Publish the event to next Node
        Note: nodered edgesignal-connector will subscribe to target topic
        :param event: event received on local event bus
        :return:
        """

        topic = LOCALMQTT_SDK_TOPIC_PREFIX + self.app_id + "_out"
        logging.debug(
            f"{__name__}: signalsdk nextNode() publishing to "
            f"applicationId topic: {topic}"
        )
        self.local_mqtt.publish(topic, event)
