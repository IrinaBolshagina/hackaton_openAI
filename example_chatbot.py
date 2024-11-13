from os import getenv
from llm import Assistant


if __name__ == "__main__":
    assistant = Assistant(
        api_key=getenv("OPENAI_API_KEY"),
        assistant_name="CV assistant",
        instructions='''
            You are an expert HR. Use job offer description to create a cover letter, edit a CV.
          ''',
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )
    assistant.upload_file("NeverovCV.pdf")
    assistant.chat()