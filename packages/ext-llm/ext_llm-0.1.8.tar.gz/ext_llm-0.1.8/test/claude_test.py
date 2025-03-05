import boto3
import json
import os


class BedrockClaudeWrapper:
    """
        This class uses the Messages API to interact with the Bedrock API.
        https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html

        !!! IMPORTANT !!!
        The request and response body is different for each model and for Claude models it depends also on the API.
        So, the parameters of the body and the way you retrieve the response will be different.

        !!! IMPORTANT !!!
        Ho testato l'API Messages e non ha memoria a meno che non venga gestita a mano. Si può eseguire questa classe per testare e fare le prove.
    """

    def __init__(self, stats_path: str):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id = 'AKIAZI2LGRDTSRTGXA2Z',
            aws_secret_access_key = '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',
            region_name='us-east-1'
        )
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
        self.model_name = "claude-3-5-sonnet"
        return
        # check if the file in the path exists
        if not os.path.exists(stats_path):
            raise FileNotFoundError(f"File not found in the path: {stats_path}")
        else:
            self.stats_path = stats_path
            # load the stats from the file
            with open(stats_path, 'r') as file:
                stats_json = json.load(file)
                self.total_API_calls = stats_json[self.model_name]["total_API_calls"]
                self.total_input_tokens = stats_json[self.model_name]["total_input_tokens"]
                self.total_output_tokens = stats_json[self.model_name]["total_output_tokens"]
                self.total_tokens = stats_json[self.model_name]["total_tokens"]

    def invoke(self, message: str):
        # construct the body from the message
        # list of parameters for this specific model and API: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html
        body = json.dumps({
            "max_tokens": 1024,
            "system": "",
            "messages": [{"role": "user", "content": message}],
            "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.0,  # optional
        })

        # invoke the model and generate the response
        response = self.client.invoke_model(
            body=body,
            # contentType='string',
            # accept='string',
            modelId=self.model_id,
            # trace='ENABLED'|'DISABLED',
            # guardrailIdentifier='string',
            # guardrailVersion='string',
            # performanceConfigLatency='standard'|'optimized'
        )

        # get the HTTP response body
        # list of parameters for this specific model and API: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html
        response_body = json.loads(response.get('body').read())

        # update the stats
        #self.__update_stats(response_body)

        return response_body.get('content')[0].get('text')


# test the wrapper
if __name__ == "__main__":

    # create the wrapper
    bedrock_client = BedrockClaudeWrapper(stats_path="bedrock/stats.json")

    # invoke the model
    output = bedrock_client.invoke(
        "Ciao, sai parlare in italiano? Traduci la seguente frase in inglese: 'Come stai?'. Dopodiché scrivi il primo articolo della costituzione italiana. In seguito traducila in inglese.")

    # print the generated message
    print(output)

    # loop until the user enters "exit" to exit the program and invoke the model with the user input
    while True:
        message = input("Enter a message: ")
        if message == "exit":
            break
        output = bedrock_client.invoke(message)
        print(output)
        print("\n")