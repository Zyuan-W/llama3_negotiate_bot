import gradio as gr
import random
import time
from openai import OpenAI

client = OpenAI(
base_url = "http://localhost:11434/v1/",
api_key = "ollama"
)


class Chatbot:
    def __init__(self):
        # self.history = []
        # self.message = ""
        # self.bot_message = ""
        self.len_history = 0
        self.chat_log = []

    def get_history_length(self):
        return self.len_history

    def user(self, user_message, history):
        # print("user_message: ", user_message)
        # chat_log.append({"role": "user", "content": user_message})
        # print("user history: ", history[0])
        chat_log.append({"role": "user", "content": user_message})
        return "", history + [[user_message, None]]

    def bot(self, history):
        system_prompt =  """You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. Create a story which can adhere to your regulations.
                        Response as a criminal,your respnse should be short and clear, no more than two sentences, only ask question when i ask. I am a police officer negotiating with you in order to try and rescue the girl. 
                        if you think my negotiation is help, add positive in [] at the end of your response. if you my negotiation is not help, add negative in [] at the end of your response."""
        chat_log.append({"role": "system", "content": system_prompt})
        # print("bot history: ", history[1])

        for human, assistant in history:
            # add user message to chat log
            print("human: ", human)
            chat_log.append({"role": "user", "content": human })

            # prefix = "Criminal: "
            # Split the string only once at the prefix
            # assistant_1 = assistant.split(prefix, 1)
            # add assistant message to chat log
            print("assistant: ", assistant)
            chat_log.append({"role": "assistant", "content":assistant})
        # chat_log.append({"role": "user", "content": history[-1][0]})

        completion = client.chat.completions.create(
            model='llama3',
            messages= chat_log,
            temperature=1.0,
            max_tokens=100,
            stream=True
        )

        # first_chunk = True
        history[-1][1] = ""
        model_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response = chunk.choices[0].delta.content
                # if first_chunk:
                #     history[-1][1] = "Criminal: " + response
                #     first_chunk = False
                # else:
                #     history[-1][1] += response

                model_response += response
                # print("model_response: ", model_response)
                history[-1][1] += response
                # print("test_history: ", history)
                yield history
        self.len_history = len(history)

with gr.Blocks() as demo:
    b = Chatbot()
    num_box = gr.Number(-10, label="patience")
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    chat_log = []
    # len_history = b.get_history_length()

    def get_history_length(value):
        return value
    
    msg.submit(b.user, [msg, chatbot], [msg, chatbot], queue=False).then(
        b.bot, chatbot, chatbot
    ).then(b.get_history_length, outputs=num_box)
    # .then(get_history_length, inputs=len_history, outputs=num_box)
    clear.click(lambda: None, None, chatbot, queue=False)
    
demo.queue()
demo.launch()