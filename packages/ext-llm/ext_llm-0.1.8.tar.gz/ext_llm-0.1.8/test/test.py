import ext_llm as xllm
import concurrent.futures
#read config yaml file
config : str = open("ext_llm_config.yaml").read()
#initialize extllm library
extllm = xllm.init(config)

print(extllm.list_available_models())

llm_client = extllm.get_model("aws")
#non blocking calls
print("first call")
future1 = llm_client.generate_text("Sei un assistente", "Recitami il primo articolo della costituzione italiana", 400, 0.5)
print("second call")
future2 = llm_client.generate_text("Sei un assistente", "Recitami il primo emendamento della costituzione americana", 400, 0.5)
# non blocking calls
print("-------------------waiting for first result-------------------")
print(future1.result())
print("-------------------waiting for second result------------------")
print(future2.result())