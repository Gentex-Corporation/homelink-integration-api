from decouple import config

HOST_URL = config("HOMELINK_HOST_URL", default="homelinkcloud.com")
PLATFORM = config("HOMELINK_SMART_HOME_PLATFORM", default="home-assistant")
DISCOVER_URL = config(
    "HOMELINK_DISCOVER_URL",
    default=f"https://{HOST_URL}/services/v2/{PLATFORM}/fulfillment",
)
ENABLE_URL = config(
    "HOMELINK_ENABLE_URL",
    default=f"https://{HOST_URL}/services/v2/{PLATFORM}/fulfillment",
)
STATE_URL = config(
    "HOMELINK_STATE_URL", default=f"https://state.{HOST_URL}/services/v2/{PLATFORM}"
)

COGNITO_POOL_ID = config("COGNITO_POOL_ID", default="us-east-2_sBYr2OD1J")
COGNITO_CLIENT_ID = config("COGNITO_CLIENT_ID", default="701cln3h6bgqfldh61rcf21ko0")
MQTT_ROOT_CA = config("MQTT_ROOT_CA", "AmazonRootCA1.pem")
MQTT_ROOT_CA_REPOSITORY = config(
    "MQTT_ROOT_CA_REPOSITORY", "https://www.amazontrust.com/repository"
)
MQTT_PRIVATE_KEY_SIZE = config("MQTT_PRIVATE_KEY_SIZE", 2048)
MQTT_IOT_ENDPOINT = config("MQTT_IOT_ENDPOINT", "iot.homelinkcloud.com")
MQTT_IOT_PORT = config("MQTT_IOT_PORT", 8883)
