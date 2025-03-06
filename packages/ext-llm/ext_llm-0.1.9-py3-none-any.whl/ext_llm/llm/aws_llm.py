import logging
from botocore.exceptions import ClientError
import boto3
import json

from ext_llm import Llm


def make_system_prompt(system_prompt):
    return [
            {
                "text": system_prompt
            }
        ]


def make_prompt(prompt):
    return [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]


def make_inference_config(max_tokens, temperature, top_p):
    return {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p
        }


class AwsLlm(Llm):

    logger = logging.getLogger('AwsLlm')

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        access_key_id = config['aws_access_key_id']
        secret_access_key = config['aws_secret_access_key']
        region = config['aws_region']
        print(access_key_id)
        print(secret_access_key)
        print(region)
        self.__session = boto3.Session(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        print("load credentials")
        print(self.__session.get_credentials().access_key)
        print(self.__session.get_credentials().secret_key)
        print("load credentials")
        self.__bedrock_client = self.__session.client(service_name='bedrock-runtime')
        self.__model_id = config['model_id']

    def __invoke_model(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):

        system_prompts = make_system_prompt(system_prompt)

        messages = make_prompt(prompt)

        inference_config = make_inference_config(max_tokens, temperature, top_p)


        response = self.__bedrock_client.converse(modelId=self.__model_id, messages=messages, system=system_prompts, inferenceConfig=inference_config)
        return response['output']['message']['content'][0]['text']

    def __invoke_model_stream(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):

        system_prompts = make_system_prompt(system_prompt)

        messages = make_prompt(prompt)

        inference_config = make_inference_config(max_tokens, temperature, top_p)

        stream = self.__bedrock_client.converse_stream(modelId=self.__model_id, messages=messages, system=system_prompts, inferenceConfig=inference_config)
        return stream['stream']

    def generate_text(self, system_prompt: str, prompt: str, max_tokens: int, temperature: float):
        if self.config['invocation_method'] == 'converse':
            return self.__invoke_model(system_prompt, prompt, max_tokens, temperature)
        elif self.config['invocation_method'] == 'converse_stream':
            return self.__invoke_model_stream(system_prompt, prompt, max_tokens, temperature)
        else:
            raise ValueError("Invalid invocation method")

    def get_config(self):
        return self.config