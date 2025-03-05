import os
import time
import platform
from functools import wraps
from site24x7_openai_observability import s247_openai_logger


def get_message(result):
    if result is not None and hasattr(result, 'choices'):
        choices = getattr(result, 'choices', [])
        if hasattr(choices[0], 'text'):
            return getattr(choices[0], 'text', '')
        elif hasattr(choices[0], 'message'):
            return getattr(choices[0].message, 'content', '')
    return ''

def get_prompt(kwargs):
    if 'prompt' in kwargs:
        return kwargs['prompt']
    elif 'messages' in kwargs:
        messages = kwargs['messages']
        return messages[-1].get('content', '')
    return ''
 

def get_system_message(kwargs):
    content = ''
    if 'messages' in kwargs:
        for messages in kwargs['messages']:
            if messages.role == 'system':
                content += messages.content

    return content

def get_error_details(err):
    if not err:
        return {'error': '-', 'response_code': 200}
    
    try:
        import openai
        if isinstance(err, openai.OpenAIError):
            return {'error': err.message, 'response_code': getattr(err, 'status_code', 500)}
    except Exception:
        s247_openai_logger.exception('Failed to fetch openai call error details')
    
    return {'error': str(err), 'response_code': 500}

    
def get_openai_key(instance):
    try:
        # Check environment variable first
        api_key = os.getenv("OPENAI_API_KEY", None)
        
        # If not found, try to get from instance
        if not api_key and hasattr(instance, "_client") and hasattr(instance._client, "api_key"):
            api_key = str(instance._client.api_key)
        
        # Mask the API key for security
        if api_key and len(api_key) > 7:
            return f"{api_key[:3]}...{api_key[-4:]}"
    except Exception:
        pass
    
    return None


def extract_info(api_info, kwargs, result=None, error=None):
    try:  
        # Basic information
        from site24x7_openai_observability import tracker
        api_info.update({
            'model': kwargs.get('model', kwargs.get('engine', '')),
            'requesttime': int(round(time.time() * 1000)) - api_info["starttime"],
            'host': platform.node(),
            'total_token': 0,
            'prompt_token': 0,
            'response_token': 0
        })
        
        # Error information
        api_info.update(get_error_details(error))

        # Include prompt if needed
        api_info['prompt'] = get_prompt(kwargs)
        api_info['message'] = get_message(result)

        # if tracker.record_message():
        #     api_info['prompt'] = get_prompt(kwargs)

        # Extract token information
        if result and hasattr(result, "usage"):
            usage = result.usage
            api_info.update({
                'total_token': getattr(usage, "total_tokens", 0),
                'prompt_token': getattr(usage, "prompt_tokens", 0),
                'response_token': getattr(usage, "completion_tokens", 0),
            })
            
            # Include response message if needed
            # if tracker.record_message():
            #     api_info['message'] = get_message(result)

        tracker.increment_call()                 
        tracker.record_request(api_info) 
    except Exception as exc:
        s247_openai_logger.exception('Failed to capture openai data: %s', exc)


def default_openai_wrapper(original):
    def handle_stream_response(openai_data, kwargs, stream_gen, exc):
        content, choice_role, data_chunk, finish_reason = '', '', None, None
        try:
            for chunk in stream_gen:
                data_chunk = chunk.copy()

                # Extract chunk content
                if hasattr(data_chunk.choices[0].delta, 'content'):
                    chunk_content = data_chunk.choices[0].delta.content
                    if isinstance(chunk_content, str):
                        content += chunk_content
                
                # Track finish reason
                finish_reason = getattr(data_chunk.choices[0], 'finish_reason', None)
                
                # Track role
                if hasattr(data_chunk.choices[0].delta, 'role'):
                    choice_role = data_chunk.choices[0].delta.role
                
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
            extract_info(openai_data, kwargs, None, exc)

    @wraps(original)
    def wrapper(*args, **kwargs):
        result = None
        stime = int(round(time.time() * 1000))
        api_key = get_openai_key(args[0])
        openai_data = {'starttime': stime, 'api_key': api_key, 'stream': kwargs.get('stream', False)}
        try:
            result = original(*args, **kwargs)
        except Exception as exc:
            extract_info(openai_data, kwargs, None, exc)
            raise exc
        
        if openai_data.get("stream"):
            return handle_stream_response(openai_data, kwargs, result)
        
        extract_info(openai_data, kwargs, result)
        return result
    
    return wrapper

