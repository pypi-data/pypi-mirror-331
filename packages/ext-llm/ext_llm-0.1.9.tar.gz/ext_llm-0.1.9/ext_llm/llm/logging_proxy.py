from ext_llm import Llm

class LlmLoggingProxy(Llm):
    def __init__(self, llm: Llm):
        super().__init__()
        self.llm = llm

    def generate_text(self, system_prompt: str, prompt: str, max_tokens: int, temperature: float):
        #print(f"generate_text called with system_prompt: {system_prompt}, prompt: {prompt}, max_tokens: {max_tokens}, temperature: {temperature}\n")
        #do logging
        result = self.llm.generate_text(system_prompt, prompt, max_tokens, temperature)
        #do logging
        #print(f"generate_text returned: {result}\n")
        return result

    def get_config(self):
        return self.llm.get_config()