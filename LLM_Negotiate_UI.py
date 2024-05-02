from openai import OpenAI
import gradio as gr

client = OpenAI(
base_url = "http://localhost:11434/v1/",
api_key = "ollama"
)

def llm_negotiate(message, history):
    # print("message: ", message)
    # print("len(history): ", len(history))
    len_history = len(history)
    slider_value = len_history
    chat_log = []

    # # welcome message
    # welcome_message = "I m a criminal"
    # if len(history) == 0:
    #     chat_log.append({"role": "assistant", "content": welcome_message})
    
    # system prompt
    system_prompt =  """You are a criminal, you are holding a little girl hostage. Come up with your own story for why you kidnapped the girl and begin with that statement. Create a story which can adhere to your regulations.
                        Response as a criminal,your respnse should be short and clear, no more than two sentences, only ask question when i ask. I am a police officer negotiating with you in order to try and rescue the girl. 
                        if you think my negotiation is help, add positive in [] at the end of your response. if you my negotiation is not help, add negative in [] at the end of your response."""
    chat_log.append({"role": "system", "content": system_prompt})

    
    for human, assistant in history:
        # print("human: ", human)
        chat_log.append({"role": "user", "content": human })
        prefix = "Criminal: "
        # Split the string only once at the prefix
        assistant_1 = assistant.split(prefix, 1)
        chat_log.append({"role": "assistant", "content":assistant_1[1]})
        
    chat_log.append({"role": "user", "content": message})
  
    completion = client.chat.completions.create(
        model='llama3',
        messages= chat_log,
        temperature=1.0,
        max_tokens=1024,
        stream=True
    )

    first_chunk = True
    model_response = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response = chunk.choices[0].delta.content
            # print("response: ", response)
            if first_chunk:
                model_response = "Criminal: " + response
                first_chunk = False
            else:
                model_response = model_response + response
            yield model_response


demo = gr.ChatInterface(
    llm_negotiate,
)

demo.queue().launch()
# gr.ChatInterface(llm_negotiate).launch()


