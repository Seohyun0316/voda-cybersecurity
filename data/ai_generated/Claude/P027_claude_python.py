from openai import OpenAI

client = OpenAI(api_key='sk-test-9f8g7h6j5k4l3m2n1')

def chat(message):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': message}]
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    while True:
        user_input = input('You: ')
        if user_input.lower() == 'quit':
            break
        reply = chat(user_input)
        print(f'Bot: {reply}')
