import os
import sys
import json
import time
import platform
from importlib import import_module

from ... import s247_openai_logger


def is_apminsight_loaded():
    return True if 'apminsight' in sys.modules else False

def get_message(return_value):
    if return_value :
        if 'text' in return_value['choices'][0]:
            return return_value['choices'][0]['text']
        elif 'message' in return_value['choices'][0]:
            return return_value['choices'][0]['message']['content']
    return ''

def get_prompt(kwargs):
    if 'prompt' in kwargs:
        return kwargs['prompt']
    elif 'messages' in kwargs:
        return kwargs['messages'][-1]['content']
         

def get_system_message(kwargs):
    content = ''
    if 'messages' in kwargs:
        for messages in kwargs['messages']:
            if messages.role == 'system':
                content.appned(messages.content)

    return content

def get_error_details(err):
    if err :
        try:
            import openai 
            if isinstance(err,openai.OpenAIError):
                return {'error':err.message, 'response_code': err.status_code}
        except Exception:
            s247_openai_logger.exception('Failed to fetch openai call error details')
        return {'error':str(err),'response_code':500}
    else:
        return {'error':'-','response_code':200}
    
def get_openai_key(instance):
    try:
        api_key = (
            os.getenv("OPENAI_API_KEY", None) or
            str(instance._client.api_key)
            if hasattr(instance, "_client") and hasattr(instance._client, "api_key")
            else ""
        )
        if api_key is not None and len(api_key) > 7:
            return (api_key[:3]+"..."+api_key[-4:])
    except :
        pass
    return None

def extract_info(api_info, kwargs, result=None, error=None):
    try:  
        from site24x7_openai import openai_tracker
        api_info.update({
            'model': kwargs.get('model',kwargs.get('engine','')),
            'requesttime':int(round(time.time() * 1000))- api_info["starttime"],#tracker.get_start_time(),
            'host':platform.node(),
            'total_token': 0,
            'prompt_token' : 0,
            'response_token' : 0
        })
        
        api_info.update(get_error_details(error))

        if openai_tracker.record_message():
            api_info.update({'prompt': get_prompt(kwargs) })

        if result and hasattr(result, "usage"):
            api_info.update({
                'total_token': getattr(result.usage,"total_tokens", 0),
                'prompt_token': getattr(result.usage,"prompt_tokens", 0),
                'response_token': getattr(result.usage,"completion_tokens", 0),
            })
            if openai_tracker.record_message():
                api_info.update({'message': get_message(result) })

        openai_tracker.increment_call()                 
        openai_tracker.record_request(api_info) 
    except Exception as exc:
        s247_openai_logger.exception('Failed in capture openai data')


def create_apm_tracker(module, method_info):
    if is_apminsight_loaded():
        try:
            import apminsight
            agent = apminsight.get_agent(external=True)
            if agent and agent.context.get_cur_txn():
                tracker_info = apminsight.instrumentation.util.create_tracker_info(module, method_info, apminsight.context.get_cur_tracker())
                return agent.check_and_create_tracker(tracker_info)
        except Exception as exc:
            s247_openai_logger.exception('Error while creating apminsight tracker')
    return None

def close_apm_tracker(tracker, method_info,args,kwargs,res,err):
    if is_apminsight_loaded and tracker :
        import apminsight
        apminsight.instrumentation.wrapper.handle_tracker_end(tracker, method_info, args, kwargs, res, err)
        apminsight.context.set_cur_tracker(tracker.get_parent())

def async_openai_wrapper(original, module, method_info):

    def handle_response(openai_data, kwargs, result, err = None):
        openai_data.update({'requesttime':int(round(time.time() * 1000)) - openai_data.get('starttime')})
        openai_data.update(kwargs)
        if err:
            openai_data.update(get_error_details(err))
            s247_openai_logger.info(json.dumps(openai_data))
            return err
        elif openai_data.get("stream",None):
            return handle_stream_response(openai_data, result)
        elif result:
            openai_data.update(result)
            s247_openai_logger.info(json.dumps(openai_data))
        return result 
    
    async def handle_stream_response( openai_data, stream_response):
        content, choice_role, data_chunck, finish_reason = "", "", None, ""
        try:
            async for chunk in stream_response:
                data_chunck = chunk.copy() if data_chunck == None else data_chunck
                content += chunk.choices[0].delta.get("content", "")
                finish_reason = chunk.choices[0].get('finish_reason')
                if hasattr(chunk.choices[0].delta, "role"):
                    choice_role = chunk.choices[0].delta.role
                yield chunk
        except Exception as ex:
            openai_data.update(get_error_details(ex))
            raise ex
        finally:
            data_chunck['choices'][0]['delta']['role'] = choice_role
            data_chunck['choices'][0]['finish_reason'] = finish_reason
            data_chunck['choices'][0]['delta']['content'] = content
            openai_data.update(data_chunck)
            openai_data.update({'requesttime':int(round(time.time() * 1000)) - openai_data.get('starttime')})
            s247_openai_logger.info(json.dumps(openai_data))

    async def wrapper( *args, **kwargs):
        result = None
        stime = int(round(time.time() * 1000))
        try:
            result = await original(*args, **kwargs)
        except Exception as exc:
            handle_response({'starttime':stime}, kwargs, None, exc)
            return exc
        return handle_response({'starttime':stime}, kwargs, result, None)
    return wrapper


