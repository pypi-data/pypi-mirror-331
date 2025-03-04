SDK_INIT_ERROR = "signalsdk::Please initialize Signal Application SDK first!"
SDK_APP_ID_NOT_FOUND_ERROR = "signalsdk::Application Id not found on environment!"
SDK_APP_LOCAL_HTTP_SERVER_ERROR = "signalsdk::Local HTTP server is not responding!"
SDK_APP_LOCAL_MQTT_EVENT_CALL_BACK_ERROR = (
    "signalsdk::local mqtt event cb function threw an error"
)
SDK_APP_LOCAL_MQTT_ON_CONNECT_CALL_BACK_ERROR = (
    "signalsdk::local mqtt on connect cb function threw an error"
)
SDK_APP_LOCAL_MQTT_CONNECT_ERROR = "signalsdk::local mqtt connect threw an error"
SDK_APP_LOCAL_MQTT_PUBLISH_ERROR = "signalsdk::local mqtt publish threw an error"
SDK_APP_LOCAL_MQTT_SUBSCRIBE_ERROR = "signalsdk::local mqtt subscribe threw an error"
SDK_APP_ON_CONFIG_CHANGED_CALL_BACK_ERROR = (
    "signalsdk::on config change callback threw an error"
)
SDK_APP_ON_COMMAND_CALL_BACK_ERROR = "signalsdk::on command callback threw an error"


class SignalAppInitError(BaseException):
    def __str__(self):
        return SDK_INIT_ERROR


class SignalAppConfigEnvError(BaseException):
    def __str__(self):
        return SDK_APP_ID_NOT_FOUND_ERROR


class SignalAppLocalHttpServerError(BaseException):
    def __str__(self):
        return SDK_APP_LOCAL_HTTP_SERVER_ERROR


class SignalAppLocalMqttEventCallBackError(BaseException):
    def __str__(self):
        return SDK_APP_LOCAL_MQTT_EVENT_CALL_BACK_ERROR


class SignalAppLocalMqttOnConnectionCallBackError(BaseException):
    def __str__(self):
        return SDK_APP_LOCAL_MQTT_ON_CONNECT_CALL_BACK_ERROR


class SignalAppLocalMqttOConnectionError(BaseException):
    def __str__(self):
        return SDK_APP_LOCAL_MQTT_CONNECT_ERROR


class SignalAppLocalMqttPublishError(BaseException):
    def __str__(self):
        return SDK_APP_LOCAL_MQTT_PUBLISH_ERROR


class SignalAppLocalMqttSubscribeError(BaseException):
    def __str__(self):
        return SDK_APP_LOCAL_MQTT_SUBSCRIBE_ERROR


class SignalAppOnConfigChangedCallBackError(BaseException):
    def __str__(self):
        return SDK_APP_ON_CONFIG_CHANGED_CALL_BACK_ERROR


class SignalAppOnCommandCallBackError(BaseException):
    def __str__(self):
        return SDK_APP_ON_COMMAND_CALL_BACK_ERROR
