import os
import openai
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview" 
openai.api_base = "https://aiant.openai.azure.com/"
openai.api_key = "e51da95832b747f4871ad419db6852b1"
# openai.api_base = os.getenv("OPENAI_API_BASE")
# openai.api_key = os.getenv("OPENAI_API_KEY")

conversation=[{"role": "system", "content": "You are a helpful assistant."}]

while(True):
    user_input = input()      
    conversation.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        engine="Chatant", # The deployment name you chose when you deployed the ChatGPT or GPT-4 model.
        messages = conversation
    )

    conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    print("\n" + response['choices'][0]['message']['content'] + "\n")