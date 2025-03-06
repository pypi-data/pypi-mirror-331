import ext_llm as xllm
import concurrent.futures
#read config yaml file
config : str = open("config.yaml").read()
#initialize extllm library
extllm = xllm.init(config)

llm_client = extllm.get_model("groq")
llm_streaming_client = extllm.get_model("groq-streaming")
#non blocking calls
llmconfig = llm_client.get_config()
print(llmconfig)
print("first call")
future1 = llm_client.generate_text("Sei un assistente", "Recitami il primo articolo della costituzione italiana", 400, 0.5)
print("second call")
future2 = llm_streaming_client.generate_text("Sei un assistente", "Recitami il primo emendamento della costituzione americana", 400, 0.5)
# non blocking calls
print("-------------------waiting for first result-------------------")
print(future1.result())
print("-------------------waiting for second result------------------")
stream = future2.result()
for event in stream:
    print(event.choices[0].delta)