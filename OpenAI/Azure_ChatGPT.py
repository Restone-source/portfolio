#import os
import openai
openai.api_type = "azure"
openai.api_base = "https://aiant.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = "e51da95832b747f4871ad419db6852b1"
# openai.api_key = os.getenv("e51da95832b747f4871ad419db6852b1")


# defining a function to create the prompt from the system message and the conversation messages
def create_prompt(system_message, messages):
    prompt = system_message
    for message in messages:
        prompt += f"\n<|im_start|>{message['sender']}\n{message['text']}\n<|im_end|>"
    prompt += "\n<|im_start|>assistant\n"
    return prompt

# defining the user input and the system message
user_input = "너가 알고있는 가장 큰 소수"
system_message = f"<|im_start|>system\n{'<your system message>'}\n<|im_end|>"

# creating a list of messages to track the conversation
messages = [{"sender": "user", "text": user_input}]

response = openai.Completion.create(
    engine="Chatant",
    prompt=create_prompt(system_message, messages),
    temperature=0.5,
    max_tokens=250,
    top_p=0.9,
    frequency_penalty=0,
    presence_penalty=0,
    stop=['<|im_end|>']
)

messages.append({"sender": "assistant", "text": response['choices'][0]['text']})
print(response['choices'][0]['text'])