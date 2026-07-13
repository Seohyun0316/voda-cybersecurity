import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

while True:
    user = input("³ª: ")

    if user.lower() == "exit":
        break

    response = client.responses.create(
        model="gpt-5.5",
        input=user
    )

    print("Ãªº¿:", response.output_text)