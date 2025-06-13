import json
from pymilvus import connections
connections.connect(
  alias="default", 
  host='milvus', 
  port='19530'
)


from pymilvus import db
db.using_database("abstract_wildlife_data_qaps")


from pymilvus import Collection
collection = Collection("source_abstract") 
collection.load()

file_path = "./Data/abstracts_data.json"
with open(file_path, 'r') as file:
    datar = json.load(file)
abstract_data = {}
for entry in datar:
    if int(entry["ID"]) in abstract_data:
        print(f"Repeated ID: {entry['ID']}")
    
    #Skip articles with empty titles or abstracts
    if not entry["Article Title"]:
        #print(f"Empty title: {entry['ID']}")
        continue
    if not entry["Abstract"]:
        #print(f"Empty abstract: {entry['ID']}")
        continue

    abstract_data[entry["ID"]] = entry

print(f"Total number of articles: {len(abstract_data)}")

with open("./secrets.json", 'r') as file:
    secrets = json.load(file)

from openai import OpenAI
client = OpenAI(
  api_key=secrets["openai_key"],  # this is also the default, it can be omitted
)

#This function takes a question as input and gets an embedding for it
def get_question_embedding(question):
    response = client.embeddings.create(
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
        anns_field = "question_embedding",
        limit = n,
        param = {"metric_type": "COSINE", "params": {}},
        output_fields=['qap_id', 'abstract_id', 'question_json']
    )
    return [returned_result.entity for returned_result in search_result[0]]

#This function takes a source and a page number and returns the text of the page
#And the source name in a consistent format
def real_get_source_page_spec(source):
    return "Source: " + source

#This function takes a question and returns a RAG prompt text
QAP_PROMPT_TEMPLATE = "Question: {}\nAnswer: {}\n Source: {}"
def get_rag_prompt(question):
    #Get the closest QAPs
    qaps = real_get_closest_n_qaps(question)
    #Format them into a prompt
    rag_examples = []
    for qap in qaps:
        abstract_id = int(qap.entity.get("abstract_id"))
        e_question = qap.entity.get("question_json")["question"]
        e_answer = qap.entity.get("question_json")["answer"]
        e_source_name = f"{abstract_data[abstract_id]['Article Title']} in {abstract_data[abstract_id]['Source Title']} ({abstract_data[abstract_id]['Publication Year']}); DOI: {abstract_data[abstract_id]['DOI']}"
        example_prompt = QAP_PROMPT_TEMPLATE.format(e_question, e_answer, e_source_name)
        rag_examples.append(example_prompt)
    rag_prompt = "\n\n".join(rag_examples)
    if len(rag_examples) > 0:
        rag_prompt += "\n\n"
    
    #Get the pages and sources for the QAPs
    #Make sure they are unique
    abstract_id_set = sorted(list(set([int(qap.entity.get("abstract_id"))  for qap in qaps])))
    #Format them into the prompt
    abstract_texts = []
    for abstract_id in abstract_id_set:
        e_source_name = f"{abstract_data[abstract_id]['Article Title']} in {abstract_data[abstract_id]['Source Title']} ({abstract_data[abstract_id]['Publication Year']}); DOI: {abstract_data[abstract_id]['DOI']}"
        abstract_texts.append(real_get_source_page_spec(e_source_name))
    if len(abstract_texts) > 0:
        rag_prompt += "\n\n".join(abstract_texts)
    
    return rag_prompt.strip()

PROMPT_SYSTEM_MESSAGE = """You are a helpful assistant that helps synthesize information about the use of Artificial Intelligence (AI) and Machine Learning (ML) for wildlife studies. You will talk with a user who wants to learn about this topic. You will need to answer the question by relying on the source material as much as possible, as well as give the appropriate citations using the APA citation style. Make sure to cite the sources in your responses. You need to refer to the sources and check with the source material every time you are asked for clarification or a new topic comes up in your conversation with the user. For context, the sources will describe the use of Artificial Intelligence (AI) and Machine Learning (ML) for wildlife studies. Please try to take this context into account and produce answers that are correct and respectful in this regard. You can use markdown formatting. Put the sources at the end."""


PAGES_GET_FUNCTION = {
    "name": "get_relevant_information",
    "description": "Get close question-answer pairs and pages of source material that are relevant to a question related to the use of Artificial Intelligence (AI) and Machine Learning (ML) for wildlife studies",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question for which to look up the pages of source material, which is stated like a question, e.g. What is the challenge in analyzing data collected from animal-borne sensor systems, according to the abstract?"
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

def run_chat_messages(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools = [{
            "type": "function",
            "function": PAGES_GET_FUNCTION
        }],
        tool_choice="auto"
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
            
-

if __name__ == '__main__':
    import textwrap
    import readline 

    cur_messages = make_init_messages("")
    while (user_text := input("User> ").strip()) not in {"<STOP>", ""}:
        llm_resp = send_user_message(user_text, cur_messages)
        print("\n".join(textwrap.wrap(llm_resp, width=75)))


