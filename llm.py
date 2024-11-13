from openai import OpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Assistant:
    def __init__(self, api_key, assistant_name, instructions, model, tools):
        self.client = OpenAI(api_key=api_key)
        self.assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            model=model,
            tools=tools,
        )
        self.message_file = None

    def upload_file(self, file_path):
        self.message_file = self.client.files.create(
            file=open(file_path, "rb"), purpose="assistants"
        )

    def new_thread(self, instruction_for_file):
        '''
        Create a new thread with intruction what to do with the file and attach the file to the instruction_for_file.
        '''
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": instruction_for_file,
                    # Attach the new file to the instruction_for_file.
                    "attachments": [
                        {"file_id": self.message_file.id, "tools": [{"type": "file_search"}]}
                    ],
                }
            ]
        )
        return thread

    def run_thread(self, thread):
        '''
        Create a run and poll the status of the run until it's in a terminal state.
        '''
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )

        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))

    def chat(self):
        '''
        Chat with the assistant for test purposes.
        '''
        while True:
            instruction_for_file = input("Enter a instruction_for_file or 'q' to exit: ")
            if instruction_for_file == 'q':
                break
            thread = self.new_thread(instruction_for_file)
            self.run_thread(thread)
