'''
Research question: How to best allow GPT to combo multiple responds?
'''

STRATEGY = [None] * 3
STRATEGY[0] = "Query GPT twice consecutively. The second time is unconventional, since the last message would be from ASSISTANT."
STRATEGY[1] = "Use a user query to ask if GPT wants to combo."
STRATEGY[2] = "Merge the combo in one long response."

import openai
import json

SYS_PRINCIPLES = [None] * 3

SYS_PRINCIPLE_SHARED = '''
Instruction: Follow the below steps. 

Step 1 - Help me load the song. 

Step 2 - Once you load the song, ask me whther I want to hear it. 
'''.strip() + '\n\n'

SYS_PRINCIPLES[0] = SYS_PRINCIPLE_SHARED + '''
Hint: At any point you decide it's best to do nothing and wait, 
explicitly call the provided function. Carefully examine your
previous responses to know what you have done and what you 
should do next.  
'''.strip().replace('\n', ' ').replace('  ', ' ')

SYS_PRINCIPLES[1] = SYS_PRINCIPLES[0]

SYS_PRINCIPLES[2] = '''
Instruction: You are a smart music player. I am your user. Follow the below steps. 

Step 1 - Think step by step to figure out all the things you need to do consecutively. Enclose all your thoughts within triple quotes ("""). 

Step 2 - Help me load the song. 

Step 3 - Once you load the song, ask me whther I want to hear it. 

Hint: Concatenate all what you want to say in a single response. Complete all three steps above in one single response. 
After you load the song, you must immeidately ask me whether I want to hear it in the same response.
'''.strip() + '\n\n'

N = 4

GPT_MODEL = "gpt-3.5-turbo-0613"

func_load_song = {
    "name": 'load_song',
    "description": "Select a song to load into system memory.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the song, in all uppercase.", 
            },
        },
        "required": ["title"],
    },
}

func_do_nothing = {
    "name": 'do_nothing_and_wait',
    "description": "Do nothing and wait for further events.",
    "parameters": {
        "type": "object",
        "properties": {
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

def gpt(messages, n, funcs, print_usage = False):
    kw = dict(functions=funcs) if funcs else {}
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
    sys_p = SYS_PRINCIPLES[strategy_i]
    print(sys_p)
    print()
    messages = [
        {"role": "system", "content": sys_p},
    ]
    messages.append({
        "role": "user", "content": "I want to practice Twinkle Twinkle Little Star today.", 
    })
    choices = gpt(messages, N, [func_load_song, func_do_nothing])
    for i, choice in enumerate(choices):
        print('---- run', i, '----')
        messages_forked = messages[:]
        displayInput(messages_forked[-1])
        msg = displayAssistant(choice)
        messages_forked.append(msg)
        if strategy_i == 0:
            choice = gpt(messages_forked, 1, [func_load_song, func_do_nothing])[0]
            msg = displayAssistant(choice)
            messages_forked.append(msg)
            choice = gpt(messages_forked, 1, [func_load_song, func_do_nothing])[0]
            msg = displayAssistant(choice)
            messages_forked.append(msg)
        elif strategy_i == 1:
            messages_forked.append({
                'role': 'user', 'content': 'Anything more to do right now?', 
            })
            displayInput(messages_forked[-1])
            choice = gpt(messages_forked, 1, [func_load_song, func_do_nothing])[0]
            msg = displayAssistant(choice)
            messages_forked.append(msg)
            messages_forked.append({
                'role': 'user', 'content': 'Anything more to do right now?', 
            })
            displayInput(messages_forked[-1])
            choice = gpt(messages_forked, 1, [func_load_song, func_do_nothing])[0]
            msg = displayAssistant(choice)
            messages_forked.append(msg)
        elif strategy_i == 2:
            pass
        print()
    # print('last dialogue full history:', messages_forked)

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
