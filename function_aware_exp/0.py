'''
Research question: Is GPT aware of previously called functions?
Research question impromtous: INCEPTION
'''

import openai
import json

N = 4

GPT_MODEL = "gpt-3.5-turbo-0613"

FUNC_NAME = 'set_curtain'

func = {
    "name": FUNC_NAME,
    "description": "Control the electronic curtain of the house. Effective immediately.",
    "parameters": {
        "type": "object",
        "properties": {
            "state": {
                "type": "string",
                "description": "The target color of the curtain.", 
                "enum": ["red", "green", "blue", "invisible"],
            },
        },
        "required": ["state"],
    },
}

def loadApiKey():
    with open('../api_key.env', 'r') as f:
        line = f.read().strip()
    name, value = line.split('=')
    assert name == 'OPENAI_API_KEY'
    return value

def gpt(messages, n, use_func, print_usage = False):
    kw = dict(functions=[func]) if use_func else {}
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0.4,
        n=n, 
        max_tokens=150,
        **kw, 
    )
    if print_usage:
        print('prompt_tokens used:', response['usage']['prompt_tokens'])
    return response["choices"]

def simulate():
    messages = [
        {"role": "user", "content": "Call the provided function now. Arbitrarily decide what state of the curtain you want, but you must call the function now.", },
    ]
    choices = gpt(messages, N, True)
    for i, choice in enumerate(choices):
        print('---- run', i, '----')
        messages_forked = messages[:]
        msg = displayAssistant(choice)
        msg['function_call'] = {
            "name": FUNC_NAME, 
            "arguments": json.dumps({"state": "invisible"}), 
        }
        # print(msg)
        messages_forked.append(msg)
        messages_forked.append({
            "role": "user", "content": "What is the current state of the curtain? Answer in less than four words.", 
        })
        choice = gpt(messages_forked, 1, True)[0]
        msg = displayAssistant(choice)
        messages_forked.append(msg)

        print()
    # print('last dialogue full history:', messages_forked + [msg])

def displayInput(x):
    print(' ', x['role'], 'says:', x['content'])

def displayAssistant(choice):
    # print('  GPT finish reason:', choice["finish_reason"])
    msg: dict = choice["message"]
    print('  GPT says:', msg['content'])
    fc = msg.get("function_call")
    if fc:
        func_name = fc["name"]
        func_args = json.loads(fc['arguments'])
        print('  GPT called:', func_name, func_args)
    else:
        print('  GPT did not call func.')
    return msg

def main():
    openai.api_key = loadApiKey()
    simulate()

main()
