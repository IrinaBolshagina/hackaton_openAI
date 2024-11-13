from openai import OpenAI
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Assistant:
    def __init__(self, api_key, assistant_name, instructions, letter_prompt, model, tools):
        self.client = OpenAI(api_key=api_key)
        self.letter_prompt = letter_prompt
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

    def new_thread_with_file(self, instruction_for_file):
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
    

    def add_message_to_thread(self, thread, message):
        '''
        add a new message to the thread.
        '''
        self.client.beta.threads.messages.create(
            thread_id=thread.id, 
            role="user",
            content=message
        )
        return thread
    
    def generate_letter(self, job_description, skills):
        '''
            Generate a cover letter based on the job description and the CV file.
        '''
        final_prompt = f'''
            Here is the job offer description:
            {job_description}
            Here is the required expertises:
            {skills}
            {self.letter_prompt}
        '''
        # self.add_message_to_thread(thread, final_prompt)
        thread = self.new_thread_with_file(final_prompt)
        response = self.run_thread(thread)
        return response


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
        response = message_content.value
        # print(response)
        # print("\n!!!!!!!!!!!! Citations!: ".join(citations))
        # print("\n".join(citations))
        return response

    def chat(self):
        '''
        Chat with the assistant for test purposes.
        '''
        thread = self.new_thread_with_file("this is a CV to work with")
        while True:
            instruction_for_file = input("Enter a instruction_for_file or 'q' to exit: ")
            if instruction_for_file == 'q':
                break
            self.add_message_to_thread(thread, instruction_for_file)
            self.run_thread(thread)
