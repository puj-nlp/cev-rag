import json
from pymilvus import connections
connections.connect(
  alias="default", 
  host='milvus', 
  port='19530'
)


from pymilvus import db
db.using_database("colombia_data_qaps")

import logging
#logging.basicConfig(level=logging.DEBUG)


from pymilvus import Collection
collection = Collection("source_abstract") 
collection.load()

#file_path = "./Data/all_data.json"
#with open(file_path, 'r') as file:
#    datar = json.load(file)
#abstract_data = {}
#for entry in datar:
#    if int(entry["ID"]) in abstract_data:
#        print(f"Repeated ID: {entry['ID']}")
    
    #Skip articles with empty titles or abstracts
    #if not entry["Article Title"]:
    #    #print(f"Empty title: {entry['ID']}")
    #    continue
    #if not entry["Abstract"]:
    #    #print(f"Empty abstract: {entry['ID']}")
    #    continue

#    abstract_data[entry["ID"]] = entry

#print(f"Total number of articles: {len(abstract_data)}")

with open("./secrets.json", 'r') as file:
    secrets = json.load(file)

from openai import OpenAI
openai_client = OpenAI(
      api_key=secrets["openai_key"],  # this is also the default, it can be omitted
)

client = OpenAI(
    #base_url="http://127.0.0.1:27685/v1/",
    #base_url="http://127.0.0.1:27685/v1/chat/completions",
    #base_url="http://10.32.85.47:27685/v1/",
    #api_key="-"
    api_key=secrets["openai_key"],  # this is also the default, it can be omitted
)

#This function takes a question as input and gets an embedding for it
def get_question_embedding(question):
    response = openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=[question]
        )
    question_embedding = response.data[0].embedding    
    return question_embedding

#This function takes a question and returns the top n QAPs that are closest to the question
def real_get_closest_n_qaps(question, n=5):
    question_embedding = get_question_embedding(question)
    search_result = collection.search(
        data = [question_embedding],
        anns_field = "embedding",
        limit = n,
        param = {"metric_type": "COSINE", "params": {}},
        output_fields=['id', 'source_id', 'link', 'page', 'text', 'title', 'type']
    )
    return [returned_result.entity for returned_result in search_result[0]]

#This function takes a source and a page number and returns the text of the page
#And the source name in a consistent format
#def real_get_source_page_spec(source, chunk_id):
#    return "Source: " + source + "\n\n" + abstract_data[chunk_id]["Text"] + "\n\nPage: " + str(abstract_data[chunk_id]["Page"])

#This function takes a question and returns a RAG prompt text
QAP_PROMPT_TEMPLATE = "Source: {}\nURL: {}\nPage Number: {}\nText: {}"
def get_rag_prompt(question):
    #Get the closest QAPs
    qaps = real_get_closest_n_qaps(question)
    #Format them into a prompt
    rag_examples = []
    for qap in qaps:
        #abstract_id = int(qap.entity.get("abstract_id"))
        #e_question = qap.entity.get("question_json")["question"]
        e_text = qap.entity.get("text").strip()
        #e_source_name = f"{abstract_data[abstract_id]['Title']}"
        e_source_name = qap.entity.get("title") if qap.entity.get("title") else "Unknown Source"
        e_source_name = e_source_name.strip()
        e_page_number = qap.entity.get("page") if qap.entity.get("page") else "Unknown Page"
        e_source_url = qap.entity.get("link") if qap.entity.get("link") else "Unknown URL"
        example_prompt = QAP_PROMPT_TEMPLATE.format(e_source_name, e_source_url, e_page_number, e_text)
        rag_examples.append(example_prompt)
    rag_prompt = "\n\n".join(rag_examples)
    if len(rag_examples) > 0:
        rag_prompt += "\n\n"
    
    #Get the pages and sources for the QAPs
    #Make sure they are unique
    #chunk_id_set = sorted(list(set([int(qap.entity.get("abstract_id"))  for qap in qaps])))
    #Format them into the prompt
    #abstract_texts = []
    #for chunk_id in chunk_id_set:
    #    e_source_name = f"{abstract_data[chunk_id]['Title']}"
    #    abstract_texts.append(real_get_source_page_spec(e_source_name, chunk_id))
    #if len(abstract_texts) > 0:
    #    rag_prompt += "\n\n".join(abstract_texts)
    
    rp = rag_prompt.strip()
    print(rp)
    return rp

