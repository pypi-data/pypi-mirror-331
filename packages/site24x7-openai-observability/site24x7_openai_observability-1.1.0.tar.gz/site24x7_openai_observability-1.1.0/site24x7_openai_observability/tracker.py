
import os
import time
import json
import requests
import threading
from .util import s247_openai_logger
from .config import DEFAULT_SAMPLING, Config

class OpenaAICallTracker():
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.appkey = Config.get_license_key()
        self.request_queue = []
        self.thread_interval = os.getenv("SITE24X7_POLLING_INTERVAL",30) #seconds
        self.task_sheduled = False
        self.stop_thread = False
        self.flush_data()
        self.schedule_background_task()
        self.openai_call_count = 0
        self.capture_openai_text = os.getenv("SITE24X7_CAPTURE_OPENAI_TEXT","true").lower() in ("true","on","yes","1")
        self.sampling_factor = Config.get_sampling()
     
    def increment_call(self):
        with self._lock:
            self.openai_call_count += 1

    def get_count(self):
        with self._lock:
            return self.openai_call_count
        
    def reset_sampling(self):
        with self._lock:
            self.openai_call_count = 0

    def set_sampling_factor(self,value = DEFAULT_SAMPLING):
        try:
            env_value = os.getenv("SITE24X7_SAMPLING_FACTOR")
            if env_value is not None:
                return int(env_value)
        except (ValueError, TypeError):
            s247_openai_logger.info("Error, apm openai sampling accepts numeric string value as input ")
        return value

    def record_message(self):
        count = self.get_count()
        return True if self.capture_openai_text and count%self.sampling_factor == 0 else False

    def record_request(self, info):
        with OpenaAICallTracker._lock:
            if self.appkey:
                self.request_queue.append(info)
                
    def flush_data(self):
        if 'request_queue' in self.__dict__:
            with self._lock:
                data = self.request_queue
                self.request_queue = []
            return data
        return []
    
    def stop(self):
        self.stop_thread = True
        if self.task_sheduled:
            self._task.join()
    
    def push_data(self):
        while True:
            try:
                self.reset_sampling()
                data = self.flush_data()
                if len(data) and self.appkey is not None:
                    url = Config.get_endpoint_url()
                    response = requests.post(url, data = json.dumps(data))
                    s247_openai_logger.info('response for '+ url+' request :'+ str(response))
            except Exception:
                s247_openai_logger.exception('Error while sending OpenAI data to APM collector')
            finally:
                time.sleep(self.thread_interval)
    
    def schedule_background_task(self):
        try:
            if self.task_sheduled is True:
                return
            
            import threading
            self._task = threading.Thread(target=self.push_data, args=(), kwargs={})
            self._task.setDaemon(True)
            self._task.start()
            self.task_sheduled = True

        except Exception as exc:
            s247_openai_logger.exception('Error while scheduleing task for openai collector')


