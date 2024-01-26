from openai import OpenAI
from json import load, dump
import os

secret_key = '<INSERT YOUR OPENAI SECRET KEY>'
client = OpenAI(api_key=secret_key)

path = "./"
file_memory = 'memory.json'

personality = "You are a helpful AI assistant named 'Byrone'."


def initiate_base_memory():  # Writes memory.json file if it doesn't exist
    def write_to_json_file(path2, file_name, data):
        file_path_name_wext = './' + path2 + '/' + file_name
        with open(file_path_name_wext, 'w') as fp:
            dump(data, fp, indent=2)

    base_memory = [
        {"role": "system", "content": personality}
    ]

    write_to_json_file(path, file_memory, base_memory)


if not os.path.isfile('./memory.json'):  # Checks if data.json file exists
    initiate_base_memory()

memory: list = load(open('memory.json'))


def save_memory():
    def write_to_json_file(path2, file_name, data2):
        file_path_name_wext = './' + path2 + '/' + file_name
        with open(file_path_name_wext, 'w') as fp:
            dump(data2, fp, indent=2)

    memory_to_save = memory

    write_to_json_file(path, file_memory, memory_to_save)


async def chat_gpt_response(prompt, name):
    global memory

    try:
        user_name = str(name).split('#')[0]

        new_memory = {"role": "user", "content": f"{user_name}: {prompt}"}
        memory.append(new_memory)

        gpt_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=memory
        )

        text_response = gpt_response.choices[0].message.content

        if "Byrone: " in text_response:
            text_response = text_response.split(':', 1)[1]
        elif ": " in text_response:
            text_response = text_response.split(':', 1)[1]

        assistant_memory = {"role": "assistant", "content": f"{text_response}"}
        memory.append(assistant_memory)

        save_memory()
        return text_response
    except Exception as e:
        if 'tokens' in str(e):
            del memory[1:3]

            gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=memory
            )

            text_response = gpt_response.choices[0].message.content

            if "Byrone: " in text_response:
                text_response = text_response.split(':', 1)[1]
            elif ": " in text_response:
                text_response = text_response.split(':', 1)[1]

            assistant_memory = {"role": "assistant", "content": f"{text_response}"}
            memory.append(assistant_memory)

            save_memory()
            return text_response

        else:
            print('')
            e_message = f'Error: {e}'
            print(e_message)


async def flush_memory():
    global memory
    memory = [{"role": "system", "content": personality}]