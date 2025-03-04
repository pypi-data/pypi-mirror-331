from pynenc.conf.config_base import ConfigPynencBase
from pynenc.conf.config_redis import ConfigRedis


class ConfigBroker(ConfigPynencBase):
    """Main config of the boker components"""


class ConfigBrokerRedis(ConfigBroker, ConfigRedis):
    """Specific Configuration for the Redis Broker"""
