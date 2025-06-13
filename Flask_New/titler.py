import json

with open("./secrets.json", 'r') as file:
    secrets = json.load(file)
    
from openai import OpenAI
client = OpenAI(
  api_key=secrets["openai_key"],  # this is also the default, it can be omitted
)


SYSTEM_PROMPT = "Your task is generating titles for chats between a user and a LLM assistant. Your titles must be at most 5 words long, and should be clear. Do not generate markdown. The chat content is as follows:"

def get_chat_title(messages):
    msg_strings = []
    for msg in messages:
        msg_strings.append(f"{msg['role']}: {msg['content']}")
    msg_content = "\n\n".join(msg_strings)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg_content},  
        ],
    )
    return response.choices[0].message.content
    