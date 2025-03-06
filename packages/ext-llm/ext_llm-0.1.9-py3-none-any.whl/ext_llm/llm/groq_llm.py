from concurrent.futures import Future
from pyexpat.errors import messages

from ext_llm import Llm
import groq


class GroqLlm(Llm):

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.__groq_client = groq.Client(api_key=config['groq_api_key'])

    def __invoke_model(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):
        chat_completion = self.__groq_client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model = self.config['model_id'],
            max_completion_tokens = max_tokens,
            temperature = temperature,
            top_p = top_p,
            stop=None,
            stream=False
        )
        return chat_completion

    def __invoke_model_stream(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):
        chat_completion = self.__groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model = self.config['model_id'],
            max_completion_tokens = max_tokens,
            temperature = temperature,
            top_p = top_p,
            stop=None,
            stream=True
        )
        return chat_completion

    def generate_text(self, system_prompt : str, prompt : str, max_tokens: int, temperature: float):
        if self.config['invocation_method'] == 'converse':
            return self.__invoke_model(system_prompt, prompt, max_tokens, temperature)
        elif self.config['invocation_method'] == 'converse_stream':
            return self.__invoke_model_stream(system_prompt, prompt, max_tokens, temperature)
        else:
            raise ValueError("Invalid invocation method")


    def get_config(self):
        return self.config