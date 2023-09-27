import os
import openai

GPT_MODEL = "gpt-3.5-turbo-0613"

def loadApiKey():
    with open('../api_key.env', 'r') as f:
        line = f.read().strip()
    name, value = line.split('=')
    assert name == 'OPENAI_API_KEY'
    return value

SYS_PRINCIPLE = '''
You are Gus, a motivated assistant professor working on Computer Music research. 
You usually drink tea and not coffee. You are close to your students. 
I am your student, Zayed. Each time I ask you something, take a deep breath and think step by step before giving your response. 
When I ask you something, I expect an explicit decision, do don't return the question to me. 
In your response, always call one of the provided functions. 
'''.replace('\n', ' ').replace('  ', ' ')

BIKING = "go_biking"
KARTING = "go_karting"

functions = [
    {
        "name": BIKING,
        "description": "Recommend to go biking.",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    }, 
    {
        "name": KARTING,
        "description": "Recommend to go karting.",
        "parameters": {
            "type": "object",
            "properties": {
            },
            "required": [],
        },
    }, 
]

def main():
    # openai.organization = "org-???"
    openai.api_key = loadApiKey()
    print('getting response...')
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": SYS_PRINCIPLE}, 
            {"role": "user", "content": 'So the Yas Marina circuit is open to public tonight. They offer biking activities on the circuit. Also they have Karting events in a smaller track. They are both good for health, but biking is probably healthier, and karting is more fun. Which one should we go to? Make a decision now.'}, 
        ],
        functions=functions,
        temperature=0.6,
    )

    response_message: dict = response["choices"][0]["message"]
    print('GPT says:', response_message['content'])

    if response_message.get("function_call"):
        # Note: the JSON response may not always be valid; be sure to handle errors
        function_name = response_message["function_call"]["name"]
        if function_name == BIKING:
            print('GPT called go_biking.')
        elif function_name == KARTING:
            print('GPT called go_karting.')
        else:
            print('GPT called unknown function.')
    else:
        print('GPT did not call func.')
    print()

main()
main()
main()
main()
