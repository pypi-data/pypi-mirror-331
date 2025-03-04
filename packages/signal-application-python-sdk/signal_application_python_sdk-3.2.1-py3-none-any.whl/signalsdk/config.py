"""
configuration used in signal application
"""
AWS_REGION = "us-east-1"
AWS_CREDENTIAL_PROVIDER_MAX_RETRIES = 100
AWS_CREDENTIAL_PROVIDER_TIMEOUT = 0
LOCALMQTT_SDK_TOPIC_PREFIX = "event/edgesignal-sdk/"
LOCALMQTT_SDK_APPLICATION_CONFIG_UPDATED_TOPIC = (
    "cmd/edgesignal-sdk/${appId}/config-changed"
)
LOCALMQTT_SDK_APPLICATION_COMMAND_NOTIFICATION_TOPIC = (
    "cmd/edgesignal-sdk/${appId}/command"
)
