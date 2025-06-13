from flask import Flask, request, session, render_template

from rag import send_user_message, make_init_messages
from titler import get_chat_title

from flask_session import Session
from cachelib.simple import SimpleCache

import time
import uuid
import markdown

app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
SESSION_TYPE = 'cachelib'
SESSION_SERIALIZATION_FORMAT = 'json'
SESSION_CACHELIB = SimpleCache()
app.config.from_object(__name__)
Session(app)


@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/chats')
def chat_list(hxoob=False):
    chats = session.get('chats', {})
    chat_specs = [{"uuid": uuid, "title": chat["title"], "date": chat["cdate"]} for uuid, chat in chats.items()]
    chat_specs.sort(key=lambda x: x["date"], reverse=True)
    return render_template('chat_list.html', chat_specs=chat_specs, nchats=len(chat_specs), hxoob=hxoob)

@app.route('/chats/<chat_uuid>', methods=['GET', 'DELETE'])
def chat_page(chat_uuid):
    if request.method == "GET":
        return render_template('chat_form.html', chat_uuid=chat_uuid)
    chats = session.get('chats', {})
    chats.pop(chat_uuid, None)
    return chat_list(hxoob=False) + "\n\n" + new_chat_page(hxoob=True)

@app.route('/chats/<chat_uuid>/messages')
def chat_messages(chat_uuid):
    chats = session.get('chats', {})
    chat = chats.get(chat_uuid, {})
    cur_messages = chat.get('messages', make_init_messages(""))
    return render_messages(cur_messages)

@app.route('/chats/new')
def new_chat_page(hxoob=False):
    chat_uuid = str(uuid.uuid4())
    return render_template('chat_form.html', chat_uuid=chat_uuid, hxoob=hxoob)

def msg2dict(msg):
    if isinstance(msg, dict):
        return msg
    return {"role": msg.role, "content": msg.content}

def get_user_facing_messages(messages):
    visible_messages = [msg2dict(message) for message in messages]
    visible_messages = [message for message in visible_messages if message["content"] is not None]
    visible_messages = [
        {"role": message["role"].lower(), "content": str(message["content"])} 
        for message in visible_messages
        if message["role"].lower() in {"user", "assistant"}]
    return visible_messages

def render_messages(messages):
    visible_messages = get_user_facing_messages(messages)
    visible_messages = [
        {"role": message["role"], "content": markdown.markdown(message["content"])} 
        for message in visible_messages
    ]
    return render_template('chat_messages.html', messages=visible_messages, nms=len(visible_messages))

@app.route('/send-message', methods=['POST'])
def message():
    chat_uuid = request.form.get('chatuuid')
    message = request.form.get('chatmessage')
    
    chats = session.get('chats', {})
    chat = chats.get(chat_uuid, {})
    cur_messages = chat.get('messages', make_init_messages(""))
    
    llm_resp = send_user_message(message, cur_messages)
    assert llm_resp is not None
    
    if "title" not in chat:
        chat["title"] = get_chat_title(get_user_facing_messages(cur_messages))
    if "cdate" not in chat:
        chat["cdate"] = time.time()
    chat["messages"] = cur_messages
    chats[chat_uuid] = chat
    session['chats'] = chats
    
    return render_messages(cur_messages) + "\n\n" + chat_list(hxoob=True)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1337, debug=True)