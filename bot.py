import discord
import responses
import threading
import asyncio

channel_name = '<INSERT YOUR BOT CHANNEL NAME>'
# Your Discord bot would only respond to this channel name
flush_keyword = '/flush'
auto_flush = False
cool_down = 3600


async def split_string(string, max_len):
    if not string or max_len <= 0:
        return []

    async def split_string_on_len(substring_param, max_len_param):
        split_list_inner = []
        start, end = 0, max_len_param

        while start < len(substring_param):
            if end >= len(substring_param):
                end = len(substring_param)

            chunk = substring_param[start:end].strip()
            split_list_inner.append(chunk)

            start, end = end, end + max_len_param

        return split_list_inner

    triple_quote = "'''"
    if triple_quote in string:
        split_list = string.split(triple_quote)
        result = []

        for i, substring in enumerate(split_list):
            chunks: list = await split_string_on_len(substring, max_len)
            if i % 2 == 1:  # Text between triple quotes
                chunks[0] = triple_quote + chunks[0]
                chunks[-1] += triple_quote
            result.extend(chunks)
    else:
        result = await split_string_on_len(string, max_len)

    return result


async def send_message(message, user_message, user_name):
    global cool_down
    global auto_flush
    auto_flush = True
    cool_down = 3600
    try:
        async with message.channel.typing():
            response: str = await responses.chat_gpt_response(user_message, user_name)

            # n = 1800
            # new_prompt = [response[i:i+n] for i in range(0, len(response), n)]

            new_prompt = await split_string(response, 1990)

            for i in new_prompt:
                await message.channel.send(i)

    except Exception as e:
        print('')
        e_message = f'Error: {e}'
        print('')
        print(e_message)


async def send_attachments_error(message, is_private):
    global cool_down
    try:
        async with message.channel.typing():
            response = "I'm not capable of seeing images or attachments, sorry."
            await message.author.send(response) if is_private else await message.channel.send(response)
            cool_down = 3600
    except Exception as e:
        e_message = f'Error: {e}'
        await message.channel.send(e_message)


async def flush(message, is_private):
    global cool_down
    global auto_flush
    try:
        response = "<MEMORY WIPED>"
        await responses.flush_memory()
        cool_down = 3600
        auto_flush = False

        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        e_message = f'Error: {e}'
        await message.channel.send(e_message)


def run_discord_bot():
    TOKEN = '<INSERT YOUR DISCORD TOKEN>'

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        threading.Thread(target=between_callback, daemon=True).start()

    @client.event
    async def on_message(message):
        try:

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)
            attachments = message.attachments

            if message.author == client.user and flush_keyword not in user_message:
                return

            print(f"{username} said: '{user_message}' on channel {channel}")

            if channel.lower() == channel_name:  # Filter to send only on channel chat-gpt
                if not attachments:
                    if user_message[0] == '?':
                        prompt = user_message[1:]
                        if flush_keyword in prompt:
                            print('FLUSH KEYWORD DETECTED')
                            await flush(message, is_private=True)
                        else:
                            await send_message(message, prompt, username)
                    else:
                        prompt = user_message
                        if flush_keyword in prompt:
                            print('FLUSH KEYWORD DETECTED')
                            await flush(message, is_private=False)
                        else:
                            await send_message(message, prompt, username)
                else:
                    await send_attachments_error(message, is_private=False)
        except Exception as e:
            print(e)

    def between_callback():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.close()

    client.run(TOKEN)
