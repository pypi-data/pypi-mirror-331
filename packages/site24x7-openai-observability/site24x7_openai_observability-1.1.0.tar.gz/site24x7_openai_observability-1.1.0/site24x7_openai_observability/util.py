import os
import sys
import logging
from logging.handlers import RotatingFileHandler


LOG_FILE_NAME = "site24x7_openai.log"
LOG_FOLDER = "site24x7_openai_data"
LOG_FOMRAT = '%(asctime)s %(processid)s %(levelname)s %(message)s'
LOG_FILE_MODE = 'a'
DEFAULT_LOG_FILE_SIZE = 5*1024*1024
DEFAULT_LOG_FILE_BACKUP_COUNT = 10
LOG_FILE_ENCODEING = None
LOG_FILE_DELAY = 0
PROCESS_ID = "processid"
LOGGER_NAME = "s247_openai_log"


class OpenAiLogger():
    
    __instance = None
      
    def __new__(cls, log_level= None):
        if cls.__instance is None:
            cls._logs_path = cls.check_and_create_dirs()
            cls._log_file_path = os.path.join(cls._logs_path, LOG_FILE_NAME)
            cls.__log_file_config = [cls._log_file_path, LOG_FILE_MODE, DEFAULT_LOG_FILE_SIZE, DEFAULT_LOG_FILE_BACKUP_COUNT]
            cls.__logger = cls.create_logger()
            cls.log_level = cls.set_log_level(log_level)
        
        return cls.__instance
     
    # @classmethod
    # def set_log_level(cls,log_level):
    #     if log_level in logging._levelToName.keys() or str(log_level) in logging._nameToLevel.keys():
    #         return log_level
    #     return logging.DEBUG
    
    @classmethod
    def check_and_create_dirs(cls):
        cus_log_dir = os.getenv("APM_LOG_DIR", None)
        if not (cus_log_dir and  isinstance(cus_log_dir,str) and len(cus_log_dir)):
            cus_log_dir = os.getcwd()

        logs_path = os.path.join(cus_log_dir, LOG_FOLDER,"logs")
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        
        return logs_path
    
    @classmethod
    def create_logger(cls):
        try:
            logger = logging.getLogger(LOGGER_NAME)
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(LOG_FOMRAT)
            cls.handler = RotatingFileHandler(*cls.__log_file_config)
            cls.handler.setFormatter(formatter)
            logger.addHandler(cls.handler)
            extra_field = {PROCESS_ID : os.getpid()}
            logger = logging.LoggerAdapter(logger, extra_field)
            return logger
        except Exception as e:
            print('site24x7 openai observability log file initialization error', e)
            cls.log_to_sysout()

    @classmethod
    def log_to_sysout(cls):
        global agentlogger
        try:
            cls.handler = logging.StreamHandler(sys.stdout)
            agentlogger = cls.create_logger(cls.handler)
        except Exception as e:
            print('unable to print site24x7 opeani observability logs to sysout', e)
      
     
    @classmethod
    def get_logger(cls, log_config=None):
        if cls.__instance is None:
            cls(log_config)
        return cls.__logger 
    
    def set_log_level(level):
        if level:
            logger = OpenAiLogger.get_logger()
            logger.setLevel(level)

def create_openai_logger(log_level = None):
    global s247_openai_logger
    s247_openai_logger = OpenAiLogger.get_logger(log_level)
    return s247_openai_logger

log_level = os.getenv("APM_LOG_LEVEL",None)
s247_openai_logger = None

create_openai_logger(log_level)

