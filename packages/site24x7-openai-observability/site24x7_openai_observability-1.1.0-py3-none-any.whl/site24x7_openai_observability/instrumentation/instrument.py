from importlib import import_module
from .packages import modules_info
from .patch import wrap_object
from site24x7_openai_observability import s247_openai_logger

class_str = "class"
method_str = "method"
wrapper_str = "wrapper"


initialized = False


def instrument_method(module_name, act_module, method_info):
    try:
        wrap_object(module_name,method_info.get('method'),method_info.get('wrapper'))
    except Exception as ex:
        s247_openai_logger.info("Error while instrumenting", module_name, method_info.get('method'), ex)

def check_and_instrument(module_name, act_module):
    if not module_name:
        return
    if hasattr(act_module, 'apminsight_instrumented'):
        return

    if module_name in modules_info.keys():
        methods_info = modules_info.get(module_name)
        for each_method_info in methods_info:
            instrument_method(module_name, act_module, each_method_info)

        setattr(act_module, 'apminsight_instrumented', True)
        s247_openai_logger.info(" %s instrumented", module_name)


def init_instrumentation():
    global initialized
    if initialized:
        return
    for each_mod in modules_info:
        try:
            act_module = import_module(each_mod)
            check_and_instrument(each_mod, act_module)
        except Exception:
            s247_openai_logger.info("%s is not present", each_mod)

    initialized = True