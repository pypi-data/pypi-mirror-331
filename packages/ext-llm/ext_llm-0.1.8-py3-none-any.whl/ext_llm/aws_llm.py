import logging
from botocore.exceptions import ClientError
import boto3
import json

from ext_llm import Llm


class AwsLlm(Llm):

    logger = logging.getLogger('AwsLlm')

    def __init__(self, config: dict):
        aws_access_key_id = config['aws_access_key_id']
        aws_secret_access_key = config['aws_secret_access_key']
        aws_region = config['aws_region']
        super().__init__()
        self._session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        self._bedrock_client = self._session.client(service_name='bedrock-runtime')
        self._model_id = config['model_id']

    def invoke_model(self, system_prompt, prompt, max_tokens: int, temperature: float, top_p=0.9):

        system_prompts = [
            {
                "text": system_prompt
            }
        ]

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]

        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p
        }



        #print(messages)
        response = self._bedrock_client.converse(modelId=self._model_id, messages=messages, system=system_prompts ,inferenceConfig=inference_config)
        #print(response)
        return response['output']['message']['content'][0]['text']

    def generate_text(self, system_prompt: str, prompt: str, max_tokens: int, temperature: float) -> str:
        return self.invoke_model(system_prompt, prompt, max_tokens, temperature)