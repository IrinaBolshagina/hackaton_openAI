from os import getenv
from llm import Assistant
import json


if __name__ == "__main__":
    assistant = Assistant(
        api_key=getenv("OPENAI_API_KEY"),
        assistant_name="CV assistant",
        instructions='''
            You are an expert HR. Use job offer description to create a cover email, edit a CV.
          ''',
        letter_prompt='''
            Create a cover letter tailored to the job description, highlighting the most relevant qualifications from the CV proveded in pdf file, and format it in JSON as follows:
            {
              "cover_letter": "Your concise cover letter text here, under 60 words."
            }
        ''',
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )
        # letter_prompt='''
        #     Create a cover email tailored to the job description, highlighting the most relevant qualifications from the CV proveded in pdf file.
        #     IMPORTANT: Respond only with finished cover email text, Take name of sender from CV and dont include subject or recipient email.
        #   ''',
    assistant.upload_file("NeverovCV.pdf")
    response = assistant.generate_letter("Software Engineer with deep knowledges", "React, Django, Kubernetes")
    print(type(response))
    print(response)