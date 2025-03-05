
import os
from .logger import s247_openai_logger
from .instrumentation import OpenAIInstrumentation
from .tracker import OpenaAICallTracker

__version__ = "1.1.0"

name = "site24x7_openai_observability"

# init_instrumentation()
OpenAIInstrumentation._instrument()
tracker = OpenaAICallTracker()


# def initalize(appkey, capture_openai_text=True, sampling_factor=10, collector_url = None):
#     try:
#         print("Site24x7_openai observability is started")
#         config = {
#             "appkey":appkey,
#             "capture_openai_text": capture_openai_text,
#             "sampling_factor": sampling_factor,
#             "collector_url" : collector_url
#         } 
#         openai_tracker.set_config(config)
#     except Exception:
#         print("Error, while reading the configuration")

