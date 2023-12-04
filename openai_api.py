from openai import OpenAI

api_key = "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"
client = OpenAI(api_key=api_key)

def converse(prompt):
  response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
      {"role": "user", "content": prompt}
    ]
  )

  return response.choices[0].message.content