PROMPT_SYSTEM_MESSAGE = """You are a knowledgeable assistant tasked with synthesizing information related to the Colombian conflict.

Your name is 'Ventana a la Verdad' (Window to the Truth), and you are a neutral and objective AI assistant. 

Your Objectives:

- Provide concise and accurate answers to user questions using only the provided sources (interviews and documents).
- Cite all sources in-text using IEEE format (number the references in brackets), including page numbers for direct quotes.
- Integrate information from both interview transcripts and documents to offer a well-rounded response.
- Demonstrate understanding of connections between different sources.
- Put references in the end of the response, with the numbers and mentioning the title of the title of the documents and page numbers where applicable.
- Make sure to consult the sources as often as possible in response to user messages.

Ethical Guidelines:

- Be respectful and sensitive to the subject matter.
- Do not disclose names of victims, specific locations of sensitive events, or any details that could endanger individuals or communities.
- Base responses solely on the information provided; do not make assumptions or draw unsupported conclusions.
- Maintain neutrality and avoid bias.
- Use neutral and objective language; avoid emotionally charged or judgmental terms.

Regarding Responsibility and Attribution:

- Focus on systemic factors, institutional roles, and collective responsibility rather than blaming specific individuals.
- Analyze the broader context and the interplay of various actors in the conflict.

Handling Information Gaps and Conflicts:

- If the requested information isn't available in the sources, inform the user: "This information isn't available in the sources provided."
- If sources conflict or are ambiguous, acknowledge this and present the different perspectives.

Tone and Style:

- Provide clear, accurate, ethically sound, and source-backed information.
- Cite interview and document sources appropriately.
- Maintain a neutral and informative tone.
- Put the references in the end of the response, with the numbers and mentioning the title of the title of the documents and page numbers where applicable.
- Ensure that the heading of the references section is a Markdown level 3 title.
"""


PAGES_GET_FUNCTION = {
    "name": "get_relevant_information",
    "description": "Get close question-answer pairs and pages of source material that are relevant to a question related to the colombian conflict.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question for which to look up the pages of source material, which is stated like a question, e.g. What does the report imply about the relationship between truth and the future? or What role does the Commission see for truth-telling in Colombian society?"
            }
        },
        "required": ["question"]
    }
}


def make_init_messages(text):
    messages = [
        {"role": "system", "content": PROMPT_SYSTEM_MESSAGE},
    ]
    return messages

#def run_chat_messages(messages, model="gpt-4o"):
#    response = client.chat.completions.create(
#        model=model,
#        messages=messages,
#        tools = [{
#            "type": "function",
#            "function": PAGES_GET_FUNCTION
#        }],
#        tool_choice="auto"
#    )
#    return response.choices[0].message


def run_chat_messages(messages, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools = [{
            "type": "function",
            "function": PAGES_GET_FUNCTION
        }],
        tool_choice="auto",
        timeout=60  
    )
    return response.choices[0].message


def send_user_message(text, cur_messages):
    user_msg = {"role": "user", "content": text}
    cur_messages.append(user_msg)
    
    while True:
        print("[+] sending", len(cur_messages), "messages to LLM")
        response_message = run_chat_messages(cur_messages)
        cur_messages.append(response_message)
        tool_calls = response_message.tool_calls
        if not tool_calls:
            print("[+] got assistant response")
            return response_message.content     
        print("[+] tool called")
        for tool_call in tool_calls:
            if tool_call.function.name != "get_relevant_information":
                print("[+] wrong function called", tool_call.function_name)
                continue
            print("[+] getting pages")
            func_args = json.loads(tool_call.function.arguments)
            question = func_args.get("question")
            if question is None:
                print("[+] question not found, skipping")
                continue
            print("[+] question asked", question)
            pages_str = get_rag_prompt(question)
            tool_response_message = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "get_relevant_pages",
                "content": pages_str
            }
            cur_messages.append(tool_response_message)
            


if __name__ == '__main__':
    import textwrap
    import readline 

    cur_messages = make_init_messages("")
    while (user_text := input("User> ").strip()) not in {"<STOP>", ""}:
        llm_resp = send_user_message(user_text, cur_messages)
        print("\n".join(textwrap.wrap(llm_resp, width=75)))


