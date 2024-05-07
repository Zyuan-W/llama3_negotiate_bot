from typing import Any
import gradio as gr
import re
from openai import OpenAI
from transformers import pipeline

client = OpenAI(
base_url = "http://localhost:11434/v1/",
api_key = "ollama"
)


class Chatbot:
    def __init__(self):
        # self.history = []
        # self.message = ""
        # self.bot_message = ""
        self.patience = -5
        self.len_history = 0
        self.chat_log = []
        # self.patience = 0
        self.mood_values = []
        # self.system_prompt =  """You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. Create a story which can adhere to your regulations.
        #                 Response as a criminal,your respnse should be short and clear, no more than two sentences, only ask question when i ask. I am a police officer negotiating with you in order to try and rescue the girl. 
        #                 if you think my negotiation is help, add positive in [] at the end of your response. if you my negotiation is not help, add negative in [] at the end of your response."""

        self.system_prompt = """You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. Create a story which can adhere to your regulations.
                        I am a police officer negotiating with you in order to try and rescue the girl. Your initial mood is -5, each of your words will display the current mood value in the final brackets. 
                        When my negotiating sentence makes you happy, give mood value as +5. When my negotiating sentence make you unhappy, give mood value as -5. 
                        Give you responses within 2 sentences"""
                        # When your mood value is greater than 20, you will surrender and release the girl and also say it out loud when you release. 
                        # When your mood value becomes less than -20 and you kill the girl and also say it out loud when you kill her."""

    def get_history_length(self):
        return self.len_history
    
    def get_patience(self):
        return self.patience
    
    # def reduce_patience(self):
    #     self.patience -= 1
    
    # def patience(self):

    # def user_greeting(self, user_message, history):
    #     self.chat_log.append({"role": "user", "content": user_message})
    #     return "", history + [[user_message, None]]
    
    def extract_numbers_from_brackets_or_parentheses(self, text):
        # Regular expression to match numbers within square brackets or parentheses
        pattern = r'[([-]?\d+[\])]'
        # Find all matches of the pattern in the text
        matches = re.findall(pattern, text)
        # Extract numbers from matches
        print("Match", matches)
        num = [int(match.lstrip('([').rstrip('])')) for match in matches]
        if 0 in num or len(num) == 0:
            return [0]
        # print(match.lstrip('([').rstrip('])') for match in matches)
        numbers = [num[0] / abs(num[0]) * 5]
        return numbers

    def greeting_message(self, history):

        greeting_log = []
        message = "Let's Start!"

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
        model_response = ""
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
        

    def user(self, user_message, history):
        # print("user_message: ", user_message)
        # chat_log.append({"role": "user", "content": user_message})
        # print("user history: ", history[0])
        self.chat_log.append({"role": "user", "content": user_message})
        return "", history + [[user_message, None]]

    def bot(self, history):
        # system_prompt =  """You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. Create a story which can adhere to your regulations.
        #                 Response as a criminal,your respnse should be short and clear, no more than two sentences, only ask question when i ask. I am a police officer negotiating with you in order to try and rescue the girl. 
        #                 if you think my negotiation is help, add positive in [] at the end of your response. if you my negotiation is not help, add negative in [] at the end of your response."""
        self.chat_log.append({"role": "system", "content": self.system_prompt})
        # print("bot history: ", history[1])
        # welcome_message = "I m a criminal"
        # yield welcome_message

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


        patience = self.get_patience()
        if patience < 20 and patience > -20:

            # first_chunk = True
            history[-1][1] = ""
            model_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response = chunk.choices[0].delta.content
                    # print("response type: ", type(response))
                    model_response += response
                    # print("model_response: ", model_response)
                    history[-1][1] += response
                    # print("test_history: ", history)
                    yield history
            
            temp = self.extract_numbers_from_brackets_or_parentheses(model_response) or [0]
            if temp[-1] == 0:
                self.bot(history[:-1])
            self.mood_values.extend(temp)
            self.patience += self.mood_values[-1]
            print(self.mood_values, self.patience)
        
        else:
            # history[-1][1] = ""
            # response = "I surrendered and released the girl"
            # history[-1][1] += response
            # yield history
            end_message = "Game Over, end the conversion and give your final decision"

            self.chat_log.append({"role": "user", "content": end_message})

            completion = client.chat.completions.create(
                model='llama3',
                messages= self.chat_log,
                temperature=1.0,
                max_tokens=100,
                stream=True
            )

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


with gr.Blocks() as demo:
    b = Chatbot()
    # num_box = gr.Number(-10, label="patience")
    
    chatbot = gr.Chatbot(height=600)
    p_slider = gr.Slider(minimum=-20, maximum=20, value=-5, label="Patience")
    msg = gr.Textbox()
    clear = gr.Button("Clear")
    start = gr.Button("Start")
    # chat_log = []
    # len_history = b.get_history_length()
    user_greeting = "Hi"

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