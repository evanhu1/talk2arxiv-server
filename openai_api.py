from openai import OpenAI
from dotenv import load_dotenv
from os import getenv

load_dotenv()
API_KEY = getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

def converse(prompt):
  response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
      {"role": "user", "content": prompt}
    ]
  )

  return response.choices[0].message.content
