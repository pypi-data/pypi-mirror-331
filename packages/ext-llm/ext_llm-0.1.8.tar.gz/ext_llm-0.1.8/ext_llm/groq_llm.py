from concurrent.futures import Future

from ext_llm import Llm


class GroqLlm(Llm):

    def __init__(self, config: dict):
        super().__init__()

    def generate_text(self, system_prompt : str, prompt : str, max_tokens: int, temperature: float) -> str | Future :
        return "Hello GroqLlm"