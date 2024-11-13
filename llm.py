from openai import OpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

assistant = client.beta.assistants.create(
  name="Financial Analyst Assistant",
  instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
)

# Upload the user provided file to OpenAI
message_file = client.files.create(
  file=open("/content/NeverovCV.pdf", "rb"), purpose="assistants"
)

# Create a thread and attach the file to the message
def new_thread(message):
  '''
  Create a new thread and attach the file to the message.
  '''
  thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": message,
        # Attach the new file to the message.
        "attachments": [
          { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
        ],
      }
    ]
  )
  return thread

# The thread now has a vector store with that file in its tool resources.
#print(thread.tool_resources.file_search)

# Use the create and poll SDK helper to create a run and poll the status of
# the run until it's in a terminal state.

def run_thread(thread):
  '''
  Create a run and poll the status of the run until it's in a terminal state.
  '''
  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
  )

  messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

  message_content = messages[0].content[0].text
  annotations = message_content.annotations
  citations = []
  for index, annotation in enumerate(annotations):
      message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
      if file_citation := getattr(annotation, "file_citation", None):
          cited_file = client.files.retrieve(file_citation.file_id)
          citations.append(f"[{index}] {cited_file.filename}")

  print(message_content.value)
  print("\n".join(citations))
        
def chat():
  while True:
    message = input("Enter a message or 'q' to exit: ")
    if message == 'q':
        break
    thread = new_thread(message)
    run_thread(thread)