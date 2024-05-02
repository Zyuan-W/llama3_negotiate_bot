import gradio as gr
import random
import time
from openai import OpenAI

client = OpenAI(
base_url = "http://localhost:11434/v1/",
api_key = "ollama"
)

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    chat_log = []

    def user(user_message, history):
        print("user_message: ", user_message)
        chat_log.append({"role": "user", "content": user_message})
        print("history: ", history)
        return "", history + [[user_message, None]]

    def bot(history):
        system_prompt =  """You are a criminal, you are holding a little girl"""
        chat_log.append({"role": "system", "content": system_prompt})


        bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.05)
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)
    
demo.queue()
demo.launch()