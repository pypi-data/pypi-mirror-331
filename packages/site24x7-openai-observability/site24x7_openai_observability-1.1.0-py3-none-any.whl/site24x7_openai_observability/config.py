import os
from .util import s247_openai_logger


COLLECTOR_HOSTS ={"us":"plusinsight.site24x7.com",
                 "eu":"plusinsight.site24x7.eu",
                 "cn":"plusinsight.site24x7.cn",
                 "in":"plusinsight.site24x7.in",
                 "au":"plusinsight.site24x7.net.au",
                 "jp":"plusinsight.site24x7.jp",
                 "aa":"plusinsight.localsite24x7.com"
                 }

REQUEST_PATH = "/airh/usage"
DEFAULT_SAMPLING = 10
COLLECTOR_PORT = os.getenv("APM_OPENAI_COLLECTOR_PORT","443")


class Config:
    appkey = os.getenv("S247_LICENSE_KEY", os.getenv("SITE24X7_LICENSE_KEY", None))
    payload_print = os.getenv("SITE24X7_PRINT_PAYLOAD","false").lower in ("true","on","yes","1")
    applogs = os.getenv("APM_ENABLE_APPLOGS",False)
    collector_url = os.getenv("APM_OPENAI_COLLECTOR_URL",None)


    @classmethod
    def get_license_key(cls):
        return cls.appkey
    
    @classmethod
    def get_payload_print(cls):
        return cls.payload_print    
    
    @classmethod
    def _get_host(cls):
        return os.getenv("SITE24X7_APM_HOST", COLLECTOR_HOSTS.get(cls.appkey[:2],COLLECTOR_HOSTS["us"]))
        
    @classmethod    
    def _get_port(cls):
        return os.getenv("SITE24X7_APM_PORT", COLLECTOR_PORT)
        
    @classmethod
    def construct_endpoint_url(cls):
        endpoint_url = os.getenv("APM_OPEANI_COLLECTOR_URL", None)
        if cls.appkey is not None and endpoint_url is None:
            host = cls._get_host()
            port = cls._get_port()
            return  host + ':' + port
        return endpoint_url
    
    @classmethod
    def get_endpoint_url(cls):
        return 'https://' + cls.construct_endpoint_url() + REQUEST_PATH + "?license.key=" + cls.appkey
    
    @classmethod
    def get_sampling(cls):
        try:
            env_value = os.getenv("SITE24X7_SAMPLING_FACTOR",DEFAULT_SAMPLING)
            if env_value is not None:
                return int(env_value)
        except (ValueError, TypeError):
            s247_openai_logger.info("Error, apm openai sampling accepts numeric string value as input ")
        return DEFAULT_SAMPLING
    
