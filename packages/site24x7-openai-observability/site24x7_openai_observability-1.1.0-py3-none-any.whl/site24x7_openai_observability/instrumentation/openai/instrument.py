
from ..patch import wrap_object
from .wrapper import default_openai_wrapper


class OpenAIInstrumentation:
    component = "OPENAI"
    _wrapped = False

    @classmethod
    def _instrument(cls):
        if cls._wrapped:
            return
        
        try:
            wrap_object(
                'openai.resources.chat.completions',
                'Completions.create',
                default_openai_wrapper
            )
        except Exception as exc:
            print("[Warning] Exception in OPENAI instrumentation: %s ", str(exc))
        finally:
            cls._wrapped = True

    @classmethod
    def _uninstrument(cls):
        pass