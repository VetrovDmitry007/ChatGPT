import openai
import os

# Установите ключ API для доступа к OpenAI API
openai.api_key = "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"
model_engine = "text-davinci-002"

def ask_chatgpt(input_text, chat_history=None):
    prompt_text = f"{input_text}\n"
    if chat_history:
        prompt_text = f"{chat_history}\n{prompt_text}"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt_text,
        temperature=0.7,
        max_tokens=1024,
        n=1,
        stop=None,
    )
    message = response.choices[0].text.strip()
    return message

def start_chat():
    print("Type something to begin...")
    chat_history = None
    while True:
        input_text = input("> ")
        if input_text.lower() in ["quit", "exit", "stop"]:
            break
        response = ask_chatgpt(input_text, chat_history)
        print(response)
        chat_history = f"{chat_history}\n{input_text.strip()}\n{response.strip()}"

if __name__ == "__main__":
    start_chat()

