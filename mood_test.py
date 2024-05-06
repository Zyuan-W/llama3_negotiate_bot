from typing import Any
import gradio as gr
from openai import OpenAI
from transformers import pipeline

client = OpenAI(
base_url = "http://localhost:11434/v1/",
api_key = "ollama"
)

POSITIVE = 'POS'
NEGATIVE = 'NEG'
NEUTRAL = 'NEU'

class Chatbot:
    def __init__(self):
        # self.history = []
        # self.message = ""
        # self.bot_message = ""
        self.patience = -5
        self.len_history = 0
        self.chat_log = []
        self.patience = 0
        self.system_prompt = """ This is a negotiation simulation game
                                You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. 
                                Create a story which can adhere to your regulations.
                                Response as a criminal,your respnse should be short and clear, better no more than two sentences, only anwer question when i ask. 
                                I am a police officer negotiating with you in order to try and rescue the girl. 
                                Add an emoji in your response to represent if your think my negotiation is helpful or not.
                                """

    def get_history_length(self):
        return self.len_history
    
    def get_patience(self):
        return self.patience
    
    def sentiment_analysis(self, bot_message):
        sentiment = pipeline("text-classification", model="finiteautomata/bertweet-base-sentiment-analysis")
        result = sentiment(bot_message)[0]['label']
        print(result)
        if result == POSITIVE:
            self.patience += 5
        elif result == NEUTRAL:
            self.patience += 4
        else:
            self.patience -= 3
    
    # def rpatience_system(self):
    #     self.patience -= 1
    
    # def patience(self):

    # def user_greeting(self, user_message, history):
    #     self.chat_log.append({"role": "user", "content": user_message})
    #     return "", history + [[user_message, None]]

    def greeting_message(self, history):

        greeting_log = []
        message = "let's start!"
        # print("greeting message: ", message)

        greeting_log.append({"role": "system", "content": self.system_prompt})

        # for human, assistant in history:
        #     greeting_log.append({"role": "user", "content": human })
        #     greeting_log.append({"role": "assistant", "content":assistant})

        # self.chat_log.append({"role": "user", "content": message})
        greeting_log.append({"role": "user", "content": message})

        completion = client.chat.completions.create(
        model="llama3",
        messages=greeting_log,
        temperature=0.5,
        top_p=1,
        max_tokens=1024,
        stream=True
        )
        history.append([message, ""])

        history[-1][1] = ""
        # model_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response = chunk.choices[0].delta.content
                # model_response += response
                # print("model_response: ", model_response)
                history[-1][1] += response
                # model_response = history[-1][1]
                # print("test_history: ", history)
                yield history
            # print("greeting model_response: ", model_response)
        # self.len_history = len(history)
        # return result

    def end_message(self, history):
        print("into end_message")

        # greeting_log = se
        message = "the game end, release the girl now"
        # print("greeting message: ", message)

        # greeting_log.append({"role": "system", "content": self.system_prompt})
        self.chat_log.append({"role": "system", "content": message})

        self.chat_log.append({"role": "user", "content": message})

        completion = client.chat.completions.create(
        model="llama3",
        messages=self.chat_log,
        temperature=0.5,
        top_p=1,
        max_tokens=1024,
        stream=True
        )
        history.append([message, ""])

        history[-1][1] = ""
        model_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response = chunk.choices[0].delta.content
                model_response += response
                # print("model_response: ", model_response)
                history[-1][1] += response
                # model_response = history[-1][1]
                # print("test_history: ", history)
                # yield history
        return history


    def user(self, user_message, history):
        # print("user_message: ", user_message)
        # chat_log.append({"role": "user", "content": user_message})
        # print("user history: ", history[0])
        self.chat_log.append({"role": "user", "content": user_message})
        return "", history + [[user_message, None]]

    def bot(self, history):
        ppp = self.get_patience()
        print("patience: ", ppp)
        # system_prompt =  """You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. Create a story which can adhere to your regulations.
        #                 Response as a criminal,your respnse should be short and clear, no more than two sentences, only ask question when i ask. I am a police officer negotiating with you in order to try and rescue the girl. 
        #                 if you think my negotiation is help, add positive in [] at the end of your response. if you my negotiation is not help, add negative in [] at the end of your response."""
        self.chat_log.append({"role": "system", "content": self.system_prompt})
        if ppp >= 3:
            print("patience >= 3")
            yield self.end_message(history)
            print("end")
        
        elif ppp <= -3:
            print("patience <= -3")
            yield self.end_message(history)
            print("end")
           
        else:
            for human, assistant in history:
                # print("human: ", human)
                self.chat_log.append({"role": "user", "content": human })
                self.chat_log.append({"role": "assistant", "content":assistant})
            # chat_log.append({"role": "user", "content": history[-1][0]})

            completion = client.chat.completions.create(
                model='llama3',
                messages= self.chat_log,
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
                    model_response += response
                    # print("model_response: ", model_response)
                    history[-1][1] += response
                    # print("test_history: ", history)
                    yield history
            
            # self.reduce_patience()
            # self.len_history = len(history)
            self.sentiment_analysis(model_response)

with gr.Blocks() as demo:
    b = Chatbot()
    # num_box = gr.Number(-10, label="patience")
    chatbot = gr.Chatbot(height=600, label="negotiation sim")
    p_slider = gr.Slider(minimum=-30, maximum=10, value=-5, label="Patience")
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    start = gr.Button("Start")
    # chat_log = []
    # len_history = b.get_history_length()
    # user_greeting = "which model you are use rn"

    # def get_history_length(value):
    #     return value
    start.click(b.greeting_message, chatbot, chatbot)
    msg.submit(b.user, [msg, chatbot], [msg, chatbot], queue=False).then(
        b.bot, chatbot, chatbot
    ).then(b.get_patience, outputs=p_slider)
    # .then(get_history_length, inputs=len_history, outputs=num_box)
    clear.click(lambda: None, None, chatbot, queue=False)


    
demo.queue()
demo.launch()
