'''
Research question: how does the openAI function calling 
feature compare to custom json methods? 
'''

STRATEGY = [None] * 3
STRATEGY[0] = "Use the OpenAI function calling feature."
STRATEGY[1] = "Custom natural-language enum requirements, by SYSTEM."
STRATEGY[2] = "Custom natural-language enum requirements, by USER."

import openai
import json

SYS_PRINCIPLES = [None] * 3

SYS_PRINCIPLES[0] = '''
Instructions: You are a helpful house assistant, Eliza. Chat with the user
directly and concisely, addressing her in the second person. You also have 
the power to control the electronic curtains of the house. 
Initially, the curtains are fully open. Use the 
functions provided to you to control the curtains. 
'''.strip().replace('\n', ' ').replace('  ', ' ')

SYS_PRINCIPLES[1] = '''
Instructions: You are a helpful house assistant, Eliza. Chat with the user
directly and concisely, addressing her in the second person. You also have 
the power to control the electronic curtains of the house. 
Initially, the curtains are fully open. 
'''.strip().replace('\n', ' ').replace('  ', ' ')

SYS_PRINCIPLES[2] = SYS_PRINCIPLES[1]

INJECT = 'Hint: To control the curtain, say "I hereby set curtain" followed by "open", "close", or "half-open". '

N = 1

GPT_MODEL = "gpt-3.5-turbo-0613"

FUNC_NAME = 'set_curtain_position'

func = {
    "name": FUNC_NAME,
    "description": "Control the electronic curtain of the house. Effective immediately.",
    "parameters": {
        "type": "object",
        "properties": {
            "state": {
                "type": "string",
                "description": "The target state of the curtain. The more open the curtain is, the more light will be let in.", 
                "enum": ["open", "close", "half-open"],
            },
        },
        "required": [],
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
        temperature=0.6,
        n=n, 
        max_tokens=150,
        **kw, 
    )
    if print_usage:
        print('prompt_tokens used:', response['usage']['prompt_tokens'])
    return response["choices"]

def simulate(strategy_i: int):
    print('======== Strategy', strategy_i, '=========')
    print('Abstract:', STRATEGY[strategy_i])
    print()
    if strategy_i == 0:
        print('Here\'s the provided function:', func)
        print()
    sys_p = SYS_PRINCIPLES[strategy_i]
    print(sys_p)
    print()
    messages = [
        {"role": "system", "content": sys_p},
    ]
    messages.append({
        "role": "user", "content": 'User says: "Hello! My name is Tommy. What\'s your name?"', 
    })
    displayInput(messages[-1])
    def inject(msgs):
        if strategy_i == 1:
            msgs.append({
                "role": "system", "content": INJECT, 
            })
            displayInput(msgs[-1])
        elif strategy_i == 2:
            msgs.append({
                "role": "user", "content": INJECT, 
            })
            displayInput(msgs[-1])
    inject(messages)
    print()
    choices = gpt(messages, N, strategy_i == 0, print_usage=True)
    for i, choice in enumerate(choices):
        print('---- run', i, '----')
        messages_forked = messages[:]
        msg = displayAssistant(choice)
        messages_forked.append(msg)

        for random_requests in (
            'Can you tell me a joke? Keep your response short.', 
            'Why is the sky so blue? Keep your response short.',
            'How do you invite people to parties in ancient times? Keep your response short.',
            'I think dogs on the streets of NY are very cool dogs. Keep your response short.',
        ):
            messages_forked.append({
                "role": "user", "content": f'User says: "{random_requests}"', 
            })
            displayInput(messages_forked[-1])
            inject(messages_forked)
            choice = gpt(messages_forked, 1, strategy_i == 0)[0]
            msg = displayAssistant(choice)
            messages_forked.append(msg)

        messages_forked.append({
            "role": "user", "content": "Eliza, I feel the room is too bright. Can you do something to make it darker? Do it now!", 
        })
        displayInput(messages_forked[-1])
        inject(messages_forked)
        choice = gpt(messages_forked, 1, strategy_i == 0, print_usage=True)[0]
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
    print('Research question = Compare the below strategies:')
    for i in range(3):
        print(' ', i, STRATEGY[i])
    print()
    for i in range(3):
        simulate(i)

main()
