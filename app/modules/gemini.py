from http import client
from google import genai
from flask import url_for

import os
from dotenv import load_dotenv

gemini = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

filedir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(filedir)
filepath = os.path.join(app_dir, 'data', 'cv.txt')
print(filepath)
with open(filepath, 'r') as f:
    my_profile = f.read()

def generate_proposal(job_description, my_profile):

    prompt = """
    I am an up work freelancer. I have found a good oppotunity.
    my profile is given below.
    ......

    here is the job that i am proposing for:
    ....
    Create a professional proposal for this job.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)