def default_openai_wrapper(original, module, method_info):
    
    def handle_stream_response(openai_data, stream_gen):
        content, choice_role, data_chunk, finish_reason = '', '', None, None
        try:
            for chunk in stream_gen:
                data_chunk = chunk.copy()
                chunk_content = getattr(data_chunk.choices[0].delta, 'content', '')
                content = (content + str(chunk_content)) if isinstance(chunk_content, str) else content
                finish_reason = getattr(data_chunk.choices[0], 'finish_reason', None)
                if hasattr(chunk.choices[0].delta, 'role'):
                    choice_role = chunk.choices[0].delta.role
                yield chunk
        except Exception as ex:
            openai_data.update(get_error_details(ex))
            raise ex
        finally:
            data_chunk['choices'][0]['delta']['role'] = choice_role
            data_chunk['choices'][0]['finish_reason'] = finish_reason
            data_chunk['choices'][0]['delta']['content'] = content
            openai_data.update(data_chunk)
            openai_data.update({'requesttime':int(round(time.time() * 1000)) - openai_data.get('starttime')})
            s247_openai_logger.info(json.dumps(openai_data))

    def handle_response(openai_data, kwargs, result, err = None):
        if err:
            extract_info(openai_data, kwargs,result,err)
            return err
        elif openai_data.get("stream",None):
            return handle_stream_response(openai_data, result)
        elif result:
            openai_data.update(result)
        extract_info(openai_data, kwargs,result,err)
        return result

    def wrapper(*args, **kwargs):
        result = None
        stime = int(round(time.time() * 1000))
        api_key = get_openai_key(args[0])
        try:
            result = original(*args, **kwargs)
        except Exception as exc:
            handle_response({'starttime':stime}, kwargs, None, exc)
            raise exc

        return handle_response({'starttime':stime,'api_key':api_key}, kwargs, result, None)

    wrapper.__name__ = original.__name__
    return wrapper

def check_and_instrument(module_info):
    for module_name in module_info:
        try:
            act_module = import_module(module_name)
            if hasattr(act_module, 'apminsight_instrumented'):
                return 
            for method_info in module_info.get(module_name):
                instrument_method(module_name, act_module, method_info)
                setattr(act_module, 'apminsight_instrumented', True)
        except Exception:
            s247_openai_logger.info(module_name + ' not presnt')

def instrument_method(module_name, act_module, method_info):
    parent_ref = act_module
    if type(method_info) is not dict:
        return
    
    class_name = method_info.get('class', '')
    if class_name and hasattr(act_module, class_name):
        parent_ref = getattr(act_module, class_name)
        module_name = module_name+'.'+class_name
        
    method_name = method_info.get('method', '')
    if method_name and hasattr(parent_ref, method_name):
        original = getattr(parent_ref, method_name)
        wrapper_factory = method_info.get('wrapper') if 'wrapper' in method_info else default_openai_wrapper
        wrapper = wrapper_factory(original, module_name, method_info)
        setattr(parent_ref,  method_name, wrapper)

module_info = {
    # 'openai.api_resources.completion' : [
    #     {
    #         'class' : 'Completion',
    #         'method' : 'create',
    #         'component' : 'OPENAI',
    #         'wrapper' : default_openai_wrapper,
    #     },
    #     {
    #         'class' : 'Completion',
    #         'method': 'acreate',
    #         'component' : 'OPENAI',
    #         'wrapper' : async_openai_wrapper,
    #     }
    # ],
    # 'openai.api_resources.chat_completion' : [
    #     {
    #         'class' : 'ChatCompletion',
    #         'method' : 'create',
    #         'component' : 'OPENAI',
    #         'wrapper' : default_openai_wrapper,
    #     },
    #     {
    #         'class' : 'ChatCompletion',
    #         'method': 'acreate',
    #         'component' : 'OPENAI',
    #         'wrapper' : async_openai_wrapper,
    #     }
    # ],
    'openai.resource.chat.completions' : [
        {
            'class' : 'Completion',
            'method' : 'create',
            'component' : 'OPENAI',
            'wrapper' : default_openai_wrapper,
        },
        # {
        #     'class' : 'Completion',
        #     'method': 'acreate',
        #     'component' : 'OPENAI',
        #     'wrapper' : async_openai_wrapper,
        # }
    ]

}
